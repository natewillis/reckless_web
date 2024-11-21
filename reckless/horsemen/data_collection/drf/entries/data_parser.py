import logging
from datetime import datetime
import pytz

# Configure logging
logger = logging.getLogger(__name__)

def parse_extracted_entries_data(extracted_entries_data):
    """
    Parse extracted entries data from DRF API into a format matching our models
    """
    # init return
    parsed_entries_data = []

    # iterate through races
    for race_data in extracted_entries_data.get('races', []):
        
        # create race object
        race_date = datetime.fromtimestamp(race_data['raceKey']["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()
        race = {
            'object_type': 'race',
            'race_date': race_date,
            'race_number': race_data["raceKey"]["raceNumber"],
            'post_time': race_data.get('postTime', ''),
            'age_restriction': race_data.get("ageRestriction", ""),
            'sex_restriction': "O" if race_data.get("sexRestriction", "") == "" else race_data.get("sexRestriction", ""),
            'minimum_claiming_price': race_data.get("minClaimPrice", 0),
            'maximum_claiming_price': race_data.get("maxClaimPrice", 0),
            'distance_description': race_data.get('distanceDescription', ''),
            'purse': race_data.get("purse", 0),
            'wager_text': race_data.get("wagerText", ""),
            'breed': race_data.get("breed", "Thoroughbred"),
            'cancelled': race_data.get("isCancelled", False),
            'course_type': race_data.get('courseType', 'D'),
            'drf_entries_import': True
        }
        parsed_entries_data.append(race)

        # Process runners (horses, jockeys, trainers, entries)
        for runner in race_data.get("runners", []):
            
            # Handle Horse
            horse = {
                'object_type': 'horse',
                'horse_name': runner['horseName'].strip().upper(),
                'registration_number': runner.get('registrationNumber', ''),
                'sire_name': runner.get('sireName', '').strip().upper(),
                'dam_name': runner.get('damName', '').strip().upper(),
                'dam_sire_name': runner.get('damSireName', '').strip().upper()
            }
            parsed_entries_data.append(horse)

            # Handle Trainer
            trainer = {
                'object_type': 'trainer',
                'first_name': runner["trainer"]["firstName"].strip().upper(),
                'last_name': runner["trainer"]["lastName"].strip().upper(),
                'middle_name': (runner["trainer"].get("middleName") or "").strip().upper(),
                'drf_trainer_id': runner["trainer"].get("id"),
                'drf_trainer_type': runner["trainer"].get("type"),
                'alias': (runner["trainer"].get("alias") or "").strip().upper()
            }
            parsed_entries_data.append(trainer)

            # Handle Jockey
            jockey = {
                'object_type': 'jockey',
                'first_name': runner["jockey"]["firstName"].strip().upper(),
                'last_name': runner["jockey"]["lastName"].strip().upper(),
                'middle_name': (runner["jockey"].get("middleName") or "").strip().upper(),
                'drf_jockey_id': runner["jockey"].get("id"),
                'drf_jockey_type': runner["jockey"].get("type"),
                'alias': (runner["jockey"].get("alias") or "").strip().upper()
            }
            parsed_entries_data.append(jockey)
            
            # Create entry
            entry = {
                'object_type': 'entry',
                'program_number': runner["programNumber"].strip().upper(),
                'post_position': int(runner['postPos']),
                'horse': horse,
                'trainer': trainer,
                'jockey': jockey,
                'race': race,
                'scratch_indicator': runner.get("scratchIndicator", ''),
                'medication': runner.get("medication"),
                'equipment': runner.get("equipment"),
                'weight': float(runner.get("weight", 0)),
                'drf_entries_import': True
            }
            parsed_entries_data.append(entry)

    return parsed_entries_data
