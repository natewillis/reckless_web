import os
import csv
import requests
import logging
from bs4 import BeautifulSoup
from datetime import timedelta, timezone
import pytz
from django.db import transaction
from horsemen.models import Tracks

# init logging
logger = logging.getLogger(__name__)

def import_tracks_from_csv(file_path):
    try:
        # Use atomic transaction for batch processing
        with transaction.atomic():
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                
                for row in reader:
                    # Unpack CSV row into variables
                    code, country_code, name, time_zone = row
                    
                    # Set the equibase_chart_name (lowercase, no spaces)
                    equibase_chart_name = name.lower().replace(" ", "")
                    
                    # Prepare data for the track
                    track_data = {
                        "name": name,
                        "time_zone": time_zone,
                        "country": 'USA',
                        "equibase_chart_name": equibase_chart_name,
                    }

                    # Use update_or_create to insert or update
                    Tracks.objects.update_or_create(
                        code=code,
                        defaults=track_data
                    )

        logger.info("Import complete.")
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")

def import_training_centers_from_csv(file_path):
    """
    Import training centers from CSV file into the Tracks model.
    Only creates new entries if they don't exist, preserves existing data.
    CSV format: Track Code,Track Name,Country Code,Time Zone
    """
    try:
        # Skip header row
        header_skipped = False
        
        # Use atomic transaction for batch processing
        with transaction.atomic():
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                
                for row in reader:
                    # Skip header row
                    if not header_skipped:
                        header_skipped = True
                        continue
                        
                    # Unpack CSV row into variables
                    print(row)
                    code, name, country, time_zone = row
                    
                    # Only create if the track doesn't exist
                    if not Tracks.objects.filter(code=code).exists():
                        # Prepare data for the training center
                        track_data = {
                            "name": name,
                            "time_zone": time_zone,
                            "country": country,
                            "code": code
                        }

                        # Create new track
                        track = Tracks.objects.create(**track_data)
                        logger.info(f"Created training center: {track.name}")

        logger.info("Training centers import complete.")
    except Exception as e:
        logger.error(f"Error during training centers import: {str(e)}")

def get_timezone_from_offset(offset):
    # Pacific Time offset is UTC-8, adjust based on offset from Pacific
    utc_offset = timedelta(hours=8 - int(offset))
    for tz in pytz.all_timezones:
        if pytz.timezone(tz).utcoffset(None) == utc_offset:
            return tz
    return 'UTC'  # Default to UTC if no match found

def import_tracks_from_trackmaster():
    # URL of the website you want to retrieve
    url = "https://info.trackmaster.com/thoroughbred/thr_tracks.htm"

    # Send GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Get the HTML content
        html_content = response.text

        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        rows = soup.find_all('tr')[1:]  # Skip the header row

        # Iterate over rows and insert data into Django model
        for row in rows:
            columns = row.find_all('td')
            track_code = columns[0].text.strip().upper()
            state_country = columns[2].text.strip().upper()
            if state_country == '':
                state_country = "USA"
            if len(state_country) == 2:
                state_country = "USA"
            time_zone_offset = columns[3].text.strip().upper()
            track_name = columns[4].text.strip().upper()
            
            # Convert offset to time zone string
            time_zone = get_timezone_from_offset(time_zone_offset)
            
            # Insert into the Django model
            track, created = Tracks.objects.update_or_create(
                code=track_code,
                defaults={
                    'name': track_name,
                    'time_zone': time_zone,
                    'country': state_country,
                }
            )
            if created:
                logger.info(f"Created track: {track}")
            else:
                logger.info(f"Track {track_code} updated.")
        

    else:
        logger.error(f"Failed to retrieve the webpage. Status code: {response.status_code}")
