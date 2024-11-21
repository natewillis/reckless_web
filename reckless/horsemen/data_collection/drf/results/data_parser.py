import logging
from datetime import datetime
import pytz

# Configure logging
logger = logging.getLogger(__name__)

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
            'post_time': race_data.get('postTime', ''),
            'age_restriction': race_data.get("ageRestriction", ""),
            'sex_restriction': "O" if race_data.get("sexRestriction", "") == "" else race_data.get("sexRestriction", ""),
            'minimum_claiming_price': race_data.get("minClaimPrice", 0),
            'maximum_claiming_price': race_data.get("maxClaimPrice", 0),
            'distance_description': race_data.get("distanceDescription", ""),
            'purse': float(race_data.get("totalPurse", "0").replace(',', '')),
            'breed': race_data.get("breed", "Thoroughbred"),
            'cancelled': False,
            'race_surface': race_data.get('surface', 'D'),
            'race_type': race_data.get('raceTypeDescription', ''),
            'condition': race_data.get("trackConditionDescription", '').strip().upper(),
            'drf_results_import': True
        }
        parsed_results_data.append(race)

        # Handle scratches
        for horse_name in race_data.get('scratches', []):
            scratch = {
                'object_type': 'scratch',
                'race': race,
                'horse_name': horse_name.strip().upper(),
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
                'wager_type': payoff_data.get('wagerType', ''),
                'winning_numbers': payoff_data.get('winningNumbers', '').strip().upper(),
                'total_pool': float(payoff_data.get('totalPool', '0').replace(',', '')),
                'payoff_amount': float(payoff_data.get('payoffAmount', '0').replace(',', '')),
                'base_amount': base_amount
            }
            parsed_results_data.append(payoff)

    return parsed_results_data
