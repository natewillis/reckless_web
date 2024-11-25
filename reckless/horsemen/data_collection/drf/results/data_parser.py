import logging
from datetime import datetime, timedelta
import pytz
import requests
from django.db.models import Q
from horsemen.models import Races, Tracks
from horsemen.data_collection.utils import convert_string_to_furlongs, get_best_choice_from_description_code
from horsemen.constants import BREED_CHOICES, EQUIBASE_RACE_TYPE_CHOICES, BET_CHOICES

# Configure logging
logger = logging.getLogger(__name__)

def get_results_data():
    """
    Get results data for races in the previous 14 days that haven't been imported
    or any races happening today regardless of import status
    """
    logger.info('running get_results_data')

    # Get current date
    today = datetime.now(pytz.UTC).date()
    fourteen_days_ago = today - timedelta(days=14)

    # Query races that match our criteria
    races = Races.objects.filter(
        Q(race_date__gte=fourteen_days_ago, race_date__lte=today, drf_results_import=False) |  # Last 14 days without import
        Q(race_date=today)  # Today's races regardless of import status
    ).select_related('track')

    # Get unique track and date combinations
    track_date_combos = set((race.track, race.race_date) for race in races)

    # Process each track/date combination
    parsed_results_data = []
    for track, race_date in track_date_combos:
        # Get results URL for this track and date
        url = track.get_drf_results_url_for_date(race_date)
        
        try:
            # Fetch data from URL
            response = requests.get(url)
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                # Parse the extracted data
                parsed_data = parse_extracted_results_data(data)
                parsed_results_data.extend(parsed_data)
                logger.info(f'Successfully fetched and parsed results data for {track.name} on {race_date}')
            else:
                logger.error(f'Failed to fetch results data from URL {url}. Status code: {response.status_code}')
        except Exception as e:
            logger.error(f'Error fetching results data for {track.name} on {race_date}: {str(e)}')

    return parsed_results_data

def parse_extracted_results_data(extracted_results_data):
    """
    Parse extracted results data from DRF API into a format matching our models
    """
    # init return
    parsed_results_data = []

    # iterate through races
    for race_data in extracted_results_data.get('races', []):
        
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
            'minimum_claiming_price': int(race_data.get("minClaimPrice", 0)),
            'maximum_claiming_price': int(race_data.get("maxClaimPrice", 0)),
            'distance': convert_string_to_furlongs(race_data.get("distanceDescription", "")),
            'purse': float(race_data.get("totalPurse", "0").replace(',', '')),
            'breed': get_best_choice_from_description_code(race_data.get("breed", "Thoroughbred"), BREED_CHOICES),
            'cancelled': False,
            'race_surface': race_data.get('surface', 'D'),
            'race_type': get_best_choice_from_description_code(race_data.get('raceTypeDescription', ''), EQUIBASE_RACE_TYPE_CHOICES) ,
            'condition': race_data.get("trackConditionDescription", '').strip().upper(),
            'drf_results_import': True
        }
        parsed_results_data.append(race)

        # Handle scratches
        for horse_name in race_data.get('scratches', []):
            scratch = {
                'object_type': 'entry',
                'race': race,
                'horse': {'horse_name': horse_name.strip().upper()},
                'scratch_indicator': 'U'  # Unknown reason for scratch
            }
            parsed_results_data.append(scratch)

        # Handle runners and WPS payoffs
        for runner_data in race_data.get('runners', []):
            horse_name = runner_data.get('horseName', '').strip().upper()
            
            # Create horse entry
            horse = {
                'object_type': 'horse',
                'horse_name': horse_name
            }
            parsed_results_data.append(horse)

            # Create entry with WPS payoffs
            entry = {
                'object_type': 'entry',
                'race': race,
                'horse': horse,
                'win_payoff': float(runner_data.get('winPayoff', 0)),
                'place_payoff': float(runner_data.get('placePayoff', 0)),
                'show_payoff': float(runner_data.get('showPayoff', 0))
            }
            parsed_results_data.append(entry)

        # Handle exotic payoffs
        for payoff_data in race_data.get('payoffs', []):
            # Get base amount from wager types
            base_amount = 0
            for wager_type_data in race_data.get('wagerTypes', []):
                if wager_type_data.get('wagerType', '') == payoff_data.get('wagerType', ''):
                    base_amount = float(wager_type_data.get('baseAmount', 0))

            payoff = {
                'object_type': 'payoff',
                'race': race,
                'wager_type': get_best_choice_from_description_code(payoff_data.get('wagerName', ''), BET_CHOICES),
                'winning_numbers': payoff_data.get('winningNumbers', '').strip().upper(),
                'total_pool': float(payoff_data.get('totalPool', '0').replace(',', '')),
                'payoff_amount': float(payoff_data.get('payoffAmount', '0').replace(',', '')),
                'base_amount': base_amount
            }
            parsed_results_data.append(payoff)

    return parsed_results_data
