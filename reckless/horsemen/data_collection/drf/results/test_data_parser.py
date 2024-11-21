import unittest
from datetime import datetime
import pytz
from .data_parser import parse_extracted_results_data

class TestDRFResultsDataParser(unittest.TestCase):
    def setUp(self):
        # Sample DRF results data matching API response format
        self.sample_data = {
            "races": [{
                "raceKey": {
                    "raceDate": {
                        "date": 1672531200000  # 2023-01-01
                    },
                    "raceNumber": 1
                },
                "postTime": "13:00",
                "ageRestriction": "3U",
                "sexRestriction": "F",
                "minClaimPrice": 25000,
                "maxClaimPrice": 30000,
                "distanceDescription": "6 Furlongs",
                "totalPurse": "50,000",
                "breed": "Thoroughbred",
                "surface": "D",
                "raceTypeDescription": "CLAIMING",
                "trackConditionDescription": "FAST",
                "scratches": ["SCRATCH HORSE"],
                "runners": [{
                    "horseName": "Test Horse",
                    "winPayoff": 6.80,
                    "placePayoff": 3.40,
                    "showPayoff": 2.60
                }],
                "wagerTypes": [{
                    "wagerType": "EX",
                    "baseAmount": 2.00
                }],
                "payoffs": [{
                    "wagerType": "EX",
                    "winningNumbers": "1-2",
                    "totalPool": "12,345",
                    "payoffAmount": "24.60"
                }]
            }]
        }

    def test_parse_race_data(self):
        parsed_data = parse_extracted_results_data(self.sample_data)
        race = next(item for item in parsed_data if item['object_type'] == 'race')
        
        self.assertEqual(race['race_number'], 1)
        self.assertEqual(race['post_time'], "13:00")
        self.assertEqual(race['age_restriction'], "3U")
        self.assertEqual(race['sex_restriction'], "F")
        self.assertEqual(race['minimum_claiming_price'], 25000)
        self.assertEqual(race['maximum_claiming_price'], 30000)
        self.assertEqual(race['distance_description'], "6 Furlongs")
        self.assertEqual(race['purse'], 50000.0)
        self.assertEqual(race['breed'], "Thoroughbred")
        self.assertEqual(race['race_surface'], "D")
        self.assertEqual(race['race_type'], "CLAIMING")
        self.assertEqual(race['condition'], "FAST")
        self.assertTrue(race['drf_results_import'])

    def test_parse_scratch_data(self):
        parsed_data = parse_extracted_results_data(self.sample_data)
        scratch = next(item for item in parsed_data if item['object_type'] == 'scratch')
        
        self.assertEqual(scratch['horse_name'], "SCRATCH HORSE")
        self.assertEqual(scratch['scratch_indicator'], "U")
        self.assertEqual(scratch['race']['race_number'], 1)

    def test_parse_horse_and_entry_data(self):
        parsed_data = parse_extracted_results_data(self.sample_data)
        horse = next(item for item in parsed_data if item['object_type'] == 'horse')
        entry = next(item for item in parsed_data if item['object_type'] == 'entry')
        
        self.assertEqual(horse['horse_name'], "TEST HORSE")
        
        self.assertEqual(entry['horse']['horse_name'], "TEST HORSE")
        self.assertEqual(entry['win_payoff'], 6.80)
        self.assertEqual(entry['place_payoff'], 3.40)
        self.assertEqual(entry['show_payoff'], 2.60)
        self.assertEqual(entry['race']['race_number'], 1)

    def test_parse_payoff_data(self):
        parsed_data = parse_extracted_results_data(self.sample_data)
        payoff = next(item for item in parsed_data if item['object_type'] == 'payoff')
        
        self.assertEqual(payoff['wager_type'], "EX")
        self.assertEqual(payoff['winning_numbers'], "1-2")
        self.assertEqual(payoff['total_pool'], 12345.0)
        self.assertEqual(payoff['payoff_amount'], 24.60)
        self.assertEqual(payoff['base_amount'], 2.00)
        self.assertEqual(payoff['race']['race_number'], 1)

    def test_empty_data(self):
        parsed_data = parse_extracted_results_data({})
        self.assertEqual(parsed_data, [])

    def test_missing_optional_fields(self):
        minimal_data = {
            "races": [{
                "raceKey": {
                    "raceDate": {
                        "date": 1672531200000
                    },
                    "raceNumber": 1
                },
                "runners": [{
                    "horseName": "Test Horse"
                }]
            }]
        }
        
        parsed_data = parse_extracted_results_data(minimal_data)
        race = next(item for item in parsed_data if item['object_type'] == 'race')
        entry = next(item for item in parsed_data if item['object_type'] == 'entry')
        
        # Check default values for optional fields
        self.assertEqual(race['sex_restriction'], "O")
        self.assertEqual(race['minimum_claiming_price'], 0)
        self.assertEqual(entry['win_payoff'], 0.0)
        self.assertEqual(entry['place_payoff'], 0.0)
        self.assertEqual(entry['show_payoff'], 0.0)

if __name__ == '__main__':
    unittest.main()
