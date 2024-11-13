import requests
from datetime import datetime
import pytz
from collections import defaultdict
from horsemen.models import Races, Tracks, Horses, Jockeys, Trainers, Entries
from horsemen.data_collection.conversions import drf_breed_word_to_code

def update_all_races_with_drf_entries():
    # Query distinct track, race_date pairs where cancelled is False and final is False
    races_to_update = Races.objects.filter(cancelled=False, final=False).values('track_id', 'race_date').distinct()

    # Create a dictionary to group races by track and date
    races_by_track_date = defaultdict(list)

    for race in races_to_update:
        track_id = race['track_id']
        race_date = race['race_date']
        races_by_track_date[(track_id, race_date)].append(race)

    for (track_id, race_date) in races_by_track_date:
        track = Tracks.objects.get(id=track_id)
        url = f"https://www.drf.com/entries/entryDetails/id/{track.code}/country/{track.country}/date/{race_date.strftime('%m-%d-%Y')}"
        response = requests.get(url)

        if response.status_code == 200:
            race_data = response.json()

            for race_json in race_data.get("races", []):

                # Post time calculations
                try:
                    post_time_local_str = race_json.get("postTime", "")
                    original_tz = pytz.timezone(track.time_zone)
                    post_time_local = datetime.strptime(post_time_local_str, "%I:%M %p")
                    post_time_datetime = datetime.combine(race_date, post_time_local.time())
                    post_time_localized = original_tz.localize(post_time_datetime)
                    post_time_utc = post_time_localized.astimezone(pytz.UTC)
                except (ValueError, TypeError):
                    post_time_utc = None

                # Update or create the race in the database
                race, created = Races.objects.update_or_create(
                    track=track,
                    race_date=race_date,
                    race_number=race_json["raceKey"]["raceNumber"],
                    defaults={
                        'drf_entries_import': True,
                        'post_time': post_time_utc,
                        'age_restriction': race_json.get("ageRestriction", ""),
                        'sex_restiction': "O" if race_json.get("sexRestriction", "") == "" else race_json.get("sexRestriction", ""),
                        'minimum_claiming_price': race_json.get("minClaimPrice", 0),
                        'maximum_claiming_price': race_json.get("maxClaimPrice", 0),
                        'distance': race_json.get("distanceValue", 0) * (8 if race_json.get("distanceUnit", "").upper() == "M" else 1),
                        'purse': race_json.get("purse", 0),
                        'wager_text': race_json.get("wagerText", ""),
                        'breed': drf_breed_word_to_code(race_json.get("breed", "Thoroughbred")),
                        'cancelled': race_json.get("isCancelled", False),
                        'race_surface': race_json.get('courseType', 'D')
                    }
                )

                # Process runners (horses, jockeys, trainers, entries)
                for runner in race_json.get("runners", []):

                    # Sire
                    sire_name_upper = runner['sireName'].strip().upper()
                    if sire_name_upper != '':
                        sire, _ = Horses.objects.update_or_create(
                            horse_name=sire_name_upper
                        )
                    else:
                        sire = None

                    # Dam
                    dam_name_upper = runner['damName'].strip().upper()
                    if dam_name_upper != '':
                        dam, _ = Horses.objects.update_or_create(
                            horse_name=dam_name_upper
                        )
                    else:
                        dam = None

                    # Dam Sire
                    dam_sire_name_upper = runner['damSireName'].strip().upper()
                    if dam_sire_name_upper != '':
                        dam_sire, _ = Horses.objects.update_or_create(
                            horse_name=dam_sire_name_upper
                        )
                    else:
                        dam_sire = None

                    # Handle Horse
                    horse_name_upper = runner['horseName'].strip().upper()
                    horse, _ = Horses.objects.update_or_create(
                        horse_name=horse_name_upper,
                        defaults={
                            'registration_number': runner.get('registrationNumber'),
                            'dam': dam,
                            'sire': sire,
                            'dam_sire': dam_sire
                        }
                    )

                    # Handle Trainer
                    trainer, _ = Trainers.objects.update_or_create(
                        first_name=runner["trainer"]["firstName"].strip().upper(),
                        last_name=runner["trainer"]["lastName"].strip().upper(),
                        defaults={
                            'middle_name': (runner["trainer"]["middleName"] or "").strip().upper(),
                            'drf_trainer_id': runner["trainer"].get("id"),
                            'drf_trainer_type': runner["trainer"].get("type"),
                            'alias': (runner["trainer"].get("alias") or "").strip().upper()
                        }
                    )

                    # Handle Jockey
                    jockey, _ = Jockeys.objects.update_or_create(
                        first_name=runner["jockey"]["firstName"].strip().upper(),
                        last_name=runner["jockey"]["lastName"].strip().upper(),
                        defaults={
                            'middle_name': (runner["jockey"]["middleName"] or "").strip().upper(),
                            'drf_jockey_id': runner["jockey"].get("id"),
                            'drf_jockey_type': runner["jockey"].get("type"),
                            'alias': (runner["jockey"].get("alias") or "").strip().upper()
                        }
                    )

                    # Create or update entry
                    Entries.objects.update_or_create(
                        race=race,
                        horse=horse,
                        program_number=runner["programNumber"].strip().upper(),
                        defaults={
                            'post_position': int(runner['postPos']),
                            'trainer': trainer,
                            'jockey': jockey,
                            'drf_entries_import': True,
                            'scratch_indicator': runner.get("scratchIndicator"),
                            'medication': runner.get("medication"),
                            'equipment': runner.get("equipment"),
                            'weight': float(runner.get("weight", 0))
                        }
                    )
        else:
            print(f"Failed to fetch data from URL {url}. Status code: {response.status_code}")
