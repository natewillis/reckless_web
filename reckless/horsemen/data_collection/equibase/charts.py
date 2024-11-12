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
            race_info['purse'] = int(line_text.replace('Purse:$','').replace(',','').replace('Guaranteed',''))

        # weather/ Track
        if 'Weather:' in line_text:
            race_info['weather']=line_text.replace('Weather:','').split('Track:')[0]
            race_info['condition']=line_text.split('Track:')[1]

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