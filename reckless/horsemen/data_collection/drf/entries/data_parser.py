import logging
from datetime import datetime, timedelta
import pytz
import requests
from django.db.models import Q
from horsemen.models import Races
from horsemen.data_collection.utils import convert_string_to_furlongs, get_best_choice_from_description_code, get_horsename_and_country_from_drf
from horsemen.constants import BREED_CHOICES

# Configure logging
logger = logging.getLogger(__name__)

def get_entries_data():
    """
    Get entries data for races in the next 3 days that haven't been imported
    or any races happening today regardless of import status
    """
    logger.info('running get_entries_data')

    # Get current date
    today = datetime.now(pytz.UTC).date()
    days_future = today + timedelta(days=7)

    # Query races that match our criteria
    races = Races.objects.filter(
        Q(race_date__gte=today, race_date__lte=days_future, drf_entries_import=False) |  # Next 3 days without import
        Q(race_date=today)  # Today's races regardless of import status
    ).select_related('track')

    # Get unique track and date combinations
    track_date_combos = set((race.track, race.race_date) for race in races)

    # Process each track/date combination
    parsed_entries_data = []
    for track, race_date in track_date_combos:
        # Get entries URL for this track and date
        url = track.get_drf_entries_url_for_date(race_date)
        
        try:
            # Fetch data from URL
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                # Parse the extracted data
                parsed_data = parse_extracted_entries_data(data)
                parsed_entries_data.extend(parsed_data)
                logger.info(f'Successfully fetched and parsed entries data for {track.name} on {race_date}')
            else:
                logger.error(f'Failed to fetch entries data from URL {url}. Status code: {response.status_code}')
        except Exception as e:
            logger.error(f'Error fetching entries data for {track.name} on {race_date}: {str(e)}')

    return parsed_entries_data

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
            'track': {
                'code': race_data["raceKey"]["trackId"],
                'country': race_data["raceKey"]["country"]
            },
            'post_time_string': race_data.get('postTime', ''),
            'age_restriction': race_data.get("ageRestriction", ""),
            'sex_restriction': "O" if race_data.get("sexRestriction", "") == "" else race_data.get("sexRestriction", ""),
            'minimum_claiming_price': race_data.get("minClaimPrice", 0),
            'maximum_claiming_price': race_data.get("maxClaimPrice", 0),
            'distance': convert_string_to_furlongs(race_data.get('distanceDescription', '')),
            'purse': race_data.get("purse", 0),
            'wager_text': race_data.get("wagerText", ""),
            'breed': get_best_choice_from_description_code(race_data.get("breed", "Thoroughbred"),BREED_CHOICES),
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
                'horse_name': get_horsename_and_country_from_drf(runner['horseName'].strip().upper())[0],
                'horse_state_or_country': get_horsename_and_country_from_drf(runner['horseName'].strip().upper())[1],
                'registration_number': runner.get('registrationNumber', ''),
                'sire_name': runner.get('sireName', '').strip().upper(),
                'dam_name': runner.get('damName', '').strip().upper(),
                'dam_sire_name': runner.get('damSireName', '').strip().upper()
            }
            parsed_entries_data.append(horse)

            # Handle Trainer
            if runner["trainer"].get("id") > 0:
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
            if runner["jockey"]["firstName"] != 'SCRATCHED' and runner["jockey"]["id"] > 0:
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
                'medication': runner.get("medication",''),
                'equipment': runner.get("equipment",''),
                'weight': float(runner.get("weight", 0)),
                'drf_entries_import': True
            }
            # fix scratch indicator of "Y"
            entry['scratch_indicator']=entry['scratch_indicator'].replace('Y','U')

            # fix scratch indicator of "N" when scratched
            if entry['post_position'] > 90 and entry['scratch_indicator']=='N':
                entry['scratch_indicator'] = 'U'
            if entry['program_number'] == '':
                del entry['program_number']
                
            parsed_entries_data.append(entry)

    return parsed_entries_data
