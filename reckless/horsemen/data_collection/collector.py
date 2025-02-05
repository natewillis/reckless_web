"""
Collector module for coordinating data collection from various sources.
"""

import logging
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.equibase.charts.extractor import parse_equibase_chart
from horsemen.data_collection.equibase.charts.data_parser import parse_extracted_chart_data
from horsemen.data_collection.equibase.charts.main import get_equibase_chart_files
from horsemen.data_collection.equibase.entries.extractor import parse_equibase_entries
from horsemen.data_collection.equibase.entries.data_parser import parse_extracted_entries_data
from horsemen.data_collection.equibase.entries.main import get_equibase_entries_files
from horsemen.data_collection.equibase.horse_results.main import get_horse_results_files
from horsemen.data_collection.equibase.horse_results.extractor import parse_equibase_horse_results
from horsemen.data_collection.equibase.horse_results.data_parser import parse_extracted_horse_results_data
from horsemen.data_collection.drf.tracks.data_parser import fetch_tracks_data
from horsemen.data_collection.drf.entries.data_parser import get_entries_data
from horsemen.data_collection.drf.results.data_parser import get_results_data
from horsemen.data_collection.data_loader import process_parsed_objects
from horsemen.models import Races, Entries, Horses, Tracks
from horsemen.data_collection.scraping import scrape_url_zenrows
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q

# Configure logging
logger = logging.getLogger(__name__)

def command_line_downloader():

    # Run drf first
    drf_run()

    # Get the current date and calculate the range
    current_date = datetime.now().date()
    start_date = current_date - timedelta(days=30)
    end_date = current_date + timedelta(days=30)

    # Step 1: Get the list of tracks with races in the specified date range
    tracks = Tracks.objects.filter(
        Q(races__race_date__gte=start_date, races__race_date__lte=end_date)
    ).distinct()

    # Step 2: Display tracks and prompt user to choose one
    do_them_all = False
    if not tracks.exists():
        print("No tracks with races in the specified date range.")
    else:
        print("Available Tracks:")
        for idx, track in enumerate(tracks, 1):
            print(f"{idx}. {track.name}")
        print(f'{len(tracks)+1}. All')
        
        while True:
            try:
                track_choice = int(input("Select a track by number: "))
                if 1 <= track_choice <= len(tracks):
                    selected_track = tracks[track_choice - 1]
                    break
                elif track_choice == len(tracks)+1:
                    do_them_all = True
                    break
                else:
                    print("Invalid choice. Please choose a valid track number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        
        # Step 3: List race dates for the selected track
        if do_them_all:
            races = Races.objects.filter(
                race_date__gte=start_date, race_date__lte=end_date
            ).order_by('race_date')
        else:
            races = Races.objects.filter(
                track=selected_track, race_date__gte=start_date, race_date__lte=end_date
            ).order_by('race_date')
        
        if not races.exists():
            print("No races available for the selected track in the specified date range.")
        else:
            if do_them_all:
                race_date_track_set = set()

                for race in races:
                    race_date_track_set.add((race.race_date, race.track))

                for race_date, track in race_date_track_set:
                    print(f'processing {track.name} on {race_date}')
                    donwload_and_process_single_race_day(race_date, track)

            else:
                print(f"Available Race Dates for {selected_track.name}:")

                race_date_info = {}

                for idx, race in enumerate(races, 1):

                    # get stats on what needs to be downloaded
                    if race.race_date not in race_date_info:

                        race_date_info[race.race_date] = {
                            'total_entries': 0,
                            'null_id_entries': 0,
                            'results_needed': 0,
                            'charts_needed': 0
                        }
                    
                    # Get entries with null equibase_horse_id
                    null_id_entries = Entries.objects.filter(
                        race=race,
                        horse__equibase_horse_id__isnull=True
                    )
                    race_date_info[race.race_date]['total_entries'] += len(race.entries_set.all())
                    race_date_info[race.race_date]['null_id_entries'] += len(null_id_entries)

                    # Horse results history
                    results_entries = Entries.objects.filter(
                        race=race,
                        equibase_horse_results_import=False,
                        equibase_horse_entries_import=False,
                        horse__equibase_horse_id__isnull=False
                    ).select_related('horse')
                    race_date_info[race.race_date]['results_needed'] += len(results_entries)

                    # get charts
                    # Get all horses in tomorrow's races
                    race_horses = Horses.objects.filter(entries__race=race)
                    
                    # Find their past races needing charts (if this is a race in the past, you can grab the chart for it as well)
                    past_races = Races.objects.filter(
                        entries__horse__in=race_horses,
                        race_date__lt=timezone.now().date(),
                        equibase_chart_import=False
                    ).distinct()
                    race_date_info[race.race_date]['charts_needed'] += len(past_races)

                for idx, prompted_race_date in enumerate(race_date_info.keys(), 1):

                    print(f"{idx}. {prompted_race_date}: {race_date_info[prompted_race_date]['null_id_entries']}/{race_date_info[prompted_race_date]['total_entries']} null eqb ids, {race_date_info[prompted_race_date]['results_needed']} needing results, {race_date_info[prompted_race_date]['charts_needed']} past races needing charts")
                
                print(f'{len(race_date_info.keys())+1}. ALL ')

                # Step 4: Prompt user to select a race date
                race_dates = None
                while True:
                    try:
                        race_choice = int(input("Select a race date by number: "))
                        if race_choice == (len(race_date_info.keys())+1):
                            race_dates = race_date_info.keys()
                            break
                        elif 1 <= race_choice <= len(race_date_info.keys()):
                            race_date = race_date_info.keys()[race_choice - 1]
                            break
                        else:
                            print("Invalid choice. Please choose a valid race date number.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                
                # Step 5: Display the result
                print(f"You selected track: {selected_track.name}")
                if race_dates:
                    print('You selected them all!')
                    for race_date in race_dates:
                        donwload_and_process_single_race_day(race_date, selected_track)
                else:
                    print(f"You selected race date: {race_date}")
                    # process
                    donwload_and_process_single_race_day(race_date, selected_track)

            


def donwload_and_process_single_race_day(race_date, track):

    # get races
    races = Races.objects.filter(
        track=track,
        race_date=race_date
    )

    if not races.exists():
        logger.info('No races found tomorrow or yesterday')
        return
    
    logger.info(f'Found {races.count()} races for {track.name}')

    # Step 1: Get race cards that have horses with null equibase_horse_id
    cards_to_process = set()
    for race in races:
        # Get entries with null equibase_horse_id
        null_id_entries = Entries.objects.filter(
            race=race,
            horse__equibase_horse_id__isnull=True
        )
        all_entries = Entries.objects.filter(
            race=race,
        )
        logger.debug(f'{len(null_id_entries)} null id entries in race out of {len(all_entries)} {race.race_number} at {race.track.name}')
        if len(null_id_entries) > 0 or len(all_entries) == 0:
            filename = f'EQB_ENTRIES_{race.track.code}_{race.race_date.strftime("%Y%m%d")}.html'
            url = race.track.get_equibase_entries_url_for_date(race.race_date)
            cards_to_process.add((url,filename))

    # Download and process equibase entries in order to get equibase horse ids
    for url, filename in cards_to_process:
        logger.info(f'Processing entries: {filename}')
        scrape_url_zenrows(url, filename)
    
    if cards_to_process:
        parse_equibase_files_by_type('ENTRIES')

    # Step 2: Get horse results (results in past for horses in these races) for entries needing them
    horses_needing_results = set()
    logger.info('looking for horse results')
    for race in races:
        entries = Entries.objects.filter(
            race=race,
            equibase_horse_results_import=False,
            equibase_horse_entries_import=False,
            horse__equibase_horse_id__isnull=False
        ).select_related('horse')
        
        for entry in entries:
            logger.debug(f'for results parsing, {entry.horse.horse_name} for race {entry.race.race_number} at {entry.race.track.name} has a results flag of {entry.equibase_horse_results_import} ')
            horses_needing_results.add((entry.horse, entry.race.race_date))

    # Download and process horse results
    for horse, race_date in horses_needing_results:
        url = horse.get_equibase_horse_results_url()
        if url:
            filename = (
                f'EQB_HORSERESULTS_{horse.equibase_horse_id}_'
                f'{race_date.strftime("%Y%m%d")}.html'
            )
            logger.info(f'Processing horse results: {filename}')
            scrape_url_zenrows(url, filename)

    if horses_needing_results:
        parse_equibase_files_by_type('HORSERESULTS')

    # Step 3: Get charts for past races
    charts_to_process = set()
    for race in races:
        # Get all horses in tomorrow's races
        horses = Horses.objects.filter(entries__race=race)
        
        # Find their past races needing charts (if this is a race in the past, you can grab the chart for it as well)
        past_races = Races.objects.filter(
            entries__horse__in=horses,
            race_date__lt=timezone.now().date(),
            equibase_chart_import=False
        ).distinct()

        logger.info(f'found {len(past_races)} past races necessary to fill in past performance for {len(horses)} for race {race.race_number} at {race.track.name} on {race.race_date}')
        
        for past_race in past_races:
            url = past_race.track.get_equibase_chart_url_for_date(past_race.race_date)
            filename = f'EQB_CHART_{past_race.track.code}_{past_race.race_date.strftime("%Y%m%d")}.pdf'
            charts_to_process.add((url, filename))

    # Download and process charts
    for url, filename in charts_to_process:
        logger.info(f'Processing chart: {filename}')
        scrape_url_zenrows(url, filename)

    if charts_to_process:
        parse_equibase_files_by_type('CHART')

    logger.info('Completed downloading and processing all required Equibase files')

    


def download_equibase_files_for_tomorrow_and_yesterday():
    """
    Download and process all required Equibase files for tomorrow's races:
    1. Find horses with null equibase_horse_id and get their past races' entries
    2. Get horse results for entries with equibase_horse_results_import=False
    3. Get charts for past races with equibase_chart_import=False
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    # Get races with a race date from yesterday to tomorrow
    races = Races.objects.filter(
        track__code__in=['AQU', 'SAR', 'CD'],
        race_date__range=[yesterday, tomorrow]
    )
    
    if not races.exists():
        logger.info('No races found tomorrow or yesterday')
        return

    logger.info(f'Found {races.count()} races tomorrow or yesterday')

    # Step 1: Get race cards that have horses with null equibase_horse_id
    cards_to_process = set()
    for race in races:
        # Get entries with null equibase_horse_id
        null_id_entries = Entries.objects.filter(
            race=race,
            horse__equibase_horse_id__isnull=True
        )
        logger.debug(f'{len(null_id_entries)} null id entries in race {race.race_number} at {race.track.name}')
        if len(null_id_entries) > 0:
            filename = f'EQB_ENTRIES_{race.track.code}_{race.race_date.strftime("%Y%m%d")}.html'
            url = race.track.get_equibase_entries_url_for_date(race.race_date)
            cards_to_process.add((url,filename))


    # Download and process entries
    for url, filename in cards_to_process:
        logger.info(f'Processing entries: {filename}')
        scrape_url_zenrows(url, filename)
    
    if cards_to_process:
        parse_equibase_files_by_type('ENTRIES')

    # Step 2: Get horse results for entries needing them
    horses_needing_results = set()
    logger.info('looking for horse results')
    for race in races:
        entries = Entries.objects.filter(
            race=race,
            equibase_horse_results_import=False,
            equibase_horse_entries_import=False,
            horse__equibase_horse_id__isnull=False
        ).select_related('horse')
        
        for entry in entries:
            logger.debug(f'for results parsing, {entry.horse.horse_name} for race {entry.race.race_number} at {entry.race.track.name} has a results flag of {entry.equibase_horse_results_import} ')
            horses_needing_results.add((entry.horse, entry.race.race_date))

    # Download and process horse results
    for horse, race_date in horses_needing_results:
        url = horse.get_equibase_horse_results_url()
        if url:
            filename = (
                f'EQB_HORSERESULTS_{horse.equibase_horse_id}_'
                f'{race_date.strftime("%Y%m%d")}.html'
            )
            logger.info(f'Processing horse results: {filename}')
            scrape_url_zenrows(url, filename)

    if horses_needing_results:
        parse_equibase_files_by_type('HORSERESULTS')

    # Step 3: Get charts for past races
    charts_to_process = set()
    for race in races:
        # Get all horses in tomorrow's races
        horses = Horses.objects.filter(entries__race=race)
        
        # Find their past races needing charts
        past_races = Races.objects.filter(
            entries__horse__in=horses,
            race_date__lt=tomorrow,
            equibase_chart_import=False
        ).distinct()

        logger.info(f'found {len(past_races)} past races necessary to fill in past performance for {len(horses)} for race {race.race_number} at {race.track.name} on {race.race_date}')
        
        for past_race in past_races:
            url = past_race.track.get_equibase_chart_url_for_date(past_race.race_date)
            filename = f'EQB_CHART_{past_race.track.code}_{past_race.race_date.strftime("%Y%m%d")}.pdf'
            charts_to_process.add((url, filename))

    # Download and process charts
    for url, filename in charts_to_process:
        logger.info(f'Processing chart: {filename}')
        scrape_url_zenrows(url, filename)

    if charts_to_process:
        parse_equibase_files_by_type('CHART')

    logger.info('Completed downloading and processing all required Equibase files')

def parse_equibase_files():
    """Parse Equibase files from the scraping folder."""
    # Create processed folder
    processed_folder = SCRAPING_FOLDER / 'processed'
    processed_folder.mkdir(exist_ok=True)

    for file_path in SCRAPING_FOLDER.iterdir():
        logger.info('Processing %s from %s', file_path.name, file_path)
        if not file_path.is_file() or 'EQB' not in file_path.name:
            continue

        if 'ENTRIES' in file_path.name:
            extracted_data = parse_equibase_entries(file_path)
            objects_to_load = parse_extracted_entries_data(extracted_data)
            process_parsed_objects(objects_to_load)
            file_path.rename(processed_folder / file_path.name)

        elif 'HORSERESULTS' in file_path.name:
            extracted_data = parse_equibase_horse_results(file_path)
            objects_to_load = parse_extracted_horse_results_data(extracted_data)
            process_parsed_objects(objects_to_load)
            file_path.rename(processed_folder / file_path.name)

        elif 'CHART' in file_path.name and '.pdf' in file_path.name:
            extracted_data = parse_equibase_chart(file_path, False)
            objects_to_load = parse_extracted_chart_data(extracted_data)
            process_parsed_objects(objects_to_load)
            try:
                file_path.rename(processed_folder / file_path.name)
            except PermissionError as p:
                logger.error('Could not delete %s due to permission error %s', file_path.name, p)

def parse_equibase_files_by_type(file_type, debug_flag = False):
    """Parse specific type of Equibase files from the scraping folder."""
    processed_folder = SCRAPING_FOLDER / 'processed'
    processed_folder.mkdir(exist_ok=True)

    for file_path in SCRAPING_FOLDER.iterdir():

        try:

            if not file_path.is_file() or 'EQB' not in file_path.name:
                continue

            if file_type in file_path.name:
                logger.info('Processing %s from %s', file_path.name, file_path)
                processed = False
                
                if file_type == 'ENTRIES':
                    extracted_data = parse_equibase_entries(file_path)
                    objects_to_load = parse_extracted_entries_data(extracted_data)
                    processed = True
                elif file_type == 'HORSERESULTS':
                    extracted_data = parse_equibase_horse_results(file_path)
                    objects_to_load = parse_extracted_horse_results_data(extracted_data)
                    processed = True
                elif file_type == 'CHART' and '.pdf' in file_path.name:
                    extracted_data = parse_equibase_chart(file_path, debug=debug_flag)
                    objects_to_load = parse_extracted_chart_data(extracted_data)
                    processed = True
                else:
                    continue

                process_parsed_objects(objects_to_load)

                # Move processed files to processed folder
                if processed:
                    try:
                        file_path.rename(processed_folder / file_path.name)
                    except PermissionError as p:
                        logger.error('Could not delete %s due to permission error %s', file_path.name, p)
                    except WindowsError as p:
                        logger.error('Could not delete %s due to windows error %s', file_path.name, p)
        except Exception as e:
            logger.error(f'eror parsing {file_path.name}: {e}')


def drf_run():
    """Run DRF data collection process."""
    # Run tracks
    objects_to_load = fetch_tracks_data()
    process_parsed_objects(objects_to_load)

    # Get entries
    objects_to_load = get_entries_data()
    process_parsed_objects(objects_to_load)

    # Get results
    objects_to_load = get_results_data()
    process_parsed_objects(objects_to_load)

def single_run():
    """Run a single data collection cycle."""
    # Get entries files
    get_equibase_entries_files()
    parse_equibase_files()

    # Get horse results
    get_horse_results_files()
    parse_equibase_files()

    # Get charts for completed races
    get_equibase_chart_files()
    parse_equibase_files()

def collect_all_data_sequentially():
    """
    Run data collection in a specific sequence:
    1. DRF subs first
    2. Get and process equibase entries
    3. Get and process horse results
    4. Get and process charts
    """
    logger.info("Starting sequential data collection...")

    # Step 1: Run all DRF subs first
    logger.info("Step 1: Running DRF data collection...")
    drf_run()

    # Step 2: Get all equibase entries HTMLs, then process them
    logger.info("Step 2: Collecting and processing Equibase files...")
    download_equibase_files_for_tomorrow_and_yesterday()
