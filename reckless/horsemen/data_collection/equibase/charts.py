import pdfplumber 
import re
from datetime import datetime

def get_line_coordinates(page, debug=False):

    # Initialize list for line coordinates
    line_coords = []

    # Extract words and group by y-coordinates to approximate lines
    lines = page.extract_text_lines()
    for line in lines:

        # validate its a real line
        if line['text'] == '?':
            continue

        y_start = line['top']
        y_end = line['bottom']
        
        # Append line coordinates based on bounding box
        line_coords.append({
            'y_start': y_start,
            'y_end': y_end,
            'text': line['text']
        })

    return line_coords


def get_line_text(page, y_start, y_end):

    words_in_line = []
    
    # Iterate over each text block in the page
    for block in page.get_text("dict")["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    # Get the bounding box of the word (span)
                    rect = span["bbox"]
                    word_y_middle = (rect[1] + rect[3]) / 2  # Average y-coordinates to get middle
                    
                    # Check if the word is within the specified y_start and y_end
                    if y_start < word_y_middle < y_end:
                        words_in_line.append(span["text"])
    
    # Join all collected words in the y-coordinate range
    line_text = " ".join(words_in_line)
    return line_text  # Returns the concatenated line or empty string if none found

def get_header_info(line):

    header_chars = line['chars']
    last_x0 = header_chars[0]['x0']
    start_x0 = last_x0
    label = ''
    header_positions = {}
    header_order = []
    for char in header_chars:
        if char['x0'] - last_x0 > 9:
            header_positions[label] = start_x0
            header_order.append(label)
            start_x0 = char['x0']
            label = ''
        label += char['text']
        last_x0 = char['x0']
    
    return header_order, header_positions

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
            distance_type_string = line['text'].split('Current')[0].replace('Distance:','')
            race_info['distance']=distance_type_string.split('OnThe')[0]
            race_info['surface']=distance_type_string.split('OnThe')[1]

        # purse
        if 'Purse:$' in line_text:
            pattern = r'\$\d{1,3}(?:,\d{3})*'
            match = re.search(pattern, line_text)
            if match:
                race_info['purse'] = int(match.group(0).replace('$', '').replace(',', ''))

        # weather/ Track
        if 'Weather:' in line_text:
            race_info['weather']=line_text.replace('Weather:','').split('Track:')[0]
            race_info['condition']=line_text.split('Track:')[1]

    # search for things without spaces
    race_info_table = False
    header_order = []
    header_positions = {}
    for line in lines:

        # fractional times
        if 'FractionalTimes:' in line['text']:
            race_info_table = False # first line after race info table
            pattern = r'\b\d+:\d+\.\d+|\b\d+\.\d+'
            race_info['times'] = re.findall(pattern, line['text'])

        # a new race info line
        if race_info_table:
            cur_pgm = ''
            for label_count, label in enumerate(header_order):
                font_height = 0
                font_y0 = 0
                normal_text = ''
                super_text = ''
                start_x = header_positions[label]
                last_x1 = line['chars'][0]['x1']
                if label_count + 1 >= len(header_order):
                    end_x = 1000000
                else:
                    end_x = header_positions[header_order[label_count+1]]

                for char in line['chars']:
                    if font_height == 0:
                        font_height = char['y1'] - char['y0']
                        font_y0 = char['y0']
                    if char['x0']<end_x-1:
                        if char['x0']>=start_x-1:
                            if char['y0']>font_y0+1:
                                super_text += char['text']
                            else:
                                if char['x0']-last_x1 > 1:
                                    normal_text += ' '
                                normal_text += char['text']
                    else:
                        if label == 'Pgm':
                            cur_pgm = normal_text.upper()
                            race_info['entries'][cur_pgm]={}
                        if label == 'HorseName(Jockey)':
                            horse_jockey_text = normal_text.upper()
                            pattern = r'^[^(]+'
                            match = re.match(pattern, horse_jockey_text)
                            if match:
                                race_info['entries'][cur_pgm]['horse_name'] = match.group(0).strip()
                        if label == 'PP':
                            race_info['entries'][cur_pgm]['post_position']=int(normal_text)
                    last_x1 = char['x1']


        # header of race info table
        if 'LastRaced' in line['text']:
            race_info_table = True
            header_order, header_positions = get_header_info(line)
            race_info['entries'] = {}
            print(header_order)
            

    # return variable
    return race_info
    
def parse_equibase_chart(filename):

    pdf = pdfplumber.open(filename) 

    for page in pdf.pages:

        # start checking for race information
        race_info = get_race_info(page)

        # if this is the second page or something, continue
        if not race_info:
            continue

        print(get_race_info(page))

    pdf.close