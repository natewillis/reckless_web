import requests
from datetime import datetime
from django.utils import timezone
from horsemen.models import Tracks, Races
import pytz

def get_drf_tracks():

    # get data from url
    url = "https://formulator.drf.com/formulator-service/api/raceTracks"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    
        for track_info in data.get("allTracks", []):
            # Create or update Track
            track, created = Tracks.objects.update_or_create(
                code=track_info['trackId'],
                defaults={
                    'name': track_info['trackName'],
                    'country': track_info['country'],
                    'equibase_chart_name': track_info['trackName'].replace(' ','').lower(),
                }
            )

            for race_card in track_info.get("cards", []):
                race_date = datetime.fromtimestamp(race_card["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()
                
                for race_number in race_card.get("raceList", []):
                    # Create Races entries
                    Races.objects.update_or_create(
                        track=track,
                        race_date=race_date,
                        race_number=race_number,
                        defaults={
                            'drf_tracks_import': True,
                            'day_evening': race_card.get("dayEvening", 'D'),
                            'final': race_card.get("final", False)
                        }
                    )
    else:
        # Handle HTTP response errors
        print(f"Failed to fetch data. Status code: {response.status_code}")
