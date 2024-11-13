import pdfplumber 
import re
from datetime import datetime
from horsemen.data_collection.utils import SCRAPING_FOLDER, convert_string_to_furlongs, convert_string_to_seconds, convert_lengths_back_string_to_furlongs
from horsemen.models import Races
from horsemen.data_collection.scraping import scrape_url_zenrows

def get_equibase_chart_pdfs():

    # query
    distinct_track_dates = Races.objects.filter(eqb_chart_import=False).values('track__code', 'track__country', 'race_date').distinct()

    for track_date in distinct_track_dates:

        # split dict
        track_code = track_date['track__code']
        track_country = track_date['track__country']
        race_date = track_date['race_date']

        # create pdf url
        pdf_url = f'https://www.equibase.com/premium/eqbPDFChartPlus.cfm?RACE=A&BorP=P&TID={track_code}&CTRY={track_country}&DT={race_date.strftime('%m/%d/%Y')}&DAY=D&STYLE=EQB'
        filename = f'EQB_CHART_{track_code}_{race_date.strftime('%Y%m%d')}.pdf'
        pdf_full_filename = SCRAPING_FOLDER / filename

        # verify it isnt already there
        if not pdf_full_filename.exists():
            print(f'scraping {pdf_url}')
        
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
    first_line_data = lines[0]['text'].replace(' ','').split('-')

    # check the structure
    if not len(first_line_data) == 3:
        return race_info
    if not 'Race' in first_line_data[2]:
        return race_info

    # store track, date, and race
    race_info['track'] = first_line_data[0]
    race_info['date'] = datetime.strptime(first_line_data[1], '%B%d,%Y')
    race_info['race'] = int(first_line_data[2].replace('Race', ''))

    # race type
    second_line_data = lines[1]['text'].replace(' ','').split('-')
    race_info['race_type'] = second_line_data[0]
    race_info['horse_type'] = second_line_data[1]

    # age/sex
    third_line_text = lines[2]['text']
    if '.' not in third_line_text:
        third_line_text += lines[3]['text']
    race_info['age_sex_restrictions'] = third_line_text.split('.')[0]

    # search for things
    for line in lines:

        # remove spaces though this should be done
        line_text = line['text'].replace(' ','')

        # distance/surface
        if 'Distance:' in line_text and 'OnThe' in line_text:
            distance_type_string = get_text_with_spaces(line).split('Current')[0].replace('Distance:','').strip()
            race_info['distance']=convert_string_to_furlongs(distance_type_string.split(' On The ')[0])
            race_info['surface']=distance_type_string.split(' On The ')[1].strip()

        # purse
        if 'Purse:$' in line_text:
            pattern = r'\$\d{1,3}(?:,\d{3})*'
            match = re.search(pattern, line_text)
            if match:
                race_info['purse'] = int(match.group(0).replace('$', '').replace(',', ''))

        # weather/ Track
        if 'Weather:' in line_text:
            race_info['weather']=line_text.replace('Weather:','').split('Track:')[0]
            race_info['condition']=line_text.split('Track:')[1].upper().strip()

    # search for things without spaces
    race_info_table = False
    past_performance_table_minus_1 = False
    past_performance_table = False
    header_order = []
    header_positions = {}
    for line in lines:

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
            program_number = value_dict['PGM']['normal_text'].strip()
            race_info['entries'][program_number]['points_of_call'] = {}
            for label in header_order:
                if label == 'PGM' or label =='HORSENAME':
                    continue
                if not value_dict[label]['normal_text'].strip().isnumeric():
                    continue
                race_info['entries'][program_number]['points_of_call'][label] = {
                    'position': int(value_dict[label]['normal_text']),
                    'lengths_back': 0 if value_dict[label]['super_text']=='' else convert_lengths_back_string_to_furlongs(value_dict[label]['super_text']),
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
            program_number = value_dict['PGM']['normal_text'].strip()
            race_info['entries'][program_number]={'program_number': program_number}

            # horsename
            horse_jockey_text = value_dict['HORSENAME(JOCKEY)']['normal_text'].strip()
            pattern = r'^[^(]+'
            match = re.match(pattern, horse_jockey_text)
            if match:
                race_info['entries'][program_number]['horse_name'] = match.group(0).strip()

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
    
def parse_equibase_chart(filename):

    print(f'parsing {filename}')
    pdf = pdfplumber.open(filename) 

    for page in pdf.pages:

        # start checking for race information
        race_info = get_race_info(page)

        # if this is the second page or something, continue
        if not race_info:
            continue

        print(get_race_info(page))

    pdf.close