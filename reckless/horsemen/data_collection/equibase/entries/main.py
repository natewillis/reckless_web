"""
Main module for Equibase entries data collection.
Handles file scraping and data extraction coordination.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from django.utils import timezone
from horsemen.models import Races
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.scraping import scrape_url_zenrows

# Configure logging
logger = logging.getLogger(__name__)

def get_equibase_entries_files():
    """
    Scrape Equibase entries files for races that need entries data.
    """
    # Query races with the given conditions
    races = Races.objects.filter(
        drf_entries_import=True,
        equibase_entries_import=False,
        race_date__gt=datetime.now() - timedelta(days=7),
        race_date__lt=datetime.now() + timedelta(days=5)
    ).values_list('track__code', 'track__country', 'race_date').distinct()

    # Process each race
    for track_code, track_country, race_date in races:
        # Prepare file info
        url_to_scrape = (
            f'https://www.equibase.com/static/entry/'
            f'{track_code}{race_date.strftime("%m%d%y")}{track_country}-EQB.html'
        )
        filename = f'EQB_ENTRIES_{track_code}_{race_date.strftime("%Y%m%d")}.html'
        entries_full_filename = SCRAPING_FOLDER / filename

        # Check if file already exists
        if not entries_full_filename.exists():
            logger.info('Scraping %s to %s', url_to_scrape, filename)
            scrape_url_zenrows(url_to_scrape, filename)
        else:
            logger.info('Not scraping %s because %s exists!', url_to_scrape, filename)
