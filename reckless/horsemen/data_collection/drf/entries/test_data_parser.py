import unittest
from datetime import datetime
import pytz
from .data_parser import parse_extracted_entries_data

class TestDRFEntriesDataParser(unittest.TestCase):
    def setUp(self):
        # Sample DRF entries data matching API response format
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
                "purse": 50000,
                "wagerText": "WPS ONLY",
                "breed": "Thoroughbred",
                "isCancelled": False,
                "courseType": "D",
                "runners": [{
                    "programNumber": "1A",
                    "postPos": "1",
                    "horseName": "Test Horse",
                    "registrationNumber": "ABC123",
                    "sireName": "Test Sire",
                    "damName": "Test Dam",
                    "damSireName": "Test Dam Sire",
                    "trainer": {
                        "firstName": "John",
                        "lastName": "Doe",
                        "middleName": "A",
                        "id": "T123",
                        "type": "Primary",
                        "alias": "J Doe"
                    },
                    "jockey": {
                        "firstName": "Jane",
                        "lastName": "Smith",
                        "middleName": "B",
                        "id": "J456",
                        "type": "Primary",
                        "alias": "J Smith"
                    },
                    "scratchIndicator": "",
                    "medication": "L",
                    "equipment": "B",
                    "weight": 120.0
                }]
            }]
        }

    def test_parse_race_data(self):
        parsed_data = parse_extracted_entries_data(self.sample_data)
        race = next(item for item in parsed_data if item['object_type'] == 'race')
        
        self.assertEqual(race['race_number'], 1)
        self.assertEqual(race['post_time'], "13:00")
        self.assertEqual(race['age_restriction'], "3U")
        self.assertEqual(race['sex_restriction'], "F")
        self.assertEqual(race['minimum_claiming_price'], 25000)
        self.assertEqual(race['maximum_claiming_price'], 30000)
        self.assertEqual(race['distance_description'], "6 Furlongs")
        self.assertEqual(race['purse'], 50000)
        self.assertEqual(race['wager_text'], "WPS ONLY")
        self.assertEqual(race['breed'], "Thoroughbred")
        self.assertEqual(race['cancelled'], False)
        self.assertEqual(race['course_type'], "D")
        self.assertTrue(race['drf_entries_import'])

    def test_parse_horse_data(self):
        parsed_data = parse_extracted_entries_data(self.sample_data)
        horse = next(item for item in parsed_data if item['object_type'] == 'horse')
        
        self.assertEqual(horse['horse_name'], "TEST HORSE")
        self.assertEqual(horse['registration_number'], "ABC123")
        self.assertEqual(horse['sire_name'], "TEST SIRE")
        self.assertEqual(horse['dam_name'], "TEST DAM")
        self.assertEqual(horse['dam_sire_name'], "TEST DAM SIRE")

    def test_parse_trainer_data(self):
        parsed_data = parse_extracted_entries_data(self.sample_data)
        trainer = next(item for item in parsed_data if item['object_type'] == 'trainer')
        
        self.assertEqual(trainer['first_name'], "JOHN")
        self.assertEqual(trainer['last_name'], "DOE")
        self.assertEqual(trainer['middle_name'], "A")
        self.assertEqual(trainer['drf_trainer_id'], "T123")
        self.assertEqual(trainer['drf_trainer_type'], "Primary")
        self.assertEqual(trainer['alias'], "J DOE")

    def test_parse_jockey_data(self):
        parsed_data = parse_extracted_entries_data(self.sample_data)
        jockey = next(item for item in parsed_data if item['object_type'] == 'jockey')
        
        self.assertEqual(jockey['first_name'], "JANE")
        self.assertEqual(jockey['last_name'], "SMITH")
        self.assertEqual(jockey['middle_name'], "B")
        self.assertEqual(jockey['drf_jockey_id'], "J456")
        self.assertEqual(jockey['drf_jockey_type'], "Primary")
        self.assertEqual(jockey['alias'], "J SMITH")

    def test_parse_entry_data(self):
        parsed_data = parse_extracted_entries_data(self.sample_data)
        entry = next(item for item in parsed_data if item['object_type'] == 'entry')
        
        self.assertEqual(entry['program_number'], "1A")
        self.assertEqual(entry['post_position'], 1)
        self.assertEqual(entry['scratch_indicator'], "")
        self.assertEqual(entry['medication'], "L")
        self.assertEqual(entry['equipment'], "B")
        self.assertEqual(entry['weight'], 120.0)
        self.assertTrue(entry['drf_entries_import'])
        
        # Test relationships
        self.assertEqual(entry['horse']['horse_name'], "TEST HORSE")
        self.assertEqual(entry['trainer']['last_name'], "DOE")
        self.assertEqual(entry['jockey']['last_name'], "SMITH")
        self.assertEqual(entry['race']['race_number'], 1)

    def test_empty_data(self):
        parsed_data = parse_extracted_entries_data({})
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
                    "programNumber": "1",
                    "postPos": "1",
                    "horseName": "Test Horse",
                    "trainer": {
                        "firstName": "John",
                        "lastName": "Doe"
                    },
                    "jockey": {
                        "firstName": "Jane",
                        "lastName": "Smith"
                    }
                }]
            }]
        }
        
        parsed_data = parse_extracted_entries_data(minimal_data)
        entry = next(item for item in parsed_data if item['object_type'] == 'entry')
        
        # Check default values for optional fields
        self.assertEqual(entry['scratch_indicator'], '')
        self.assertEqual(entry['medication'], None)
        self.assertEqual(entry['equipment'], None)
        self.assertEqual(entry['weight'], 0.0)

if __name__ == '__main__':
    unittest.main()
