import logging
import re
import json
from datetime import datetime
from horsemen.data_collection.utils import convert_string_to_seconds, convert_lengths_back_string

# Configure logging
logger = logging.getLogger(__name__)


def parse_track_race_date_race_number(line):
    
    # init return
    data = {}

    # define pattern
    pattern = r'([A-Z0-9\s&]+)\s?-\s?(.+?)\s?-\s?Race\s?(\d+)'

    # search
    match = re.search(pattern, line)
    if match:
        data = {
            'track': {
                'object_type': 'track',
                'name': match.group(1).strip().upper(),
            },
            'race_date': datetime.strptime(match.group(2), '%B %d, %Y'),
            'race_number': int(match.group(3))
        }
    
    # return
    return data

def parse_race_type_name_grade_breed(line):

    # init return
    data = {}

    # define pattern
    pattern = r'Race\s\d+\s(?:.?\s)?([A-Z ]+)( (.+) (Grade (\d))| (.+ S\.)( (.+))?| (.+))? - (Thoroughbred|Quarter Horse|Arabian|Mixed)'

    # search
    match = re.search(pattern, line)
    if match:
        
        # breed and type should always be there
        breed_text = match.group(10)
        race_type_text = match.group(1)

        # init all the other things
        grade = None
        race_name = None
        black_type = None

        # get grade if its there also black type
        if match.group(5):
            grade = int(match.group(5))
            black_type = match.group(4)
        
        # try and get the race name
        if grade:
            race_name = match.group(3)
        else:
            race_name_text = match.group(6)
            if race_name_text:
                race_name = race_name_text
            else:
                race_name_text = match.group(9)
                if race_name_text:
                    race_name = race_name_text
            
            black_type_text = match.group(8)
            if black_type_text:
                black_type = black_type_text
        
        # fix for when race anme starts with capital letters
        if race_type_text.upper().startswith('STAKES'):
            split_text = race_type_text.split(' ', 2)
            race_type_text = split_text[0]
            if len(split_text)>1 and split_text[1]:
                race_name = split_text[1] + ' ' + race_name

        # they abbreviate stakes
        if race_name:
            race_name = race_name.replace('S.', 'STAKES')

        # formulate return
        data = {
            'breed_text': breed_text,
            'race_type_text': race_type_text
        }
        if race_name:
            data['race_name'] = race_name
        if grade:
            data['grade'] = grade

    # return
    return data

def parse_distance_surface_track_record(line):

    # init return
    data = {}

    if line.startswith('Distance:'):

        # get the distance with splits
        split_string = line.split(' On The ')
        data['distance_string'] = split_string[0].replace('Distance: ','').replace('About ','')
        remaining_string = split_string[1]
        data['surface'] = 'D' if 'DIRT' in remaining_string.upper() else 'T'

        # define pattern
        pattern = r'Track Record: \((.+) - ([\d:\.]+) - (.+)\)'

        # search
        match = re.search(pattern, remaining_string)
        if match:
            data['record_horse_name'] = match.group(1)
            data['record_time_string'] = match.group(2)
            data['record_date'] = datetime.strptime(match.group(3), '%B %d, %Y')

    # return
    return data

def parse_purse(line):

    # init return
    data = {}

    if 'Purse: $' in line:
        pattern = r'Purse: \$\d{1,3}(?:,\d{3})*'
        match = re.search(pattern, line)
        if match:
            data['purse'] = int(match.group(0).replace('Purse: $', '').replace(',', ''))

    # return
    return data

def parse_entries(table_data):
    
    # init return
    objects = []
    
    # iterate through entries
    for entry_data in table_data['data']:
        
        # init return
        entry = {
            'object_type': 'entry',
        }
        
        # get name/jockey
        pattern = r'(.+) \(((.+),( (.+))?)?\)'
        match = re.search(pattern, entry_data['HORSENAME(JOCKEY)']['normal_text'])
        if match:
            entry['horse'] = {
                'object_type': 'horse',
                'horse_name': match.subgroup(1).upper().strip().replace('DQ-','')
            }
            entry['jockey'] = {
                'object_type': 'jockey',
                'first_name': match.subgroup(5).strip().upper(),
                'last_name': match.subgroup(3).strip().upper(),
            }
        
        
        # comments
        entry['comments'] = entry_data['COMMENTS']['normal_text']
        
        # post position
        entry['post_position'] = int(entry_data['PP']['normal_text'])
        
        # program number
        entry['program_number'] = entry_data['PGM']['normal_text']
        
        # TODO: IND.TIME (incorporate into split_velocities)
        
        # speed index
        if 'SP.IN.' in entry_data:
            if entry_data['SP.IN.']['normal_text'].isnumeric():
                entry['speed_index'] = int(entry_data['SP.IN.']['normal_text'])
        
        # append object
        objects.append(entry)
    
    # return
    return objects


def parse_past_performance(table_data):
    
    # init return
    objects = []
    
    # iterate through entries
    for entry_data in table_data['data']:
        
        # init return
        entry = {
            'object_type': 'entry',
            'children': []
        }
        
        # horse name and  program number
        entry['program_number']=entry_data['PGM']['normal_text']
        
        # get points of call
        line_index = 0;
        for column_name in table_data['header_order']:
            if column_name in ['PGM','HORSENAME']:
                continue
            if not table_data['data'][column_name]['normal_text'].isnumeric():
                continue
            line_index += 1
            point_of_call = {
                'object_type': 'point_of_call',
                'position': int(table_data['data'][column_name]['normal_text']),
                'lengths_back': convert_lengths_back_string(table_data['data'][column_name]['super_text']),
                'text': column_name,
                'line_index': line_index,
            }
        

        # append object
        objects.append(entry)
    
    # return
    return objects


def parse_fractional_times(line):
    
    # init return
    objects = []
    
    # find fractional times
    if 'Fractional Times:' in line:
        
        # create pattern and extract times
        pattern = r'\b\d+:\d+\.\d+|\b\d+\.\d+'
        fractional_time_array = [convert_string_to_seconds(time_string) for time_string in re.findall(pattern, line['text'])]
        
        # create children
        objects.append({
            'object_type': 'fractional_time',
            'fractional_time_array': fractional_time_array,
        })
    
    # return
    return objects


def parse_extracted_chart_data(extracted_chart_data):

    # init return
    parsed_chart_data = []

    # define parsers
    line_parse_configs = [
        {
            'parser': parse_track_race_date_race_number,
            'output': 'attribute'
        },
        {
            'parser': parse_race_type_name_grade_breed,
            'output': 'attribute'
        },
        {
            'parser': parse_distance_surface_track_record,
            'output': 'attribute'
        },
        {
            'parser': parse_purse,
            'output': 'attribute'
        },
        {
            'parser': parse_fractional_times,
            'output': 'children'
        },
    ]
    table_parse_configs = {
        'entries': {
            'parser': parse_entries,
            'output': 'children'
        },
        'past_performance': {
            'parser': parse_past_performance,
            'output': 'children'
        }
    }

    # iterate through each race
    for extracted_race_data in extracted_chart_data:

        # init return
        parsed_race_data = {
            'object_type':'race',
            'children': []
        }

        # line parsing
        for line_parse_config in line_parse_configs:
            for line in extracted_race_data['lines']:
                if line_parse_config['output'] == 'attribute':
                    parsed_race_data.update(line_parse_config['parser'](line))
                else:
                    parsed_race_data['children'].extend(line_parse_config['parser'](line))

        # table parsing
        for table_name, table_config in table_parse_configs.items():
            if table_name in extracted_race_data['tables']:
                if table_config['output'] == 'children':
                    parsed_race_data['children'].extend(table_config['parser'](extracted_race_data['tables'][table_name]))
                else:
                    parsed_race_data.update(table_config['parser'](extracted_race_data['tables'][table_name]))


        # append data
        parsed_chart_data.append(parsed_race_data)

    # return
    return parsed_chart_data