
from bs4 import BeautifulSoup
import logging
import re
from django.core.exceptions import ValidationError
from horsemen.models import Entries, Races, Horses
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.scraping import scrape_url_zenrows
from datetime import datetime, timedelta

# init logging
logger = logging.getLogger(__name__)


def get_equibase_entries_files():

    # Querying races with the given conditions
    races = Races.objects.filter(
        drf_entries_import=True,
        equibase_entries_import=False,
        race_date__gt=datetime.now() - timedelta(days=7),
        race_date__lt=datetime.now() + timedelta(days=5)
    ).values_list('track__code', 'track__country', 'race_date').distinct()

    # Convert result to a list of tuples (track code, race date)
    for track_code, track_country, race_date in races:

        # prep args
        url_to_scrape = f'https://www.equibase.com/static/entry/{track_code}{race_date.strftime('%m%d%y')}{track_country}-EQB.html'
        filename = f'EQB_ENTRIES_{track_code}_{race_date.strftime('%Y%m%d')}.html'
        entries_full_filename = SCRAPING_FOLDER / filename
        

        # verify it isnt already there
        if not entries_full_filename.exists():
            
            # logging
            logger.info(f'in get_equibase_entries_files, scraping {url_to_scrape} to {filename}')

            # save file
            scrape_url_zenrows(url_to_scrape,filename)
            
        else:
            
            # logging
            logger.info(f'in get_equibase_entries_files, not scraping {url_to_scrape} because {filename} exists!')


def parse_equibase_entry_url(html_content):

    # Parse html
    soup = BeautifulSoup(html_content, 'html.parser')

    # get track
    track_url_tag = soup.find('a', class_='track-name')
    track_url = track_url_tag['href']
    match = re.search(r"trk=([A-Za-z0-9]+)", track_url)
    if match:
        track_code = match.group(1)
        logger.info(f'in parse_equibase_entry_url, track code is {track_code}')
    else:
        logger.error('in parse_equibase_entry_url, track code not found in html')
        return False
    
    # get date
    date_text = soup.find('div', class_='race-date').text
    race_date = datetime.strptime(date_text, "%B %d, %Y").date()

    # Parse each races div
    for single_race_div in soup.find_all('div', class_='entryRace'):

        # Race number
        strong_tag = single_race_div.find('strong')
        if not strong_tag:
            continue
        race_number = int(strong_tag.text.strip().replace('Race ', ''))

        for horse_row in single_race_div.select('div.race-info table.fullwidth tr'):

            # get rid of bad lines
            if 'Also Eligibles:' in horse_row.get_text():
                    continue
            
            # Split into cells
            horse_cells = horse_row.find_all('td')
            
            # Ignore header
            if len(horse_cells) == 0:
                continue

            # Horse link
            horse_link_tag = horse_row.find('a')

            # Equibase data parsing
            horse_url = horse_link_tag['href']
            pattern = r'refno=(\d+).*?®istry=([A-Z])&rbt=([A-Z]{2})'
            match = re.search(pattern, horse_url)
            if not match:
                logger.error('in parse_equibase_entry_url, couldnt find horse_url')
                continue
            equibase_horse_id = int(match.group(1))
            equibase_horse_registry = match.group(2)
            equibase_horse_type = match.group(3)

            # Horse name parsing
            horse_name_and_state = horse_link_tag.get_text().strip().upper()
            match = re.match(r"^(.+?)(?:\s*\((\w{2,3})\))?$", horse_name_and_state)
            if match:
                horse_name = match.group(1).strip()
                state_or_country = match.group(2)
            else:
                horse_name = horse_name_and_state
                state_or_country = None
            if horse_name == '':
                logger.error('in parse_equibase_entry_url, couldnt find horse name')
                continue
            
            # Program number or (SCR)
            program_number = horse_cells[0].get_text().upper().strip()
            if program_number == '':
                logger.error('in parse_equibase_entry_url, couldnt find program number')
                continue
            
            # check if we can get the horse by id first
            entry = None
            horse = Horses.objects.filter(equibase_horse_id=equibase_horse_id).first()
            
            # update the horse equibase id
            if not horse:
                
                # get entry
                if program_number == 'SCR':
                    # by horse name if scratched
                    entry = Entries.objects.filter(race__track__code=track_code, race__race_date=race_date, race__race_number=race_number, horse__horse_name=horse_name).first()
                else:
                    # by program number
                    entry = Entries.objects.filter(race__track__code=track_code, race__race_date=race_date, race__race_number=race_number, program_number=program_number).first()
                if not entry:
                    logger.error(f'in parse_equibase_entry_url, couldnt find entry from horse_name {horse_name} and program number {program_number}')
                    continue
                
                # get horse
                horse = entry.horse
                
                # Update Horse
                horse.equibase_horse_id = equibase_horse_id
                horse.equibase_horse_type = equibase_horse_type
                horse.equibase_horse_registry = equibase_horse_registry
                horse.horse_state_or_country = state_or_country
                try:
                    horse.save()
                except ValidationError as e:
                    logger.error(f'in parse_equibase_entry_url, failed to save horse due to {e.error_list}')
                    return
            else:
                entry = Entries.objects.filter(race__track__code=track_code, race__race_date=race_date, race__race_number=race_number, horse=horse).first()

            # TBA complicates everything
            if ' TBA' in horse_row.get_text():
                logger.warning('in parse_equibase_entry_url, found TBA in horse row')
                continue
            if len(horse_row.find_all('a')) < 3:
                logger.warning('in parse_equibase_entry_url, not enough hrefs found for trainer/jockey')
                continue
            if not entry:
                logger.error('in parse_equibase_entry_url, no entry found')
                
            if entry.jockey and not entry.jockey.equibase_jockey_id:

                # Jockey
                jockey_link_tag = horse_row.find_all('a')[1]
                jockey_url = jockey_link_tag['href']
                pattern = r'ID=(\d+)&rbt=([A-Z]{2})'
                match = re.search(pattern, jockey_url)
                if match:
                    equibase_jockey_id = int(match.group(1))
                    equibase_jockey_type = match.group(2)

                    # Update Jockey
                    jockey = entry.jockey
                    jockey.equibase_jockey_id = equibase_jockey_id
                    jockey.equibase_jockey_type = equibase_jockey_type
                    try:
                        jockey.save()
                    except ValidationError as e:
                        logger.error(f'in parse_equibase_entry_url, failed to save jockey due to {e.error_list}')
                        continue
                else:
                    logger.error('in parse_equibase_entry_url, failed to save jockey due to lack of jocky href')
                    
            if entry.trainer and not entry.trainer.equibase_trainer_id:
                
                # Trainer
                trainer_link_tag = horse_row.find_all('a')[2]
                trainer_url = trainer_link_tag['href']
                pattern = r'ID=(\d+)&rbt=([A-Z]{2})'
                match = re.search(pattern, trainer_url)
                if match:
                    equibase_trainer_id = int(match.group(1))
                    equibase_trainer_type = match.group(2)

                    # Update Trainer
                    trainer = entry.trainer
                    trainer.equibase_trainer_id = equibase_trainer_id
                    trainer.equibase_trainer_type = equibase_trainer_type
                    try:
                        trainer.save()
                    except ValidationError as e:
                        logger.error(f'in parse_equibase_entry_url, failed to save trainer due to {e.error_list}')
                        continue

        # this race is done
        race = Races.objects.get(track__code=track_code, race_number=race_number, race_date=race_date)
        race.equibase_entries_import = True
        race.save()

            
            
