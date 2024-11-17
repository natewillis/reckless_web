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
        
        # breed should always be there
        breed_text = match.group(10)

        # get grade if its there
        grade = None
        race_name = None
        black_type = None
        if match.group(5):
            grade = int(match.group(5))
            black_type = match.group(4)
            race_name = match.group(3)
        elif match.group(6):
            race_name = match.group(6)
        elif match.group(9):
            race_name = match.group(9)
        print(match.group(0))
        print(f'race_name: {race_name}, black: {black_type}, grade: {grade}')
        

        


    
    # return
    return data

def parse_extracted_chart_data(extracted_chart_data):

    # init return
    parsed_chart_data = []

    # define parsers
    line_parsers = [
        lambda line: parse_track_race_date_race_number(line),
        lambda line: parse_race_type_name_grade_breed(line),
    ]
    table_parsers = {

    }

    # iterate through each race
    for extracted_race_data in extracted_chart_data:

        # init return
        parsed_race_data = {}

        # line parsing
        for line_parser in line_parsers:
            parsed_race_data.update(line_parser(extracted_race_data['text']))

        # table parsing
        for table_name, table_parser in table_parsers.items():
            if table_name in extracted_race_data:
                parsed_race_data[table_name] = table_parser[table_name](extracted_race_data[table_name])

        # append data
        parsed_chart_data.append(parsed_race_data)

    # return
    return parsed_chart_data

