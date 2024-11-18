import logging
import re
import json
from datetime import datetime

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
            'track_name': match.group(1).strip().upper(),
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


def parse_extracted_chart_data(extracted_chart_data):

    # init return
    parsed_chart_data = []

    # define parsers
    line_parsers = [
        lambda line: parse_track_race_date_race_number(line),
        lambda line: parse_race_type_name_grade_breed(line),
        lambda line: parse_distance_surface_track_record(line),
        lambda line: parse_purse(line),
    ]
    table_parsers = {

    }

    # iterate through each race
    for extracted_race_data in extracted_chart_data:

        # init return
        parsed_race_data = {'object_type':'race'}

        # line parsing
        for line_parser in line_parsers:
            for line in extracted_race_data['lines']:
                parsed_race_data.update(line_parser(line))

        # table parsing
        for table_name, table_parser in table_parsers.items():
            if table_name in extracted_race_data:
                parsed_race_data[table_name] = table_parser[table_name](extracted_race_data[table_name])
        print(parsed_race_data)

        # append data
        parsed_chart_data.append(parsed_race_data)

    # return
    return parsed_chart_data

