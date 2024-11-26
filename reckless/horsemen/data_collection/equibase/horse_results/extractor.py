"""
Extractor module for Equibase horse results data.
Handles extraction of raw data from HTML horse results pages.
"""

import logging
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, Any, Optional
from horsemen.data_collection.utils import convert_string_to_furlongs, convert_string_to_seconds

# Configure logging
logger = logging.getLogger(__name__)

class EquibaseHorseResultsExtractor:
    def __init__(self, filename: Path):
        """
        Initialize with a filename.
        
        Args:
            filename: Path to the HTML file to parse
        """
        logger.info('Initializing EquibaseHorseResultsExtractor with %s', filename)
        self.filename = filename
        self.data = {
            'horse': None,
            'entries': [],
            'workouts': [],
            'results': []
        }

    def to_json(self):
        """Save extracted data to a JSON file."""
        json_filename = self.filename.with_suffix('.json')
        with open(json_filename, 'w') as json_file:
            json.dump(self.data, json_file, indent=4)

    def parse(self):
        """
        Parse the HTML file and extract horse results information.
        """
        logger.info('EquibaseHorseResultsExtractor parsing %s', self.filename)

        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract horse info
            horse_data = self._extract_horse_info(soup)
            if not horse_data:
                logger.error('Failed to extract horse information')
                return
            self.data['horse'] = horse_data

            # Extract entries
            entries_div = soup.find('div', id='entries')
            if entries_div:
                self.data['entries'] = self._extract_entries(entries_div)

            # Extract workouts
            workouts_div = soup.find('div', id='workouts')
            if workouts_div:
                self.data['workouts'] = self._extract_workouts(workouts_div)

            # Extract results
            results_div = soup.find('div', id='results')
            if results_div:
                self.data['results'] = self._extract_results(results_div)

            logger.info('Successfully parsed horse results data')

        except Exception as e:
            logger.error('Error parsing horse results file: %s', e)
            raise

    def _extract_horse_info(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract horse identification information."""
        try:
            # Try checkbox method first
            horse_id_checkbox = soup.find('input', id='addCompare')
            if horse_id_checkbox:
                return {
                    'equibase_horse_id': int(horse_id_checkbox['data-comid']),
                    'horse_name': horse_id_checkbox['data-comname'].upper().strip(),
                    'equibase_horse_type': horse_id_checkbox['data-comrbt'].upper().strip(),
                    'equibase_horse_registry': horse_id_checkbox['data-comreg'].upper().strip()
                }

            # Try link method as fallback
            link = soup.find('a', href=re.compile(r'refno=\d+'), class_="green-borderbutton")
            if link:
                href = link['href']
                refno_match = re.search(r'refno=(\d+)', href)
                if refno_match:
                    return {
                        'equibase_horse_id': int(refno_match.group(1))
                    }

            return None

        except Exception as e:
            logger.error('Error extracting horse info: %s', e)
            return None

    def _extract_entries(self, entries_div: BeautifulSoup) -> list:
        """Extract entries information."""
        entries = []
        try:
            for row in entries_div.find_all('tr'):
                if len(row.find_all('td')) == 0:
                    continue

                track_cell = row.find('td', class_='track')
                if not track_cell or not track_cell.find('a'):
                    continue

                track_url = track_cell.find('a')['href']
                pattern = r'trk=([A-Z]{2,3}).*?cy=([A-Z]{2,3})'
                match = re.search(pattern, track_url)
                
                if match:
                    entries.append({
                        'track_code': match.group(1),
                        'track_country': match.group(2),
                        'race_date': datetime.strptime(
                            row.find('td', class_='date').get_text().strip(),
                            "%m/%d/%Y"
                        ).date(),
                        'race_number': int(row.find('td', class_='race').get_text().strip()),
                    })

            return entries

        except Exception as e:
            logger.error('Error extracting entries: %s', e)
            return []

    def _extract_workouts(self, workouts_div: BeautifulSoup) -> list:
        """Extract workout information."""
        workouts = []
        try:
            for row in workouts_div.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 0:
                    continue

                track_cell = cells[0]
                if not track_cell.find('a'):
                    continue

                track_url = track_cell.find('a')['href']
                pattern = r'trk=([A-Z]{2,3}).*?cy=([A-Z]{2,3})'
                match = re.search(pattern, track_url)
                
                if match:
                    date_text = row.find('td', {'data-label': 'Date'}).get_text().strip()
                    distance_text = row.find('td', {'data-label': 'Distance'}).get_text().strip()
                    surface_text = row.find('td', {'data-label': 'Course'}).get_text().strip()
                    time_text = row.find('td', {'data-label': 'Time'}).get_text().strip()
                    rank_text = row.find('td', {'data-label': 'Rank'}).get_text().strip()
                    
                    rank_parts = rank_text.split('/')
                    rank = int(rank_parts[0]) if len(rank_parts) == 2 else 0
                    rank_total = int(rank_parts[1]) if len(rank_parts) == 2 else 0

                    workouts.append({
                        'track_code': match.group(1),
                        'track_country': match.group(2),
                        'workout_date': datetime.strptime(date_text, "%m/%d/%Y").date(),
                        'distance': convert_string_to_furlongs(distance_text),
                        'surface': 'D' if 'DIRT' in surface_text.upper() else 'T',
                        'time_seconds': convert_string_to_seconds(time_text),
                        'note': row.find('td', {'data-label': 'Note'}).get_text().strip().upper(),
                        'workout_rank': rank,
                        'workout_total': rank_total
                    })

            return workouts

        except Exception as e:
            logger.error('Error extracting workouts: %s', e)
            return []

    def _extract_results(self, results_div: BeautifulSoup) -> list:
        """Extract race results information."""
        results = []
        try:
            for row in results_div.find_all('tr'):
                if len(row.find_all('td')) == 0:
                    continue

                chart_cell = row.find('td', class_='chart')
                if not chart_cell or not chart_cell.find('a'):
                    continue

                chart_url = chart_cell.find('a')['href']
                pattern = r'track=([A-Z]{2,3}).*?raceDate=(\d{2}/\d{2}/\d{4}).*?cy=([A-Z]{3}).*?rn=(\d+)'
                match = re.search(pattern, chart_url)
                
                if match:
                    speed_cell = row.find('td', class_='speedFigure')
                    speed_text = speed_cell.get_text().strip() if speed_cell else ''
                    speed_rating = int(speed_text) if speed_text.isnumeric() else None

                    results.append({
                        'track_code': match.group(1),
                        'track_country': match.group(3),
                        'race_date': datetime.strptime(match.group(2), "%m/%d/%Y").date(),
                        'race_number': int(match.group(4)),
                        'speed_rating': speed_rating
                    })

            return results

        except Exception as e:
            logger.error('Error extracting results: %s', e)
            return []

def parse_equibase_horse_results(filename: Path, debug: bool = False) -> Dict[str, Any]:
    """
    Parse Equibase horse results HTML file.
    
    Args:
        filename: Path to the HTML file
        debug: If True, save extracted data to JSON file
        
    Returns:
        Dictionary containing extracted horse results data
    """
    logger.info('parse_equibase_horse_results called for %s', filename)

    extractor = EquibaseHorseResultsExtractor(filename)
    extractor.parse()

    if debug:
        extractor.to_json()

    return extractor.data
