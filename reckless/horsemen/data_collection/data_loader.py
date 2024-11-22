import logging
from django.core.exceptions import ObjectDoesNotExist
from horsemen.data_collection.utils import create_fractional_data_from_array_and_object
from horsemen.models import FractionalTimes, Races, Horses, Tracks, Trainers, Jockeys, PointsOfCall, Payoffs, Entries

# Configure logging
logger = logging.getLogger(__name__)

def parse_track(track_data):
    logger.debug("Attempting to parse track data: %s", track_data)

    track = None

    try:
        if 'code' in track_data:
            track = Tracks.objects.filter(code=track_data['code']).first()
        if not track and 'track_name' in track_data:
            track = Tracks.objects.filter(name=track_data['track_name']).first()

        if track:
            logger.info("Found track: %s", track)
            return track

    except Exception as e:
        logger.error("Error occurred while parsing track: %s", e)

    logger.warning("No matching track found for data: %s", track_data)
    raise ValueError(f'There was no matching track. {track_data}')


def parse_race(race_data):
    logger.debug("Attempting to parse race data: %s", race_data)

    try:
        # Validate input data
        if 'track' not in race_data or not race_data['track']:
            raise ValueError("The 'track' field is required and cannot be empty.")

        if 'race_date' not in race_data or not race_data['race_date']:
            raise ValueError("The 'race_date' field is required and cannot be empty.")

        if 'race_number' not in race_data or race_data['race_number'] is None:
            raise ValueError("The 'race_number' field is required and cannot be None.")

        # Get track
        track = parse_track(race_data['track'])

        race, created = Races.objects.get_or_create(
            track=track,
            race_number=race_data['race_number'],
            race_date=race_data['race_date']
        )

        if created:
            logger.info("Created a new race: %s", race)
        else:
            logger.info("Found existing race: %s", race)

        # Update fields if changed
        changed = False
    
        # Fields to update
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
        logger.error("Error occurred while parsing race: %s", e)
        raise

def parse_horse(horse_data, existing_instance=None):
    logger.debug("Attempting to parse horse data: %s", horse_data)
    
    # init horse
    horse = None
    
    try:
        
        # deal with existing instance
        if existing_instance:
            if 'horse_name' in horse_data:
                if horse_data['horse_name'] == existing_instance.horse_name:
                    horse = existing_instance
        
        # Try identifiers first
        if not horse and 'registration_number' in horse_data:
            horse = Horses.objects.filter(registration_number=horse_data['registration_number']).first()

        if not horse and 'equibase_horse_id' in horse_data:
            horse = Horses.objects.filter(equibase_horse_id=horse_data['equibase_horse_id']).first()

        if not horse and 'horse_name' in horse_data:
            horse = Horses.objects.filter(horse_name=horse_data['horse_name']).first()

        # Create horse if needed
        if not horse:
            if 'horse_name' not in horse_data:
                raise ValueError("The 'horse_name' field is required and cannot be None.")

            horse = Horses.objects.create(horse_name=horse_data['horse_name'])
            logger.info("Created a new horse: %s", horse)
        else:
            logger.info("Found existing horse: %s", horse)

        # Update attributes if they are present in horse_data
        changed = False
        for key, value in horse_data.items():
            if key != 'object_type' and key != 'children' and hasattr(horse, key):
                if getattr(horse, key) != value:  # Check if the value has changed
                    changed = True
                    setattr(horse, key, value)  # Update the horse instance
                    logger.info("Updated '%s' for horse: %s", key, horse)
        if changed:
            horse.save()  # Save changes if any attributes were updated
        return horse

    except Exception as e:
        logger.error("Error occurred while parsing horse: %s", e)
        raise

def parse_trainer(trainer_data, existing_instance = None):
    logger.debug("Attempting to parse trainer data: %s", trainer_data)

    trainer = None
    try:
        
        # deal with existing instance
        if existing_instance:
            if 'first_name' in trainer_data and 'last_name' in trainer_data:
                if trainer_data['first_name'] == existing_instance.first_name and trainer_data['last_name'] == existing_instance.last_name:
                    trainer = existing_instance
        
        # Try identifiers first
        if not trainer and 'drf_trainer_id' in trainer_data:
            trainer = Trainers.objects.filter(drf_trainer_id=trainer_data['drf_trainer_id']).first()

        if not trainer and 'equibase_trainer_id' in trainer_data:
            trainer = Trainers.objects.filter(equibase_trainer_id=trainer_data['equibase_trainer_id']).first()

        if not trainer and 'first_name' in trainer_data and 'last_name' in trainer_data:
            trainer = Trainers.objects.filter(
                first_name=trainer_data['first_name'],
                last_name=trainer_data['last_name']
            ).first()

        # Create trainer if needed
        if not trainer:
            if 'first_name' not in trainer_data or 'last_name' not in trainer_data:
                raise ValueError("The 'first_name' and 'last_name' fields are required and cannot be None.")

            trainer = Trainers.objects.create(
                first_name=trainer_data['first_name'],
                last_name=trainer_data['last_name'],
                alias=trainer_data.get('alias', '')  # Handle optional fields
            )
            logger.info("Created a new trainer: %s", trainer)
        else:
            logger.info("Found existing trainer: %s", trainer)

        # Update attributes if they are present in trainer_data
        changed = False
        for key, value in trainer_data.items():
            if key != 'object_type' and key != 'children' and hasattr(trainer, key):
                if getattr(trainer, key) != value:  # Check if the value has changed
                    changed = True
                    setattr(trainer, key, value)  # Update the trainer instance
                    logger.info("Updated '%s' for trainer: %s", key, trainer)
        if changed:
            trainer.save()  # Save changes if any attributes were updated
        return trainer

    except Exception as e:
        logger.error("Error occurred while parsing trainer: %s", e)
        raise

def parse_jockey(jockey_data, existing_instance = None):
    logger.debug("Attempting to parse jockey data: %s", jockey_data)

    jockey = None
    try:
        
        # deal with existing instance
        if existing_instance:
            if 'first_name' in jockey_data and 'last_name' in jockey_data:
                if jockey_data['first_name'] == existing_instance.first_name and jockey_data['last_name'] == existing_instance.last_name:
                    jockey = existing_instance
        
        # Try identifiers first
        if not jockey and 'drf_jockey_id' in jockey_data:
            jockey = Jockeys.objects.filter(drf_jockey_id=jockey_data['drf_jockey_id']).first()

        if not jockey and 'equibase_jockey_id' in jockey_data:
            jockey = Jockeys.objects.filter(equibase_jockey_id=jockey_data['equibase_jockey_id']).first()

        if not jockey and 'first_name' in jockey_data and 'last_name' in jockey_data:
            jockey = Jockeys.objects.filter(first_name=jockey_data['first_name'], last_name=jockey_data['last_name']).first()

        # Create jockey if needed
        if not jockey:
            if 'first_name' not in jockey_data or 'last_name' not in jockey_data:
                raise ValueError("The 'first_name' and 'last_name' fields are required and cannot be None.")

            jockey = Jockeys.objects.create(
                first_name=jockey_data['first_name'],
                last_name=jockey_data['last_name'],
            )
            logger.info("Created a new jockey: %s", jockey)
        else:
            logger.info("Found existing jockey: %s", jockey)

        # Update attributes if they are present in jockey_data
        changed = False
        for key, value in jockey_data.items():
            if key != 'object_type' and key != 'children' and hasattr(jockey, key):
                if getattr(jockey, key) != value:  # Check if the value has changed
                    changed = True
                    setattr(jockey, key, value)  # Update the jockey instance
                    logger.info("Updated '%s' for jockey: %s", key, jockey)
        if changed:
            jockey.save()  # Save changes if any attributes were updated
        return jockey

    except Exception as e:
        logger.error("Error occurred while parsing jockey: %s", e)
        raise

def parse_entry(entry_data, parent_object=None):
    logger.debug("Attempting to parse entry data: %s", entry_data)
    try:
        race = parent_object or parse_race(entry_data['race'])
        if not race:
            raise ValueError(f"A parent race is required! {entry_data} and parent object of {parent_object}")

        # Find the existing entry by program number
        entry = None
        if 'program_number' in entry_data:
            entry = Entries.objects.filter(
                race=race,
                program_number=entry_data['program_number']
            ).first()
            
            # validate the horse didn't change
            if 'horse' in entry_data:
                if 'horse_name' in entry_data['horse']:
                    if entry.horse.horse_name != entry_data['horse']['horse_name']:
                        # horse changed!
                        logger.warning(f'{entry.program_number} changed from {entry.horse.horse_name} to {entry_data['horse']['horse_name']}')
                        entry.delete()
                        entry = None

        if not entry and 'horse' in entry_data:
            horse = parse_horse(entry_data['horse'])
            if horse:
                entry, created = Entries.objects.get_or_create(
                    race=race,
                    horse=horse
                )

        if not entry:
            raise ValueError("No matching entry found or could be created.")

        # Update entry with new values
        changed = False
        for key, value in entry_data.items():
            if isinstance(value, dict):
                # this is a dict object that needs to be parsed
                if key not in ['race', 'horse']: # weve already parsed those by now
                    if value['object_type'] in OBJECT_MAP:
                        old_id = -1
                        if getattr(entry, key):
                            old_id = getattr(entry, key).id
                        setattr(entry, key, OBJECT_MAP[value['object_type']](value, existing_instance=getattr(entry, key)))
                        if old_id != getattr(entry, key).id:
                            logger.debug(f'changing {key} from id of {old_id} to {getattr(entry, key).id}')
                            changed = True
            else:
                if hasattr(entry, key) and getattr(entry, key) != value:
                    changed = True
                    logger.debug("Updating field '%s' from '%s' to '%s'", key, getattr(entry, key), value)
                    setattr(entry, key, value)

        # Save the entry if it was updated
        if changed:
            entry.save()
            
        # Process children
        if 'children' in entry_data:
            for child in entry_data['children']:
                if child['object_type'] in OBJECT_MAP:
                    OBJECT_MAP[child['object_type']](child, entry)

        logger.info("Parsed entry: %s", entry)
        return entry

    except Exception as e:
        logger.error("Error occurred while parsing entry: %s", e)
        raise
        
def parse_payoff(payoff_data, parent_object=None):
    logger.debug("Attempting to parse payoff data: %s", payoff_data)

    payoff = None
    try:
        
        race = parent_object or parse_race(payoff_data['race'])
        if not race:
            raise ValueError(f"A parent race is required! {payoff_data} and parent object of {parent_object}")

        
        # payoff found by winning number and wager type
        payoff, created = Payoffs.objects.get_or_create(
            race=race,
            wager_type=payoff_data['wager_type'],
            winning_numbers=payoff_data['winning_numbers']
        )
        
        # Update attributes if they are present in jockey_data
        changed = False
        for key, value in payoff_data.items():
            if key != 'object_type' and key != 'children' and hasattr(payoff, key):
                if getattr(payoff, key) != value:  # Check if the value has changed
                    changed = True
                    setattr(payoff, key, value)  # Update the jockey instance
                    logger.info("Updated '%s' for payoff: %s", key, payoff)
        if changed:
            payoff.save()  # Save changes if any attributes were updated
        return payoff

    except Exception as e:
        logger.error("Error occurred while parsing payoff: %s", e)
        raise
     
def parse_fractional_time(fractional_time_data, parent_object=None):
    logger.debug("Attempting to parse fractional_time data: %s", fractional_time_data)

    fractional_time = None
    try:
        
        race = parent_object or parse_race(fractional_time_data['race'])
        if not race:
            raise ValueError(f"A parent race is required! {fractional_time_data} and parent object of {parent_object}")

        
        # special calcs just for fractional times
        if 'fractional_time_array' in fractional_time_data:
            
            payoffs = []
            for fractional_time_object in create_fractional_data_from_array_and_object(fractional_time_data['fractional_time_array'], race.distance):
                payoffs.append(parse_fractional_time(fractional_time_object, parent_object=race))

        else:
        
            # payoff found by winning number and wager type
            fractional_time, created = FractionalTimes.objects.get_or_create(
                race=race,
                point=[fractional_time_data['point']]
            )
        
            # Update attributes if they are present in jockey_data
            changed = False
            for key, value in fractional_time.items():
                if key != 'object_type' and key != 'children' and hasattr(fractional_time, key):
                    if getattr(fractional_time, key) != value:  # Check if the value has changed
                        changed = True
                        setattr(fractional_time, key, value)  # Update the jockey instance
                        logger.info("Updated '%s' for payoff: %s", key, fractional_time)
            if changed:
                fractional_time.save()  # Save changes if any attributes were updated
            return fractional_time

    except Exception as e:
        logger.error("Error occurred while parsing payoff: %s", e)
        raise
        
def process_parsed_objects(parsed_objects):
    logger.info("Processing parsed objects")

    try:
        for parsed_object in parsed_objects:
            if parsed_object['object_type'] in OBJECT_MAP:
                OBJECT_MAP[parsed_object['object_type']](parsed_object)
            else:
                raise ValueError(f"Unsupported object type: {parsed_object['object_type']}")

    except Exception as e:
        logger.error("Error occurred while processing parsed objects: %s", e)
        raise


# Define object map for parsing
OBJECT_MAP = {
    'race': parse_race,
    'track': parse_track,
    'horse': parse_horse,
    'entry': parse_entry
    # Add 'trainer': parse_trainer and 'jockey': parse_jockey as needed
}