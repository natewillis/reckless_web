"""
Data loader module for parsing and loading horse racing data into database models.
Handles parsing of tracks, races, horses, entries, and related data.
"""

import logging
from typing import Optional, Dict, Any, List, Union
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from horsemen.data_collection.utils import (
    create_fractional_data_from_array_and_object,
    get_point_of_call_object_from_furlongs
)
from horsemen.models import (
    FractionalTimes, Races, Horses, Tracks, Trainers,
    Jockeys, PointsOfCall, Payoffs, Entries
)

# Configure logging
logger = logging.getLogger(__name__)

def parse_track(track_data: Dict[str, Any]) -> Tracks:
    """
    Parse track data and return corresponding Tracks model instance.
    
    Args:
        track_data: Dictionary containing track information
        
    Returns:
        Tracks: The found or created track instance
        
    Raises:
        ValueError: If no matching track found or required fields missing
    """
    logger.debug("Attempting to parse track data: %s", track_data)

    try:
        # Try to find track by code first, then by name
        track = None
        if 'code' in track_data:
            track = Tracks.objects.filter(code=track_data['code']).first()
        if not track and 'track_name' in track_data:
            track = Tracks.objects.filter(name=track_data['track_name']).first()

        if track:
            logger.info("Found track: %s", track)
            return track

        raise ValueError(f'No matching track found for data: {track_data}')

    except Exception as e:
        logger.error("Error parsing track: %s", e)
        raise

def parse_race(race_data: Dict[str, Any]) -> Races:
    """
    Parse race data and return corresponding Races model instance.
    
    Args:
        race_data: Dictionary containing race information
        
    Returns:
        Races: The found or created race instance
        
    Raises:
        ValueError: If required fields are missing
    """
    logger.debug("Attempting to parse race data: %s", race_data)

    try:
        # Validate required fields
        required_fields = ['track', 'race_date', 'race_number']
        for field in required_fields:
            if field not in race_data or not race_data[field]:
                raise ValueError(f"The '{field}' field is required and cannot be empty.")

        # Get track
        track = parse_track(race_data['track'])

        # Get or create race
        race, created = Races.objects.get_or_create(
            track=track,
            race_number=race_data['race_number'],
            race_date=race_data['race_date']
        )

        if created:
            logger.info("Created new race: %s", race)
        else:
            logger.info("Found existing race: %s", race)

        # Update fields if changed
        changed = False
        update_fields = [
            'drf_tracks_import', 'day_evening',
            'drf_entries_import', 'post_time', 'age_restriction',
            'sex_restriction', 'minimum_claiming_price',
            'maximum_claiming_price', 'distance', 'purse',
            'wager_text', 'breed', 'cancelled',
            'race_surface', 'drf_results_import',
            'condition', 'off_time',
            'equibase_entries_import', 'equibase_chart_import',
            'race_type', 'race_name', 'grade',
            'record_horse_name', 'record_time', 'record_date'
        ]
        
        for field in update_fields:
            if field in race_data:
                current_value = getattr(race, field)
                new_value = race_data[field]
                if current_value != new_value:
                    setattr(race, field, new_value)
                    changed = True
                    logger.debug("Updated field '%s' from '%s' to '%s'", field, current_value, new_value)
    
        if changed:
            race.save()
            logger.info("Updated race: %s", race)
    
        # Process children
        if 'children' in race_data:
            for child in race_data['children']:
                if child['object_type'] in OBJECT_MAP:
                    OBJECT_MAP[child['object_type']](child, race)
    
        return race

    except Exception as e:
        logger.error("Error parsing race: %s", e)
        raise

def parse_horse(horse_data: Dict[str, Any], existing_instance: Optional[Horses] = None) -> Horses:
    """
    Parse horse data and return corresponding Horses model instance.
    
    Args:
        horse_data: Dictionary containing horse information
        existing_instance: Optional existing horse instance to update
        
    Returns:
        Horses: The found or created horse instance
        
    Raises:
        ValueError: If required fields are missing
    """
    logger.debug("Attempting to parse horse data: %s", horse_data)
    
    try:
        horse = None
        
        # Check existing instance
        if existing_instance and 'horse_name' in horse_data:
            if horse_data['horse_name'] == existing_instance.horse_name:
                horse = existing_instance
        
        # Try identifiers in order of preference
        if not horse:
            identifiers = [
                ('registration_number', 'registration_number'),
                ('equibase_horse_id', 'equibase_horse_id'),
                ('horse_name', 'horse_name')
            ]
            for field, lookup in identifiers:
                if not horse and field in horse_data:
                    horse = Horses.objects.filter(**{lookup: horse_data[field]}).first()

        # Create new horse if needed
        if not horse:
            if 'horse_name' not in horse_data:
                raise ValueError("The 'horse_name' field is required")

            horse = Horses.objects.create(horse_name=horse_data['horse_name'])
            logger.info("Created new horse: %s", horse)
        else:
            logger.info("Found existing horse: %s", horse)

        # Update attributes
        changed = False
        for key, value in horse_data.items():
            if key not in ['object_type', 'children'] and hasattr(horse, key):
                if getattr(horse, key) != value:
                    setattr(horse, key, value)
                    changed = True
                    logger.debug("Updated '%s' for horse: %s", key, horse)
        
        if changed:
            horse.save()
            
        return horse

    except Exception as e:
        logger.error("Error parsing horse: %s", e)
        raise

def parse_trainer(trainer_data: Dict[str, Any], existing_instance: Optional[Trainers] = None) -> Trainers:
    """
    Parse trainer data and return corresponding Trainers model instance.
    
    Args:
        trainer_data: Dictionary containing trainer information
        existing_instance: Optional existing trainer instance to update
        
    Returns:
        Trainers: The found or created trainer instance
        
    Raises:
        ValueError: If required fields are missing
    """
    logger.debug("Attempting to parse trainer data: %s", trainer_data)

    try:
        trainer = None
        
        # Check existing instance
        if existing_instance and all(field in trainer_data for field in ['first_name', 'last_name']):
            if (trainer_data['first_name'] == existing_instance.first_name and 
                trainer_data['last_name'] == existing_instance.last_name):
                trainer = existing_instance
        
        # Try identifiers in order of preference
        if not trainer:
            identifiers = [
                ('drf_trainer_id', 'drf_trainer_id'),
                ('equibase_trainer_id', 'equibase_trainer_id'),
                (['first_name', 'last_name'], lambda d: {'first_name': d['first_name'], 'last_name': d['last_name']})
            ]
            for fields, lookup in identifiers:
                if not trainer:
                    if isinstance(fields, list):
                        if all(f in trainer_data for f in fields):
                            trainer = Trainers.objects.filter(**lookup(trainer_data)).first()
                    elif fields in trainer_data:
                        trainer = Trainers.objects.filter(**{fields: trainer_data[fields]}).first()

        # Create new trainer if needed
        if not trainer:
            required_fields = ['first_name', 'last_name']
            if not all(field in trainer_data for field in required_fields):
                raise ValueError("first_name and last_name are required")

            trainer = Trainers.objects.create(
                first_name=trainer_data['first_name'],
                last_name=trainer_data['last_name'],
                alias=trainer_data.get('alias', '')
            )
            logger.info("Created new trainer: %s", trainer)
        else:
            logger.info("Found existing trainer: %s", trainer)

        # Update attributes
        changed = False
        for key, value in trainer_data.items():
            if key not in ['object_type', 'children'] and hasattr(trainer, key):
                if getattr(trainer, key) != value:
                    setattr(trainer, key, value)
                    changed = True
                    logger.debug("Updated '%s' for trainer: %s", key, trainer)
        
        if changed:
            trainer.save()
            
        return trainer

    except Exception as e:
        logger.error("Error parsing trainer: %s", e)
        raise

def parse_jockey(jockey_data: Dict[str, Any], existing_instance: Optional[Jockeys] = None) -> Jockeys:
    """
    Parse jockey data and return corresponding Jockeys model instance.
    
    Args:
        jockey_data: Dictionary containing jockey information
        existing_instance: Optional existing jockey instance to update
        
    Returns:
        Jockeys: The found or created jockey instance
        
    Raises:
        ValueError: If required fields are missing
    """
    logger.debug("Attempting to parse jockey data: %s", jockey_data)

    try:
        jockey = None
        
        # Check existing instance
        if existing_instance and all(field in jockey_data for field in ['first_name', 'last_name']):
            if (jockey_data['first_name'] == existing_instance.first_name and 
                jockey_data['last_name'] == existing_instance.last_name):
                jockey = existing_instance
        
        # Try identifiers in order of preference
        if not jockey:
            identifiers = [
                ('drf_jockey_id', 'drf_jockey_id'),
                ('equibase_jockey_id', 'equibase_jockey_id'),
                (['first_name', 'last_name'], lambda d: {'first_name': d['first_name'], 'last_name': d['last_name']})
            ]
            for fields, lookup in identifiers:
                if not jockey:
                    if isinstance(fields, list):
                        if all(f in jockey_data for f in fields):
                            jockey = Jockeys.objects.filter(**lookup(jockey_data)).first()
                    elif fields in jockey_data:
                        jockey = Jockeys.objects.filter(**{fields: jockey_data[fields]}).first()

        # Create new jockey if needed
        if not jockey:
            required_fields = ['first_name', 'last_name']
            if not all(field in jockey_data for field in required_fields):
                raise ValueError("first_name and last_name are required")

            jockey = Jockeys.objects.create(
                first_name=jockey_data['first_name'],
                last_name=jockey_data['last_name']
            )
            logger.info("Created new jockey: %s", jockey)
        else:
            logger.info("Found existing jockey: %s", jockey)

        # Update attributes
        changed = False
        for key, value in jockey_data.items():
            if key not in ['object_type', 'children'] and hasattr(jockey, key):
                if getattr(jockey, key) != value:
                    setattr(jockey, key, value)
                    changed = True
                    logger.debug("Updated '%s' for jockey: %s", key, jockey)
        
        if changed:
            jockey.save()
            
        return jockey

    except Exception as e:
        logger.error("Error parsing jockey: %s", e)
        raise

def parse_entry(entry_data: Dict[str, Any], parent_object: Optional[Races] = None) -> Entries:
    """
    Parse entry data and return corresponding Entries model instance.
    
    Args:
        entry_data: Dictionary containing entry information
        parent_object: Optional parent race instance
        
    Returns:
        Entries: The found or created entry instance
        
    Raises:
        ValueError: If required fields are missing or entry cannot be created
    """
    logger.debug("Attempting to parse entry data: %s", entry_data)
    
    try:
        # Get or validate parent race
        race = parent_object or parse_race(entry_data['race'])
        if not race:
            raise ValueError(f"Parent race is required: {entry_data}")

        # Find existing entry
        entry = None
        if 'program_number' in entry_data:
            entry = Entries.objects.filter(
                race=race,
                program_number=entry_data['program_number']
            ).first()
            
            # Validate horse hasn't changed
            if entry and 'horse' in entry_data:
                if 'horse_name' in entry_data['horse']:
                    if entry.horse.horse_name != entry_data['horse']['horse_name']:
                        logger.warning(
                            "Horse changed for program number %s from %s to %s",
                            entry.program_number,
                            entry.horse.horse_name,
                            entry_data['horse']['horse_name']
                        )
                        entry.delete()
                        entry = None

        # Create new entry if needed
        if not entry and 'horse' in entry_data:
            horse = parse_horse(entry_data['horse'])
            if horse:
                entry, created = Entries.objects.get_or_create(
                    race=race,
                    horse=horse
                )
                if created:
                    logger.info("Created new entry: %s", entry)
            else:
                raise ValueError("Could not parse horse data")

        if not entry:
            raise ValueError("No matching entry found or could be created")

        # Update entry attributes
        changed = False
        for key, value in entry_data.items():
            if isinstance(value, dict):
                # Handle nested objects that need parsing
                if key not in ['race', 'horse'] and value['object_type'] in OBJECT_MAP:
                    old_id = getattr(entry, key).id if getattr(entry, key) else None
                    parsed_value = OBJECT_MAP[value['object_type']](
                        value,
                        existing_instance=getattr(entry, key)
                    )
                    if old_id != parsed_value.id:
                        setattr(entry, key, parsed_value)
                        changed = True
                        logger.debug("Updated nested object '%s' for entry: %s", key, entry)
            elif hasattr(entry, key) and getattr(entry, key) != value:
                setattr(entry, key, value)
                changed = True
                logger.debug("Updated field '%s' from '%s' to '%s'", key, getattr(entry, key), value)

        if changed:
            entry.save()
            
        # Process children
        if 'children' in entry_data:
            for child in entry_data['children']:
                if child['object_type'] in OBJECT_MAP:
                    OBJECT_MAP[child['object_type']](child, entry)

        return entry

    except Exception as e:
        logger.error("Error parsing entry: %s", e)
        raise

def parse_payoff(payoff_data: Dict[str, Any], parent_object: Optional[Races] = None) -> Payoffs:
    """
    Parse payoff data and return corresponding Payoffs model instance.
    
    Args:
        payoff_data: Dictionary containing payoff information
        parent_object: Optional parent race instance
        
    Returns:
        Payoffs: The found or created payoff instance
        
    Raises:
        ValueError: If required fields are missing
    """
    logger.debug("Attempting to parse payoff data: %s", payoff_data)

    try:
        # Get or validate parent race
        race = parent_object or parse_race(payoff_data['race'])
        if not race:
            raise ValueError(f"Parent race is required: {payoff_data}")

        # Validate required fields
        required_fields = ['wager_type', 'winning_numbers']
        if not all(field in payoff_data for field in required_fields):
            raise ValueError("wager_type and winning_numbers are required")

        # Get or create payoff
        payoff, created = Payoffs.objects.get_or_create(
            race=race,
            wager_type=payoff_data['wager_type'],
            winning_numbers=payoff_data['winning_numbers']
        )

        if created:
            logger.info("Created new payoff: %s", payoff)
        else:
            logger.info("Found existing payoff: %s", payoff)

        # Update attributes
        changed = False
        for key, value in payoff_data.items():
            if key not in ['object_type', 'children'] and hasattr(payoff, key):
                if getattr(payoff, key) != value:
                    setattr(payoff, key, value)
                    changed = True
                    logger.debug("Updated '%s' for payoff: %s", key, payoff)
        
        if changed:
            payoff.save()
            
        return payoff

    except Exception as e:
        logger.error("Error parsing payoff: %s", e)
        raise

def parse_fractional_time(
    fractional_time_data: Dict[str, Any],
    parent_object: Optional[Races] = None
) -> Union[FractionalTimes, List[FractionalTimes]]:
    """
    Parse fractional time data and return corresponding FractionalTimes model instance(s).
    
    Args:
        fractional_time_data: Dictionary containing fractional time information
        parent_object: Optional parent race instance
        
    Returns:
        Union[FractionalTimes, List[FractionalTimes]]: The found or created fractional time instance(s)
        
    Raises:
        ValueError: If required fields are missing
    """
    logger.debug("Attempting to parse fractional time data: %s", fractional_time_data)

    try:
        # Get or validate parent race
        race = parent_object or parse_race(fractional_time_data['race'])
        if not race:
            raise ValueError(f"Parent race is required: {fractional_time_data}")

        # Handle array of fractional times
        if 'fractional_time_array' in fractional_time_data:
            fractional_times = []
            for time_object in create_fractional_data_from_array_and_object(
                fractional_time_data['fractional_time_array'],
                race.distance
            ):
                fractional_times.append(
                    parse_fractional_time(time_object, parent_object=race)
                )
            return fractional_times

        # Validate required fields
        if 'point' not in fractional_time_data:
            raise ValueError("point is required")

        # Get or create fractional time
        fractional_time, created = FractionalTimes.objects.get_or_create(
            race=race,
            point=fractional_time_data['point']
        )

        if created:
            logger.info("Created new fractional time: %s", fractional_time)
        else:
            logger.info("Found existing fractional time: %s", fractional_time)

        # Update attributes
        changed = False
        for key, value in fractional_time_data.items():
            if key not in ['object_type', 'children'] and hasattr(fractional_time, key):
                if getattr(fractional_time, key) != value:
                    setattr(fractional_time, key, value)
                    changed = True
                    logger.debug("Updated '%s' for fractional time: %s", key, fractional_time)
        
        if changed:
            fractional_time.save()
            
        return fractional_time

    except Exception as e:
        logger.error("Error parsing fractional time: %s", e)
        raise

def parse_point_of_call(point_of_call_data: Dict[str, Any], parent_object: Optional[Entries] = None) -> PointsOfCall:
    """
    Parse point of call data and return corresponding PointsOfCall model instance.
    
    Args:
        point_of_call_data: Dictionary containing point of call information
        parent_object: Optional parent entry instance
        
    Returns:
        PointsOfCall: The found or created point of call instance
        
    Raises:
        ValueError: If required fields are missing
    """
    logger.debug("Attempting to parse point of call data: %s", point_of_call_data)

    try:
        # Get or validate parent entry
        entry = parent_object or parse_entry(point_of_call_data['entry'])
        if not entry:
            raise ValueError(f"Parent entry is required: {point_of_call_data}")

        # Get point of call object based on distance if available
        if 'distance' in point_of_call_data:
            point_of_call_object = get_point_of_call_object_from_furlongs(
                point_of_call_data['distance'],
                quarter_horse_flag=entry.race.breed == 'QH'
            )
            if point_of_call_object:
                point_of_call_data['point'] = point_of_call_object['point']
                point_of_call_data['text'] = point_of_call_object['text']

        # Validate required fields
        if 'point' not in point_of_call_data:
            raise ValueError("point is required")

        # Get or create point of call
        point_of_call, created = PointsOfCall.objects.get_or_create(
            entry=entry,
            point=point_of_call_data['point']
        )

        if created:
            logger.info("Created new point of call: %s", point_of_call)
        else:
            logger.info("Found existing point of call: %s", point_of_call)

        # Update attributes
        changed = False
        for key, value in point_of_call_data.items():
            if key not in ['object_type', 'children'] and hasattr(point_of_call, key):
                if getattr(point_of_call, key) != value:
                    setattr(point_of_call, key, value)
                    changed = True
                    logger.debug("Updated '%s' for point of call: %s", key, point_of_call)
        
        if changed:
            point_of_call.save()
            
        return point_of_call

    except Exception as e:
        logger.error("Error parsing point of call: %s", e)
        raise

def process_parsed_objects(parsed_objects: List[Dict[str, Any]]) -> None:
    """
    Process a list of parsed objects using the appropriate parser from OBJECT_MAP.
    
    Args:
        parsed_objects: List of dictionaries containing object data to parse
        
    Raises:
        ValueError: If object type is not supported
    """
    logger.info("Processing parsed objects")

    try:
        for parsed_object in parsed_objects:
            if 'object_type' not in parsed_object:
                raise ValueError(f"Missing object_type in parsed object: {parsed_object}")
                
            if parsed_object['object_type'] in OBJECT_MAP:
                OBJECT_MAP[parsed_object['object_type']](parsed_object)
            else:
                raise ValueError(f"Unsupported object type: {parsed_object['object_type']}")

    except Exception as e:
        logger.error("Error processing parsed objects: %s", e)
        raise

# Map of object types to their parser functions
OBJECT_MAP = {
    'race': parse_race,
    'track': parse_track,
    'horse': parse_horse,
    'entry': parse_entry,
    'point_of_call': parse_point_of_call,
    'fractional_time': parse_fractional_time,
    'payoff': parse_payoff,
    'trainer': parse_trainer,
    'jockey': parse_jockey
}
