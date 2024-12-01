import pdfplumber
import logging
import re
import json

# Configure logging
logger = logging.getLogger(__name__)

# precompile regex
page_type_pattern = re.compile(r'([A-Z0-9\s&]+)\s?-\s?(.+?)\s?-\s?Race\s?(\d+)')

# parsing lines into normal lines
def get_text_with_spaces(line):

    # init return
    return_text = ''

    # loop chars
    last_x1 = line['chars'][0]['x1']
    for char in line['chars']:
        if char['x0']-last_x1 > 1.5:
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
        if char['x0'] - last_x1 > 4 or label == 'WGT':

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


class EquibaseChartExtractor:
    def __init__(self, filename):
        """
        Initialize with a filename.
        """
        logger.info(f'intializing EquibaseChartParser with {filename}')
        self.filename = filename
        self.data = []

    def to_json(self):

        # rename the filename to have json at the end
        json_filename = self.filename.with_suffix('.json')

        # write the file
        with open(json_filename, 'w') as json_file:
            json.dump(self.data, json_file, indent=4) 

    def parse(self):
        """
        Parse the file and extract race information.
        """
        logger.info(f'EquibaseChartParser parsing {self.filename}')

        # init lines
        plumber_lines = []

        # parse pdf
        with pdfplumber.open(self.filename) as pdf:

            # loop through pages and extract lines
            
            for page in pdf.pages:

                # extract lines
                extracted_lines = page.extract_text_lines()

                # check what kind of page this is
                if page_type_pattern.search(extracted_lines[0]['text']):
                    # this is the first page of a race
                    plumber_lines.append(extracted_lines)
                else:
                    # this is the second page of race, hopefully
                    if len(plumber_lines)>0:
                        plumber_lines[-1].extend(extracted_lines)

            logger.info(f'{self.filename} has {len(pdf.pages)} pdf pages but {len(plumber_lines)} races')
            pdf.close()

        # process lines
        for extracted_lines in plumber_lines:

            # init data storage
            data = {
                'lines': [],
                'tables': {}
            }

            # configure tables
            table_configs = [
                {
                    'header_pattern': r'Wager\s*Type\s*Winning\s*Numbers',
                    'stop_pattern': r'Past\s*Performance',
                    'table_name': 'payoffs'
                },
                {
                    'header_pattern': r'Last\s*Raced\s*Pgm',
                    'stop_pattern': r'(?:Fractional\s*Times|Run\s*-?\s*Up|Winner)',
                    'table_name': 'entries'
                },
                {
                    'header_pattern': r'Horse\s*Name\s*(Start|1|2)',
                    'stop_pattern': r'(?:Trainers:|Owners:)',
                    'table_name': 'past_performance'
                }
            ]

            # process lines
            table = None
            active_table_config = None
            for line in extracted_lines:

                # table processing vs line processing
                if table:
                    # table processing
                    # check if this is the end of the table
                    if re.match(active_table_config['stop_pattern'], line['text']):
                        data['tables'][active_table_config['table_name']] = table
                        table = None
                        active_table_config = None
                    else:
                        # process table row
                        table['data'].append(get_table_values_from_line(table['header_order'], table['header_positions'], line))

                # check for table headers
                if not table:
                    for table_config in table_configs:
                        if re.search(table_config['header_pattern'], line['text']):

                            # load config
                            active_table_config = table_config

                            # parse header
                            header_order, header_positions = get_header_info(line=line)

                            # init table data
                            table = {
                                'header_order': header_order,
                                'header_positions': header_positions,
                                'data': []
                            }

                            # dont search anymore
                            break

                # after all the table stuff, if were not dealing with it append the line
                if not table:
                    #line processing
                    stripped_line = get_text_with_spaces(line).strip()
                    pattern = r'([\w\s]+:)|(Footnotes)'
                    if len(data['lines'])==0 or re.match(pattern, stripped_line):
                        data['lines'].append(stripped_line)
                    else:
                        data['lines'][-1] += ' ' + stripped_line

            # append to data
            self.data.append(data)

            # log
            logger.info(f'parsed {len(data['tables'])} tables and {len(data['lines'])} lines')

# main extraction sub
def parse_equibase_chart(filename, debug=False):

    # logging
    logger.info(f'parse_equibase_charts called for {filename}')

    # init the parser
    extractor = EquibaseChartExtractor(filename)
    
    # parse data
    extractor.parse()

    # if debug, output json
    if debug:
        extractor.to_json()

    # return extracted data
    return extractor.data


