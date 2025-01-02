"""
Parser module for Equibase chart data.
Handles parsing of race information, entries, past performances, and related data.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from horsemen.data_collection.utils import (
    convert_string_to_seconds,
    convert_lengths_back_string,
    convert_string_to_furlongs,
    get_best_choice_from_description_code,
    get_horsename_and_country_from_drf
)
from horsemen.constants import BREED_CHOICES

# Configure logging
logger = logging.getLogger(__name__)

def parse_track_race_date_race_number(line: str) -> Dict[str, Any]:
    """
    Parse track name, race date, and race number from a line of text.
    
    Args:
        line: String containing track, date, and race information
        
    Returns:
        Dictionary containing parsed track, race date, and race number
    """
    
    try:
        pattern = r'^([A-Za-z0-9\s\&]+)-([A-Za-z0-9\s\,]+)-\s?Race\s?(\d+)'
        match = re.search(pattern, line)
        
        if not match:
            return {}

        data = {
            'track': {
                'object_type': 'track',
                'name': match.group(1).strip().upper(),
            },
            'race_date': datetime.strptime(match.group(2).strip(), '%B %d, %Y'),
            'race_number': int(match.group(3).strip())
        }
        
        logger.debug("Successfully parsed track/race info: %s", data)
        return data

    except Exception as e:
        logger.error("Error parsing track/race info: %s", e)
        return {}

def parse_race_type_name_grade_breed(line: str) -> Dict[str, Any]:
    """
    Parse race type, name, grade, and breed information from a line of text.
    
    Args:
        line: String containing race details
        
    Returns:
        Dictionary containing parsed race information
    """
    
    try:
        pattern = (
            r'Race\s\d+\s(?:.?\s)?([A-Z ]+)'
            r'( (.+) (Grade (\d))|'
            r' (.+ S\.)( (.+))?|'
            r' (.+))? - (Thoroughbred|Quarter Horse|Arabian|Mixed)'
        )
        
        match = re.search(pattern, line)
        if not match:
            return {}

        breed_text = match.group(10)
        race_type_text = match.group(1)
        data = {
            'breed': get_best_choice_from_description_code(breed_text, BREED_CHOICES),
            'race_type_text': race_type_text
        }

        # Handle grade and race name
        if match.group(5):  # Grade is present
            data.update({
                'grade': int(match.group(5)),
                'race_name': match.group(3)
            })
        else:  # No grade, try to get race name
            race_name = match.group(6) or match.group(9)
            if race_name:
                # Fix stakes abbreviation
                race_name = race_name.replace('S.', 'STAKES')
                data['race_name'] = race_name

        # Handle special case for stakes races
        if race_type_text.upper().startswith('STAKES'):
            split_text = race_type_text.split(' ', 2)
            data['race_type_text'] = split_text[0]
            if len(split_text) > 1 and split_text[1] and 'race_name' in data:
                data['race_name'] = f"{split_text[1]} {data['race_name']}"

        logger.debug("Successfully parsed race details: %s", data)
        return data

    except Exception as e:
        logger.error("Error parsing race details: %s", e)
        return {}

def parse_distance_surface_track_record(line: str) -> Dict[str, Any]:
    """
    Parse race distance, surface, and track record information.
    
    Args:
        line: String containing distance and track information
        
    Returns:
        Dictionary containing parsed distance, surface, and track record details
    """
    
    try:
        if not line.startswith('Distance:'):
            return {}

        data = {}
        split_string = line.split(' On The ')
        
        # Parse distance
        distance_str = split_string[0].replace('Distance: ', '').replace('About ', '')
        data['distance'] = convert_string_to_furlongs(distance_str)
        
        # Parse surface
        remaining_string = split_string[1]
        data['race_surface'] = 'D' if 'DIRT' in remaining_string.upper() else 'T'

        # Parse track record if present
        pattern = r'Track Record: \((.+) - ([\d:\.]+) - (.+)\)'
        match = re.search(pattern, remaining_string)
        if match:
            data.update({
                'record_horse_name': match.group(1),
                'record_time_string': match.group(2),
                'record_date': datetime.strptime(match.group(3), '%B %d, %Y')
            })

        logger.debug("Successfully parsed distance/surface info: %s", data)
        return data

    except Exception as e:
        logger.error("Error parsing distance/surface info: %s", e)
        return {}

def parse_purse(line: str) -> Dict[str, Any]:
    """
    Parse purse amount from a line of text.
    
    Args:
        line: String containing purse information
        
    Returns:
        Dictionary containing parsed purse amount
    """
    
    try:
        if 'Purse: $' not in line:
            return {}

        pattern = r'Purse: \$\d{1,3}(?:,\d{3})*'
        match = re.search(pattern, line)
        if match:
            purse = int(match.group(0).replace('Purse: $', '').replace(',', ''))
            logger.debug("Successfully parsed purse: %d", purse)
            return {'purse': purse}

        return {}

    except Exception as e:
        logger.error("Error parsing purse: %s", e)
        return {}
    
def parse_cancelled(line: str) -> Dict[str, Any]:
    """
    Parse cancelled race from a line of text.
    
    Args:
        line: String containing cancelled race
        
    Returns:
        Dictionary containing cancelled race
    """
    
    try:
        if 'CANCELLED - ' in line.upper():
            return {'cancelled': True}
        else:
            return {}

    except Exception as e:
        logger.error("Error parsing cancelled race: %s", e)
        return {}
    
def parse_hurdles(line: str) -> Dict[str, Any]:
    """
    Parse hurdles race from a line of text.
    
    Args:
        line: String containing hurdles race
        
    Returns:
        Dictionary containing hurdles race
    """
    
    try:
        if 'TO BE RUN OVER NATIONAL FENCES' in line.upper():
            return {'hurdles': True}
        else:
            return {}

    except Exception as e:
        logger.error("Error parsing hurdles race: %s", e)
        return {}
    
def parse_track_condition(line: str) -> Dict[str, Any]:
    """
    Parse track condition amount from a line of text.
    
    Args:
        line: String containing track condition information
        
    Returns:
        Dictionary containing parsed track condition
    """
    
    try:
        if 'Track:' not in line:
            return {}

        pattern = r'Track: (\w+)'
        match = re.search(pattern, line)
        if match:
            condition = match.group(1).strip().upper()
            logger.debug("Successfully parsed track condition: %s", condition)
            return {'condition': condition}
        else:
            return {'condition': "UNKNOWN"}

    except Exception as e:
        logger.error("Error parsing condition: %s", e)
        return {}

def parse_entries(table_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse entry information from table data.
    
    Args:
        table_data: Dictionary containing entry table information
        
    Returns:
        List of dictionaries containing parsed entry information
    """
    logger.debug("Parsing entries from table data")
    
    try:
        objects = []
        for entry_data in table_data['data']:
            entry = {'object_type': 'entry'}
            
            # Parse horse name and jockey
            horse_jockey_text = entry_data['HORSENAME(JOCKEY)']['normal_text']
            pattern = r'(.+) \(((.+),( (.+))?)?\)'
            match = re.search(pattern, horse_jockey_text)
            
            if match:
                horse_name = match.group(1).upper().strip().replace('DQ-', '')
                entry['horse'] = {
                    'object_type': 'horse',
                    'horse_name': get_horsename_and_country_from_drf(horse_name)[0],
                }
                if match.group(3):  # Jockey information exists
                    entry['jockey'] = {
                        'object_type': 'jockey',
                        'first_name': (match.group(5) or '').strip().upper(),
                        'last_name': match.group(3).strip().upper(),
                    }
            
            # Parse other entry data
            entry.update({
                'comments': entry_data['COMMENTS']['normal_text'].strip().upper(),
                'post_position': int(entry_data['PP']['normal_text'].strip()),
                'program_number': entry_data['PGM']['normal_text'].strip().upper()
            })
            
            # Parse speed index if present
            if 'SP.IN.' in entry_data:
                speed_text = entry_data['SP.IN.']['normal_text']
                if speed_text.isnumeric():
                    entry['speed_index'] = int(speed_text)
            
            objects.append(entry)
        
        logger.debug("Successfully parsed %d entries", len(objects))
        return objects

    except Exception as e:
        logger.error("Error parsing entries: %s", e)
        return []

def parse_past_performance(table_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse past performance information from table data.
    
    Args:
        table_data: Dictionary containing past performance table information
        
    Returns:
        List of dictionaries containing parsed past performance information
    """
    logger.debug("Parsing past performance data")
    
    try:
        objects = []
        for idx, entry_data in enumerate(table_data['data']):

            program_number = entry_data['PGM']['normal_text'].strip().upper()
            if program_number == '':
                continue

            entry = {
                'object_type': 'entry',
                'program_number': program_number,
                'children': []
            }

            # get horse name as a backup
            if 'HORSENAME' in entry_data:
                if entry_data['HORSENAME']['normal_text'].strip().upper() != '':
                    entry['horse'] = {
                        'object_type': 'horse',
                        'horse_name': get_horsename_and_country_from_drf(entry_data['HORSENAME']['normal_text'].strip().upper())[0],
                    }
            
            # Parse points of call
            idx = 0
            for column_name in table_data['header_order']:

                if column_name in ['PGM', 'HORSENAME']:
                    continue
                    
                column_data = entry_data[column_name]

                if not column_data['normal_text'].isnumeric():
                    continue
                    
                point_of_call = {
                    'object_type': 'point_of_call',
                    'position': int(column_data['normal_text']),
                    'lengths_back': convert_lengths_back_string(column_data['super_text']),
                    'text': column_name,
                    'line_index': idx
                }
                entry['children'].append(point_of_call)
                idx += 1
            
            objects.append(entry)
        
        logger.debug("Successfully parsed past performance for %d entries", len(objects))
        return objects

    except Exception as e:
        logger.error("Error parsing past performance: %s", e)
        return []

def parse_fractional_times(line: str) -> List[Dict[str, Any]]:
    """
    Parse fractional times from a line of text.
    
    Args:
        line: Dictionary containing line text with fractional times
        
    Returns:
        List containing parsed fractional time information
    """
    
    try:
        if 'Fractional Times:' not in line and 'Final Time:' not in line:
            return []

        pattern = r'\b\d+:\d+\.\d+|\b\d+\.\d+'
        time_strings = re.findall(pattern, line)
        
        if not time_strings:
            logger.warning("No fractional times found in line: %s", line)
            return []
        logger.debug(f'time strings is {time_strings}')

        fractional_times = [convert_string_to_seconds(time_str) for time_str in time_strings]
        
        logger.debug("Successfully parsed %d fractional times", len(fractional_times))
        return [{
            'object_type': 'fractional_time',
            'fractional_time_array': fractional_times
        }]

    except Exception as e:
        logger.error("Error parsing fractional times: %s", e)
        return []

def parse_extracted_chart_data(extracted_chart_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse complete extracted chart data into structured race information.
    
    Args:
        extracted_chart_data: List of dictionaries containing extracted chart data
        
    Returns:
        List of dictionaries containing fully parsed race information
    """
    logger.info("Beginning parse of extracted chart data")
    
    try:
        # Define parsing configurations
        line_parsers = [
            {'parser': parse_track_race_date_race_number, 'output': 'attribute'},
            {'parser': parse_race_type_name_grade_breed, 'output': 'attribute'},
            {'parser': parse_distance_surface_track_record, 'output': 'attribute'},
            {'parser': parse_purse, 'output': 'attribute'},
            {'parser': parse_fractional_times, 'output': 'children'},
            {'parser': parse_track_condition, 'output': 'attribute'},
            {'parser': parse_cancelled, 'output': 'attribute'},
            {'parser': parse_hurdles, 'output': 'attribute'},
        ]
        
        table_parsers = {
            'entries': {'parser': parse_entries, 'output': 'children'},
            'past_performance': {'parser': parse_past_performance, 'output': 'children'}
        }

        parsed_chart_data = []
        for race_data in extracted_chart_data:
            race = {
                'object_type': 'race',
                'equibase_chart_import': True,
                'children': []
            }

            # Process line parsers
            for config in line_parsers:
                for line in race_data['lines']:
                    if config['output'] == 'attribute':
                        race.update(config['parser'](line))
                    else:
                        race['children'].extend(config['parser'](line))

            # Process table parsers
            for table_name, config in table_parsers.items():
                if table_name in race_data['tables']:
                    if config['output'] == 'children':
                        race['children'].extend(config['parser'](race_data['tables'][table_name]))
                    else:
                        race.update(config['parser'](race_data['tables'][table_name]))


            parsed_chart_data.append(race)

        logger.info("Successfully parsed %d races", len(parsed_chart_data))
        return parsed_chart_data

    except Exception as e:
        logger.error("Error parsing extracted chart data: %s", e)
        return []
