"""
Main module for Equibase horse results data collection.
Handles file scraping and data extraction coordination.
"""

import logging
from datetime import datetime
from pathlib import Path
from django.utils import timezone
from horsemen.models import Horses
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.scraping import scrape_url_zenrows

# Configure logging
logger = logging.getLogger(__name__)

def get_horse_results_files():
    """
    Scrape Equibase horse results files for horses that need results data.
    """
    # Find horses whose entries haven't been scraped in horse_results
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
        logger.info('Scraping results for %s', horse.horse_name)

        # Create horse url
        horse_result_url = horse.get_equibase_horse_results_url()
        if not horse_result_url:
            logger.error('Could not generate URL for %s', horse.horse_name)
            continue

        # Prepare filename
        horse_filename = (
            f'EQB_HORSERESULTS_{horse.equibase_horse_id}_'
            f'{datetime.now().strftime("%Y%m%d")}.html'
        )
        horse_full_filename = SCRAPING_FOLDER / horse_filename

        # Check if file already exists
        if not horse_full_filename.exists():
            logger.info('Scraping %s to %s', horse_result_url, horse_filename)
            scrape_url_zenrows(horse_result_url, horse_filename)
        else:
            logger.info('%s already scraped!', horse_filename)