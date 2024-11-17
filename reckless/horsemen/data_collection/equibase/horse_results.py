
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime
from horsemen.data_collection.scraping import scrape_url_zenrows
from horsemen.data_collection.utils import SCRAPING_FOLDER, convert_string_to_furlongs, convert_string_to_seconds
from horsemen.models import Tracks, Races, Entries, Horses, Workouts
from django.core.exceptions import ValidationError
from django.utils import timezone


# init logging
logger = logging.getLogger(__name__)


def get_horse_results_files():

    # find horses whos entries havent been scraped in horse_results
    horses_future_races = Horses.objects.filter(
        entries__equibase_horse_results_import=False,
        entries__race__race_date__gte=timezone.now().date()
    ).distinct()

    horses_past_races = Horses.objects.filter(
        entries__equibase_horse_results_import=False,
        entries__race__race_date__lt=timezone.now().date()
    ).distinct()

    horses = horses_past_races.union(horses_future_races)
    
    for horse in horses:
        
        # logging
        logger.info(f'in get_horse_results_files, scraping {horse.horse_name}')

        # create horse url
        horse_result_url = horse.get_equibase_horse_results_url()
        horse_filename = f'EQB_HORSERESULTS_{horse.equibase_horse_id}_{datetime.now().strftime('%Y%m%d')}.html'
        horse_full_filename = SCRAPING_FOLDER / horse_filename

        # validate url
        if horse_result_url == '':
            logger.error(f'in get_horse_results_files, {horse.horse_name} couldnt generate a url')
            continue

        # verify it isnt already there
        if not horse_full_filename.exists():

            # grab html at url
            scrape_url_zenrows(horse_result_url, horse_filename)

        else:

            logger.info(f'{horse_filename} already scraped!')

def parse_equibase_horse_results_history(html_content):

    # parse html
    soup = BeautifulSoup(html_content, 'html.parser')

    # find the equibase horse id
    horse_id_checkbox = soup.find('input', id='addCompare')
    horse = None
    if horse_id_checkbox:
        horse_id = int(horse_id_checkbox['data-comid'])
        horse_name = horse_id_checkbox['data-comname'].upper().strip()
        horse_type = horse_id_checkbox['data-comrbt'].upper().strip()
        horse_registry = horse_id_checkbox['data-comreg'].upper().strip()
        horse = Horses.objects.filter(equibase_horse_id=horse_id).first()
        if not horse:
            horse, created = Horses.objects.update_or_create(
                horse_name=horse_name,
                defaults={
                    'equibase_horse_id': horse_id,
                    'equibase_horse_type': horse_type,
                    'equibase_horse_registry': horse_registry,
                }
            )

    else:

        # Use regex to match the href pattern with any refno value
        link = soup.find('a', href=re.compile(r'refno=\d+'), class_="green-borderbutton")

        # Extract the refno from the href if the link is found
        if link:
            href = link['href']
            refno_match = re.search(r'refno=(\d+)', href)
            horse_id = int(refno_match.group(1)) if refno_match else None
            if horse_id:
                horse = Horses.objects.filter(equibase_horse_id=horse_id).first()

    if not horse:
        logger.error(f'in parse_equibase_horse_results_history, horse not found {horse_id_checkbox}')
        return

    # Find the div with id="entries"
    entries_div = soup.find('div', id='entries')
    if entries_div:
        
        # parse results rows
        for entries_row in entries_div.find_all('tr'):
            
            # ignore header
            if len(entries_row.find_all('td')) == 0:
                continue

            # race data
            track_url = entries_row.find('td', class_='track').find('a')['href']
            pattern = r'trk=([A-Z]{2,3}).*?cy=([A-Z]{2,3})'
            match = re.search(pattern, track_url)
            if match:
                track_code = match.group(1)
                track_country = match.group(2)

                race_date = datetime.strptime(entries_row.find('td', class_='date').get_text().strip(), "%m/%d/%Y")
                race_number = int(entries_row.find('td', class_='race').get_text().strip())

                # Look up or create the track
                track = Tracks.objects.filter(code=track_code).first()
                if not track:
                    # Handle case where track does not exist in the database
                    logger.error(f"in parse_equibase_horse_results_history, track with code {track_code} not found.")
                    continue  # Skip this entry if track does not exist

                # Create or update the race entry
                try:
                    race, created = Races.objects.update_or_create(
                        track=track,
                        race_date=race_date,
                        race_number=race_number,
                    )
                except ValidationError as e:
                    logger.error(f'in parse_equibase_horse_results_history, failed to save race due to {e.message_dict}')
                    return

                try:
                    entry, created = Entries.objects.update_or_create(
                        race=race,
                        horse=horse, defaults={
                            'equibase_horse_entries_import': True
                        }
                    )
                except ValidationError as e:
                    logger.error(f'in parse_equibase_horse_results_history, failed to save entry due to {e.message_dict}')
                    return

    # Find the div with id="entries"
    workout_div = soup.find('div', id='workouts')
    if workout_div:
        
        # parse results rows
        for workout_row in workout_div.find_all('tr'):
            
            # split on td
            workout_cells = workout_row.find_all('td')

            # ignore header
            if len(workout_cells) == 0:
                continue

            # workout data
            if workout_cells[0].find('a'):
                track_url = workout_cells[0].find('a')['href']
                pattern = r'trk=([A-Z]{2,3}).*?cy=([A-Z]{2,3})'
                match = re.search(pattern, track_url)
                if match:
                    track_code = match.group(1)
                    track_country = match.group(2)

                    workout_date = datetime.strptime(workout_row.find('td', {'data-label': 'Date'}).get_text().strip(), "%m/%d/%Y")
                    distance = convert_string_to_furlongs(workout_row.find('td', {'data-label': 'Distance'}).get_text().strip())
                    surface = 'D' if 'DIRT' in workout_row.find('td', {'data-label': 'Course'}).get_text().strip().upper() else 'T'
                    time_seconds = convert_string_to_seconds(workout_row.find('td', {'data-label': 'Time'}).get_text().strip())
                    note = workout_row.find('td', {'data-label': 'Note'}).get_text().strip().upper()
                    rank_string = workout_row.find('td', {'data-label': 'Rank'}).get_text().strip()
                    split_rank_string = rank_string.split('/')
                    if len(split_rank_string) == 2:
                        rank = int(split_rank_string[0])
                        rank_total = int(split_rank_string[1])
                    else:
                        rank = 0
                        rank_total = 0
                        
                    # Look up or create the track
                    track = Tracks.objects.filter(code=track_code).first()
                    if not track:
                        # Handle case where track does not exist in the database
                        logger.error(f"in parse_equibase_horse_results_history, track with code {track_code} not found.")
                        continue  # Skip this entry if track does not exist

                    # write workout
                    # Create or update the race entry
                    try:
                        workout, created = Workouts.objects.update_or_create(
                            track=track,
                            workout_date=workout_date,
                            horse = horse,
                            defaults={
                                'surface': surface,
                                'distance': distance,
                                'time_seconds': time_seconds,
                                'note': note,
                                'workout_rank': rank,
                                'workout_total': rank_total
                            }
                        )
                    except ValidationError as e:
                        logger.error(f'in parse_equibase_horse_results_history, failed to save workout due to {e.message_dict}')
                    


    # Find the div with id="results"
    results_div = soup.find('div', id='results')
    if not results_div:
        logger.info('in parse_equibase_horse_results_history, no results reported')
        return
    
    
    # parse results rows
    for results_row in results_div.find_all('tr'):
        
        # ignore header
        if len(results_row.find_all('td')) == 0:
            continue

        # race data
        chart_url = results_row.find('td', class_='chart').find('a')['href']
        pattern = r'track=([A-Z]{2,3}).*?raceDate=(\d{2}/\d{2}/\d{4}).*?cy=([A-Z]{3}).*?rn=(\d+)'
        match = re.search(pattern, chart_url)
        if match:
            track_code = match.group(1)
            race_date_str = match.group(2)
            race_date = datetime.strptime(race_date_str, "%m/%d/%Y").date()
            race_number = int(match.group(4))

        # speed rating
        speed_rating_text = results_row.find('td', class_='speedFigure')
        speed_rating = None
        if speed_rating_text:
            if speed_rating_text.get_text().strip().isnumeric():
                speed_rating = int(speed_rating_text.get_text().strip())
                
        # Look up or create the track
        track = Tracks.objects.filter(code=track_code).first()
        if not track:
            # Handle case where track does not exist in the database
            logger.error(f"in parse_equibase_horse_results_history, track with code {track_code} not found.")
            continue  # Skip this entry if track does not exist

        # Create or update the race entry
        try:
            race, created = Races.objects.update_or_create(
                track=track,
                race_date=race_date,
                race_number=race_number,
            )
        except ValidationError as e:
            logger.error(f'in parse_equibase_horse_results_history, failed to save race due to {e.message_dict}')
                    
        # create entry for this horse if needed
        try:
            entry, created = Entries.objects.update_or_create(
                race=race,
                horse=horse, defaults={
                    'equibase_speed_rating': speed_rating,
                    'equibase_horse_results_import': True
                }
            )
        except ValidationError as e:
            logger.error(f'in parse_equibase_horse_results_history, failed to save entry due to {e.message_dict}')
            
