"""
Main module for Equibase horse results data collection.
Handles file scraping and data extraction coordination.
"""

import logging
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from horsemen.models import Horses, Entries
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.scraping import scrape_url_zenrows

# Configure logging
logger = logging.getLogger(__name__)

def get_horse_results_files():
    """
    Scrape Equibase horse results files for horses with past entries needing results data.
    """
    # Find horses that have entries in past races needing results data
    horses = Horses.objects.filter(
        Q(entries__equibase_horse_results_import=False) & 
        Q(entries__race__race_date__lt=timezone.now().date()),
        equibase_horse_id__isnull=False
    ).distinct()
    
    for horse in horses:
        logger.info('Scraping results for %s', horse.horse_name)

        # Get horse URL
        horse_result_url = horse.get_equibase_horse_results_url()
        if not horse_result_url:
            logger.error('Could not generate URL for %s - missing equibase info', horse.horse_name)
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
