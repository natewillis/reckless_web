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

# Configure logging
logger = logging.getLogger(__name__)

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

        elif 'HORSERESULTS' in file_path.name:
            extracted_data = parse_equibase_horse_results(file_path)
            objects_to_load = parse_extracted_horse_results_data(extracted_data)
            process_parsed_objects(objects_to_load)
            #file_path.rename(processed_folder / file_path.name)

        elif 'CHART' in file_path.name and '.pdf' in file_path.name:
            extracted_data = parse_equibase_chart(file_path, True)
            objects_to_load = parse_extracted_chart_data(extracted_data)
            process_parsed_objects(objects_to_load)
            try:
                file_path.rename(processed_folder / file_path.name)
            except PermissionError as p:
                logger.error('Could not delete %s due to permission error %s', file_path.name, p)

def parse_equibase_files_by_type(file_type):
    """Parse specific type of Equibase files from the scraping folder."""
    processed_folder = SCRAPING_FOLDER / 'processed'
    processed_folder.mkdir(exist_ok=True)

    for file_path in SCRAPING_FOLDER.iterdir():
        if not file_path.is_file() or 'EQB' not in file_path.name:
            continue

        if file_type in file_path.name:
            logger.info('Processing %s from %s', file_path.name, file_path)
            
            if file_type == 'ENTRIES':
                extracted_data = parse_equibase_entries(file_path)
                objects_to_load = parse_extracted_entries_data(extracted_data)
            elif file_type == 'HORSERESULTS':
                extracted_data = parse_equibase_horse_results(file_path)
                objects_to_load = parse_extracted_horse_results_data(extracted_data)
            elif file_type == 'CHART' and '.pdf' in file_path.name:
                extracted_data = parse_equibase_chart(file_path, True)
                objects_to_load = parse_extracted_chart_data(extracted_data)
            else:
                continue

            process_parsed_objects(objects_to_load)

            # Move processed files to processed folder
            if file_type == 'CHART':
                try:
                    file_path.rename(processed_folder / file_path.name)
                except PermissionError as p:
                    logger.error('Could not delete %s due to permission error %s', file_path.name, p)

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
    logger.info("Step 2: Collecting and processing Equibase entries...")
    get_equibase_entries_files()
    parse_equibase_files_by_type('ENTRIES')

    # Step 3: Get all horse results HTMLs, then process them
    logger.info("Step 3: Collecting and processing horse results...")
    get_horse_results_files()
    parse_equibase_files_by_type('HORSERESULTS')

    # Step 4: Get all charts, then process them
    logger.info("Step 4: Collecting and processing charts...")
    get_equibase_chart_files()
    parse_equibase_files_by_type('CHART')

    logger.info("Sequential data collection completed.")
