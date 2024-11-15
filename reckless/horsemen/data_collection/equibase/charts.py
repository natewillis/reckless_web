import pdfplumber 
import logging
import re
from collections import OrderedDict
from datetime import datetime
from django.core.exceptions import ValidationError
from fuzzywuzzy import process
from horsemen.data_collection.utils import SCRAPING_FOLDER, get_best_choice_from_description_code, \
    convert_string_to_furlongs, convert_string_to_seconds, convert_lengths_back_string, \
    get_point_of_call_object_from_furlongs, get_fractional_time_object_from_furlongs
from horsemen.models import Races, Tracks, Entries, Horses, PointsOfCall, FractionalTimes
from horsemen.data_collection.scraping import scrape_url_zenrows

# init logging
logger = logging.getLogger(__name__)

def get_equibase_chart_pdfs():
    
    # init ordered dict
    track_date_set = OrderedDict()
    
    # get races
    for race in Races.objects.order_by('-race_date'):
        for entry in race.entries_set.all():
            horse = entry.horse
            for horse_race in Races.objects.filter(
                    entry__horse=horse,
                    equibase_chart_import=False
                ).order_by('-race_date'):
                
                # create tuple
                track_date_tuple = (horse_race.track, horse_race.race_date)
                
                # store in dict
                if track_date_tuple not in track_date_set:
                    track_date_set[track_date_tuple] = True
    
    for track_date_tuple in list(track_date_set.keys()):
        
        # split the tuple
        track, race_date = track_date_tuple

        # create pdf url
        pdf_url = track.get_equibase_chart_url_for_date(race_date)
        filename = f'EQB_CHART_{track.code}_{race_date.strftime('%Y%m%d')}.pdf'
        pdf_full_filename = SCRAPING_FOLDER / filename

        # verify it isnt already there
        if not pdf_full_filename.exists():
            logger.info(f'in get_equibase_chart_pdfs, scraping {pdf_url}')
        
            # get pdf
            scrape_url_zenrows(pdf_url, filename)


def get_text_with_spaces(line):

    # init return
    return_text = ''

    # loop chars
    last_x1 = line['chars'][0]['x1']
    for char in line['chars']:
        if char['x0']-last_x1 > 1:
            return_text += ' '
        return_text += char['text']
        last_x1 = char['x1']

    # return
    return return_text

def get_header_info(line):
    header_chars = line['chars']
    last_x1 = header_chars[0]['x1']
    start_x0 = header_chars[0]['x0']
    label = ''
    header_positions = {}
    header_order = []
    for char in header_chars:

        # seems to be the spacing between columns
        if char['x0'] - last_x1 > 4:

            # store data
            header_positions[label] = start_x0
            header_order.append(label)

            # reset for next column
            start_x0 = char['x0']
            label = ''

        # append to label
        label += char['text'].upper()
        last_x1 = char['x1']

    # finish last entry
    header_positions[label] = start_x0
    header_order.append(label)
    # custom overrides
    if 'POOL' in header_order:
        header_positions['POOL'] = header_positions['POOL']-30

    return header_order, header_positions

def get_table_values_from_line(header_order, header_positions, line):

    # init return
    return_dict = {}
    for label in header_order:
        return_dict[label] = {
            'normal_text': '',
            'super_text': ''
        }

    # init loop
    current_header_index = 0
    current_header = header_order[current_header_index]
    end_x0 = header_positions[header_order[current_header_index+1]]
    font_y0 = line['chars'][0]['y0']
    last_x1 = line['chars'][0]['x0']
    for char in line['chars']:

        # check if we crossed a header boundry
        while char['x0'] >= end_x0-1:

            # increment the header
            current_header_index += 1
            current_header = header_order[current_header_index]
            
            # if we're at the end of the headers, set the line end to something huge
            if current_header_index+1 >= len(header_order):
                end_x0 = 100000
            else:
                end_x0 = header_positions[header_order[current_header_index+1]]

            # set last_x1 so that we dont put a space at the beginning of a new column
            last_x1 = char['x0']

        # check if there needs to be a space
        char_to_append = char['text'].upper()
        if char['x0']-last_x1 > 1:
            char_to_append = ' ' + char_to_append

        # check if the character is normal or super
        if char['y0']>font_y0+1:
            return_dict[current_header]['super_text'] += char_to_append
        else:
            return_dict[current_header]['normal_text'] += char_to_append

        # set last x1 to find spaces
        last_x1 = char['x1']

    return return_dict


def get_race_info(page):

    # init return dict
    race_info = {}

    # get page line coords
    lines = page.extract_text_lines()
    lines = [line for line in lines if len(line['text'])>4]

    # Join the words to form the full line
    first_line_data = get_text_with_spaces(lines[0]).split(' - ')

    # check the structure
    if not len(first_line_data) == 3:
        return race_info
    if 'Race' not in first_line_data[2]:
        return race_info

    # store track, date, and race
    race_info['track'] = first_line_data[0].strip().upper()
    race_info['date'] = datetime.strptime(first_line_data[1], '%B %d, %Y')
    race_info['race'] = int(first_line_data[2].replace('Race ', ''))

    # race type
    second_line_data = get_text_with_spaces(lines[1]).split(' - ')
    race_info['race_type'] = get_best_choice_from_description_code(second_line_data[0],Races.EQUIBASE_RACE_TYPE_CHOICES)
    race_info['horse_type'] = get_best_choice_from_description_code(second_line_data[1],Races.BREED_CHOICES)

    # age/sex
    # TODO: manually specify the OPEN restrictions
    current_line = 2
    general_race_data = []
    while 'Distance:' not in lines[current_line] and current_line < 6:
        general_race_data.append(get_text_with_spaces(lines[current_line]))
        current_line += 1
    general_race_line = ' '.join(general_race_data)
    
    open_sex = True
    for sex_type in ['FILLIES', 'MARES', 'COLTS', 'GELDINGS']:
        if sex_type in general_race_line.split('.')[0]:
            open_sex = False
    race_info['sex_restriction'] = 'O' if open_sex else get_best_choice_from_description_code(general_race_line.split('.')[0],Races.DRF_SEX_RESTRICTION_CHOICES)
    race_info['age_restriction'] = get_best_choice_from_description_code(general_race_line.split('.')[0],Races.DRF_AGE_RESTRICTION_CHOICES)


    # search for things without spaces
    race_info_table = False
    past_performance_table_minus_1 = False
    past_performance_table = False
    header_order = []
    header_positions = {}
    for line in lines:

        # Single line work
        line_text = get_text_with_spaces(line)

        # distance/surface
        if 'Distance:' in line_text and ' On The ' in line_text:
            distance_type_string = get_text_with_spaces(line).split('Current')[0].replace('Distance:','').strip()
            race_info['distance']=convert_string_to_furlongs(distance_type_string.split(' On The ')[0])
            race_info['surface']='D' if 'DIRT' in distance_type_string.split(' On The ')[1].strip().upper() else 'T'

        # purse
        if 'Purse: $' in line_text:
            pattern = r'\$\d{1,3}(?:,\d{3})*'
            match = re.search(pattern, line_text)
            if match:
                race_info['purse'] = int(match.group(0).replace('$', '').replace(',', ''))

        # weather/ Track
        if 'Weather: ' in line_text:
            race_info['weather']=line_text.replace('Weather: ','').split('Track:')[0]
            race_info['condition']=line_text.split('Track:')[1].upper().strip()


        ##### TABLE WORK #####
        # fractional times
        if 'FractionalTimes:' in line['text']:
            race_info_table = False # first line after race info table
            pattern = r'\b\d+:\d+\.\d+|\b\d+\.\d+'
            race_info['fractional_times'] = [convert_string_to_seconds(time_string) for time_string in re.findall(pattern, line['text'])]

        # end past performance
        if 'Trainers:' in line['text']:
            past_performance_table = False

        # a new past performance line
        if past_performance_table:

            # parse values into dict
            value_dict = get_table_values_from_line(header_order, header_positions, line)
            if value_dict['PGM']['normal_text'] == '':
                continue
            # parse dict into return
            program_number = value_dict['PGM']['normal_text'].strip().upper()
            race_info['entries'][program_number]['points_of_call'] = {}
            for label in header_order:
                if label == 'PGM' or label =='HORSENAME':
                    continue
                if not value_dict[label]['normal_text'].strip().isnumeric():
                    continue
                race_info['entries'][program_number]['points_of_call'][label] = {
                    'position': int(value_dict[label]['normal_text']),
                    'lengths_back': 0 if value_dict[label]['super_text']=='' else convert_lengths_back_string(value_dict[label]['super_text']),
                    'point_of_call': label
                }

        # a new race info line
        if race_info_table:

            # parse values into dict
            value_dict = get_table_values_from_line(header_order, header_positions, line)
            if value_dict['FIN']['normal_text'] == '':
                race_info_table = False
                continue

            # parse dict into return
            program_number = value_dict['PGM']['normal_text'].strip().upper()
            race_info['entries'][program_number]={'program_number': program_number}

            # horsename
            horse_jockey_text = value_dict['HORSENAME(JOCKEY)']['normal_text'].strip()
            pattern = r'^[^(]+'
            match = re.match(pattern, horse_jockey_text)
            if match:
                race_info['entries'][program_number]['horse_name'] = match.group(0).strip().upper()

            # PP
            race_info['entries'][program_number]['post_position']=int(value_dict['PP']['normal_text'].strip())

            # Odds
            odds_text = value_dict['ODDS']['normal_text'].strip().replace('*','')
            try:
                race_info['entries'][program_number]['odds']=float(odds_text)
            except ValueError:
                pass

            # Comments
            race_info['entries'][program_number]['comments']=value_dict['COMMENTS']['normal_text'].strip()

        
        # header of race info table
        if 'LastRaced' in line['text']:
            race_info_table = True
            header_order, header_positions = get_header_info(line)
            race_info['entries'] = {}

        # header of past performance table
        if past_performance_table_minus_1:
            if 'HorseName' in line['text']:
                past_performance_table = True
                past_performance_table_minus_1 = False
                header_order, header_positions = get_header_info(line)
        if 'PastPerformanceRunningLinePreview' in line['text']:
            past_performance_table_minus_1 = True
            
    # return variable
    return race_info

def store_race_info_in_table(race_info):
    
    # get track
    track = Tracks.objects.filter(name=race_info['track']).first()
    if track is None:

        # logging
        logger.info(f'in store_race_info_in_table, {race_info["track"]} doesnt match existing tracks')

        # Retrieve all track names from the database
        track_names = list(Tracks.objects.values_list('name', flat=True))

        # Use fuzzywuzzy to find the closest match
        closest_match, match_score = process.extractOne(race_info['track'], track_names)
        
        # Check if the match score meets the threshold
        if match_score >= 80:
            track = Tracks.objects.filter(name=closest_match).first()
        else:
            logger.error(f'in store_race_info_in_table, {race_info["track"]} doesnt match existing tracks with fuzzywuzzy')
            return
        
    # get race
    race, created = Races.objects.update_or_create(
        track=track,
        race_date=race_info['date'],
        race_number=race_info['race'],
    )
    if not race.drf_entries_import and not race.drf_results_import:
        race.age_restriction = race_info['age_restriction']
        race.sex_restriction = race_info['sex_restriction']
        race.distance = race_info['distance']
        race.race_surface = race_info['surface']
        race.purse = race_info['purse']
        race.breed = race_info['horse_type']
        race.condition = race_info['condition']
    elif not race.drf_results_import:
        race.condition = race_info['condition']
    race.equibase_chart_import = True
    try:
        race.save()
    except ValidationError as e:
        logger.error(f'in store_race_info_in_table, failed to save race due to {e.error_list}')
        return
    
    # fractional times
    fractional_time_object = get_fractional_time_object_from_furlongs(race.distance)
    fractional_time_data = race_info.get('fractional_times', [])
    if fractional_time_object and len(fractional_time_data) == len(fractional_time_object['fractionals']):
        for index, fractional_time in enumerate(fractional_time_data):
            FractionalTimes.objects.get_or_create(
                race=race,
                point=fractional_time_object['fractionals'][index]['point'],
                defaults={
                    'text': fractional_time_object['fractionals'][index].get('text',''),
                    'distance': fractional_time_object['fractionals'][index].get('feet',0)/660,
                    'time': fractional_time
                }
            )
    else:
        if race.distance > 2.5 and race.breed == 'TB':
            if fractional_time_object and len(fractional_time_data) > 0:
                logger.error(f'in store_race_info_in_table, the number of ractional times ({len(fractional_time_data)}) are wrong compared to the object ({len(fractional_time_object['fractionals'])}) for race distance of {race.distance*660}!')
            elif not fractional_time_object:
                logger.warning(f'no fractional object for race distance of {race.distance}')
    
    # go through entries
    for entry_data in race_info['entries'].values():

        # see if you can find an existing entry first
        entry = Entries.objects.filter(
            race=race,
            program_number=entry_data['program_number']
        ).first()

        # retrieve it through the horse if we dont have a program nubmer, create if it truly doesnt exist
        if not entry:
            horse, created = Horses.objects.get_or_create(
                horse_name=entry_data['horse_name']
            )
            entry, created = Entries.objects.get_or_create(
                race=race,
                horse=horse,
                defaults={
                    'program_number': entry_data['program_number'],
                    'post_position': entry_data['post_position']
                }
            )

        # race comment
        if entry.comment is None:
            entry.comment = entry_data['comments']
            try:
                entry.save()
            except ValidationError as e:
                logger.error(f'in store_race_info_in_table, failed to save entry due to {e.error_list}')
                continue
        
        # points of call
        point_of_call_object = get_point_of_call_object_from_furlongs(race.distance)
        points_of_call = entry_data.get('points_of_call', [])
        if point_of_call_object and len(points_of_call) == len(point_of_call_object['calls']):
            for index, point_of_call_data in enumerate(points_of_call.values()):
                PointsOfCall.objects.get_or_create(
                    entry=entry,
                    point=point_of_call_object['calls'][index]['point'],
                    defaults = {
                        'distance': point_of_call_object['calls'][index].get('feet',0)/660,
                        'position': point_of_call_data['position'],
                        'lengths_back': point_of_call_data['lengths_back'],
                        'text': point_of_call_object['calls'][index]['text']
                    }
                )
        else:
            if race.distance > 2.5 and race.breed == 'TB':
                if point_of_call_object and len(points_of_call) > 0:
                    logger.error(f'in store_race_info_in_table, the number of points of call ({len(points_of_call)}) are wrong compared to the object ({len(point_of_call_object['calls'])}) for race distance of {race.distance*660}!')
                elif not point_of_call_object:
                    logger.warning(f'no points of call object for race distance of {race.distance}')
        

        
          
    
    
    
def parse_equibase_chart(filename):

    print(f'parsing {filename}')
    pdf = pdfplumber.open(filename) 

    for page in pdf.pages:

        # start checking for race information
        race_info = get_race_info(page)

        # if this is the second page or something, continue
        if not race_info:
            continue

        # store data
        store_race_info_in_table(race_info=race_info)

    pdf.close