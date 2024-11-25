"""
Main module for Equibase charts data collection.
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

def get_equibase_chart_files():
    """
    Scrape Equibase chart files for completed races that need chart data.
    
    Looks for races that:
    - Happened at least one day ago
    - Don't have chart data imported yet (equibase_chart_import=False)
    """
    # Calculate cutoff date (yesterday)
    cutoff_date = timezone.now().date() - timedelta(days=1)
    
    # Query races with the given conditions
    races = Races.objects.filter(
        equibase_chart_import=False,
        race_date__lt=cutoff_date
    ).values_list('track__code', 'track__country', 'race_date').distinct()

    # Process each race
    for track_code, track_country, race_date in races:
        # Prepare file info
        url_to_scrape = (
            f'https://www.equibase.com/premium/eqbPDFChartPlus.cfm'
            f'?RACE=A&BorP=P&TID={track_code}&CTRY={track_country}'
            f'&DT={race_date.strftime("%m/%d/%Y")}&DAY=D&STYLE=EQB'
        )
        filename = f'EQB_CHART_{track_code}_{race_date.strftime("%Y%m%d")}.pdf'
        chart_full_filename = SCRAPING_FOLDER / filename

        # Check if file already exists
        if not chart_full_filename.exists():
            try:
                logger.info('Scraping chart for %s on %s', track_code, race_date)
                scrape_url_zenrows(url_to_scrape, filename)
                logger.info('Successfully scraped chart to %s', filename)
            except Exception as e:
                logger.error(
                    'Failed to scrape chart for %s on %s: %s',
                    track_code, race_date, e
                )
        else:
            logger.info(
                'Not scraping chart for %s on %s - file already exists',
                track_code, race_date
            )
