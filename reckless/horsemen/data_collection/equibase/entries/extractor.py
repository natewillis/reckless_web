"""
Extractor module for Equibase entries data.
Handles extraction of raw data from HTML entries pages.
"""

import logging
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class EquibaseEntriesExtractor:
    def __init__(self, filename: Path):
        """
        Initialize with a filename.
        
        Args:
            filename: Path to the HTML file to parse
        """
        logger.info('Initializing EquibaseEntriesExtractor with %s', filename)
        self.filename = filename
        self.data = []

    def to_json(self):
        """Save extracted data to a JSON file."""
        json_filename = self.filename.with_suffix('.json')
        with open(json_filename, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)

    def parse(self):
        """
        Parse the HTML file and extract entries information.
        """
        logger.info('EquibaseEntriesExtractor parsing %s', self.filename)

        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract track info
            track_data = self._extract_track_info(soup)
            if not track_data:
                logger.error('Failed to extract track information')
                return

            # Extract race date
            race_date = self._extract_race_date(soup)
            if not race_date:
                logger.error('Failed to extract race date')
                return

            # Process each race
            for race_div in soup.find_all('div', class_='entryRace'):
                race_data = self._extract_race_data(race_div, track_data, race_date)
                if race_data:
                    self.data.append(race_data)


            logger.info('Successfully parsed %d races', len(self.data))

        except Exception as e:
            logger.error('Error parsing entries file: %s', e)
            raise

    def _extract_track_info(self, soup):
        """Extract track information from the page."""
        try:
            track_url_tag = soup.find('a', class_='track-name')
            if not track_url_tag or 'href' not in track_url_tag.attrs:
                return None

            track_url = track_url_tag['href']
            match = re.search(r"trk=([A-Za-z0-9]+)", track_url)
            if not match:
                return None

            return {
                'code': match.group(1),
                'name': track_url_tag.text.strip()
            }

        except Exception as e:
            logger.error('Error extracting track info: %s', e)
            return None

    def _extract_race_date(self, soup):
        """Extract race date from the page."""
        try:
            date_div = soup.find('div', class_='race-date')
            if not date_div:
                return None

            return datetime.strptime(date_div.text.strip(), "%B %d, %Y").date()

        except Exception as e:
            logger.error('Error extracting race date: %s', e)
            return None

    def _extract_race_data(self, race_div, track_data, race_date):
        """Extract data for a single race."""
        try:
            # Get race number
            strong_tag = race_div.find('strong')
            if not strong_tag:
                return None

            race_number = int(strong_tag.text.strip().replace('Race ', ''))

            # Initialize race data
            race_data = {
                'track': {
                    'object_type': 'track',
                    'code': track_data['code'],
                    'name': track_data['name']
                },
                'race_date': race_date,
                'race_number': race_number,
                'entries': []
            }
            # Process header
            entry_header_data = self._extract_entry_header_data(race_div.select_one('table.fullwidth tr'))

            # Process each entry
            for horse_row in race_div.select('table.fullwidth tr'):
                entry_data = self._extract_entry_data(horse_row, entry_header_data)
                if entry_data:
                    race_data['entries'].append(entry_data)
            return race_data

        except Exception as e:
            logger.error('Error extracting race data: %s', e)
            return None
        
    def _extract_entry_header_data(self, horse_row):
        """Extract data for the header rows"""

        # Get all cells
        cells = horse_row.find_all('th')
        if not cells:
            return None
        return [cell.get_text().strip().upper() for cell in cells]


    def _extract_entry_data(self, horse_row,  header_data):
        """Extract data for a single entry."""
        try:
            # Skip "Also Eligibles" rows
            if 'Also Eligibles:' in horse_row.get_text():
                return None

            # Get all cells
            cells = horse_row.find_all('td')
            if not cells:
                return None
            
            # Get horse link
            # check for scratch
            scratch_flag = False
            if cells[0].get_text().upper().strip() == "SCR":
                scratch_flag = True
                horse_cell = cells[1]
            else:
                horse_cell = cells[header_data.index('HORSE')]
            horse_link = horse_cell.find('a')
            if not horse_link:
                return None

            # Extract horse info
            horse_data = self._extract_horse_info(horse_link)
            if not horse_data:
                return None
            
            # init return object
            return_data = {
                'object_type': 'entry',
                'horse': horse_data,
            }
            
            # Extract program number
            program_number = None
            if 'P#' in header_data and not scratch_flag:
                program_number = cells[header_data.index('P#')].get_text().strip().upper()
                return_data['program_number'] = program_number

            # things for non scratched horses
            if not scratch_flag:

                # Extract connections
                jockey_cell = cells[header_data.index('JOCKEY')]
                jockey_link = jockey_cell.find('a')
                if jockey_link:
                    jockey_data = self._extract_connection_info(jockey_link, 'jockey')
                    return_data['jockey'] = jockey_data

                trainer_cell = cells[header_data.index('TRAINER')]
                trainer_link = trainer_cell.find('a')
                if trainer_link:
                    trainer_data = self._extract_connection_info(trainer_link, 'trainer')
                    return_data['trainer'] = trainer_data

            return return_data

        except Exception as e:
            logger.error('Error extracting entry data: %s', e)
            return None

    def _extract_horse_info(self, horse_link):
        """Extract horse information from link."""
        try:
            horse_url = horse_link['href']
            pattern = r'refno=(\d+).*?®istry=([A-Z])&rbt=([A-Z]{2})'
            match = re.search(pattern, horse_url)
            if not match:
                return None

            # Parse horse name and state
            horse_text = horse_link.get_text().strip().upper()
            horse_text = re.sub(r'^(.*?\(.*?\).*?)\s*\(.*?\)(.*)$', r'\1\2', horse_text)
            name_match = re.match(r"^(.+?)(?:\s*\((\w{2,3})\))?$", horse_text)
            if not name_match:
                return None

            return {
                'object_type': 'horse',
                'horse_name': name_match.group(1).strip(),
                'equibase_horse_id': int(match.group(1)),
                'equibase_horse_registry': match.group(2),
                'equibase_horse_type': match.group(3),
                'horse_state_or_country': name_match.group(2) if name_match.group(2) else None
            }

        except Exception as e:
            logger.error('Error extracting horse info: %s', e)
            return None

    def _extract_connection_info(self, link, connection_type):
        """Extract jockey or trainer information from link."""
        try:
            url = link['href']
            pattern = r'ID=(\d+)&rbt=([A-Z]{2})'
            match = re.search(pattern, url)
            if not match:
                return None

            # Parse name
            name_text = link.get_text().strip()
            if name_text == '':
                return None
            # remove extra spaces
            name_text = re.sub(r'\s+', ' ', name_text)

            # split by spaces
            split_name = name_text.split(' ')

            # init return
            first_initial_array = []
            last_name = ''
            for name_part in split_name:
                if len(name_part) == 1 and last_name == '':
                    first_initial_array.append(name_part)
                elif re.match(r'[A-Z][a-z\,\-]+$', name_part):
                    last_name += name_part
                else:
                    last_name += ' ' + name_part
 
            return {
                'object_type': connection_type,
                f'equibase_{connection_type}_id': int(match.group(1)),
                f'equibase_{connection_type}_type': match.group(2),
                'last_name': last_name.strip().upper(),
                'first_initials': ' '.join(first_initial_array).strip().upper()
            }


        except Exception as e:
            logger.error('Error extracting %s info from (%s): %s', connection_type, link, e)
            return None

def parse_equibase_entries(filename: Path, debug: bool = False) -> list:
    """
    Parse Equibase entries HTML file.
    
    Args:
        filename: Path to the HTML file
        debug: If True, save extracted data to JSON file
        
    Returns:
        List of extracted race data
    """
    logger.info('parse_equibase_entries called for %s', filename)

    extractor = EquibaseEntriesExtractor(filename)
    extractor.parse()

    if debug:
        extractor.to_json()

    return extractor.data
