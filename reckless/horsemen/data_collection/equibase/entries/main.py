"""
Main module for Equibase entries data collection.
Handles file scraping and data extraction coordination.
"""

import logging
from datetime import datetime
from django.utils import timezone
from django.db.models import Q
from horsemen.models import Races, Horses, Entries
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.scraping import scrape_url_zenrows

# Configure logging
logger = logging.getLogger(__name__)

def get_equibase_entries_files():
    """
    Scrape Equibase entries files for future races with horses missing equibase IDs.
    """
    # Get future races with horses missing equibase IDs
    races = Races.objects.filter(
        race_date__gt=timezone.now().date(),
        entries__horse__equibase_horse_id__isnull=True
    ).distinct()

    # Process each race
    for race in races:
        # Prepare file info
        url_to_scrape = (
            f'https://www.equibase.com/static/entry/'
            f'{race.track.code}{race.race_date.strftime("%m%d%y")}'
            f'{race.track.country}-EQB.html'
        )
        filename = f'EQB_ENTRIES_{race.track.code}_{race.race_date.strftime("%Y%m%d")}.html'
        entries_full_filename = SCRAPING_FOLDER / filename

        # Check if file already exists
        if not entries_full_filename.exists():
            logger.info('Scraping %s to %s', url_to_scrape, filename)
            scrape_url_zenrows(url_to_scrape, filename)
        else:
            logger.info('Not scraping %s because %s exists!', url_to_scrape, filename)
