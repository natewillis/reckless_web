import requests
import logging
from datetime import datetime
import pytz

# init logging
logger = logging.getLogger(__name__)

def fetch_tracks_data():

    logger.info('running fetch_tracks_data')

    # get data from url
    url = "https://formulator.drf.com/formulator-service/api/raceTracks"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return {}



def parse_extracted_tracks_data(extracted_tracks_data):

    # init return
    parsed_track_data = []

    # loop through tracks
    for track_data in extracted_tracks_data.get('allTracks', []):

        # create track object
        track = {
            'object_type': 'track',
            'code': track_data['trackId'],
            'name': track_data['trackName'],
            'country': track_data['country']
        }

        # iterate through card and race to create track item
        for race_card in track_data.get('cards',[]):
            for race_number in race_card.get("raceList", []):
                parsed_track_data.append({
                    'object_type': 'race',
                    'track': track,
                    'race_date': datetime.fromtimestamp(race_card["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date(),
                    'race_number': race_number,
                    'day_evening': race_card.get('dayEvening', 'D'),
                    'drf_tracks_import': True
                })

    # return
    return parsed_track_data


