import requests
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
from horsemen.models import Races, Tracks, Horses, Jockeys, Trainers, Entries, Payoffs
from horsemen.data_collection.conversions import drf_breed_word_to_code
from horsemen.data_collection.utils import convert_string_to_furlongs, get_post_time_from_drf

def get_drf_tracks():

    # get data from url
    url = "https://formulator.drf.com/formulator-service/api/raceTracks"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    
        for track_info in data.get("allTracks", []):

            # create or update track
            track, created = Tracks.objects.update_or_create(
                code=track_info['trackId'],
                defaults={
                    'name': track_info['trackName'],
                    'country': track_info['country'],
                    'equibase_chart_name': track_info['trackName'].replace(' ','').lower(),
                }
            )

            # iterate through race_card and create race if necessary
            for race_card in track_info.get("cards", []):
                race_date = datetime.fromtimestamp(race_card["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()
                
                drf_results_import = True
                drf_entries_import = True
                for race_number in race_card.get("raceList", []):

                    # Create Races entries
                    race, created = Races.objects.update_or_create(
                        track=track,
                        race_date=race_date,
                        race_number=race_number,
                        defaults={
                            'drf_tracks_import': True,
                            'day_evening': race_card.get("dayEvening", 'D'),
                            'final': race_card.get("final", False)
                        }
                    )

                    # check if results are needed
                    if not race.drf_results_import and race.race_date <= datetime.today().date():
                        drf_results_import = False
                    # check if entries are needed
                    if race.race_date >= datetime.today().date():
                        drf_entries_import = False

                # if results are needed
                if not drf_results_import:
                    print(f'importing drf results for {track.name} on {race_date}')
                    import_drf_results(track, race_date)

                if not drf_entries_import:
                    print(f'importing entries for {track.name} on {race_date}')
                    import_drf_entries(track, race_date)


    else:
        # Handle HTTP response errors
        print(f"Failed to fetch data. Status code: {response.status_code}")

def import_drf_results(track, race_date):

    # get data from url
    url = f'https://www.drf.com/results/resultDetails/id/{track.code}/country/{track.country}/date/{race_date.strftime('%m-%d-%Y')}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # iterate through races
        for race_data in data.get('races',[]):
            
            # recalculate date in case something weird happens
            race_date = datetime.fromtimestamp(race_data['raceKey']["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()

            # Update or create the race in the database
            race, created = Races.objects.update_or_create(
                track=track,
                race_date=race_date,
                race_number=race_data["raceKey"]["raceNumber"],
                defaults={
                    'drf_results_import': True,
                    'post_time': get_post_time_from_drf(track=track, race_date=race_date, post_time_local_str=race_data.get('postTime','')),
                    'age_restriction': race_data.get("ageRestriction", ""),
                    'sex_restiction': "O" if race_data.get("sexRestriction", "") == "" else race_data.get("sexRestriction", ""),
                    'minimum_claiming_price': race_data.get("minClaimPrice", 0),
                    'maximum_claiming_price': race_data.get("maxClaimPrice", 0),
                    'distance': convert_string_to_furlongs(race_data.get("distanceDescription")),
                    'purse': float(race_data.get("totalPurse", 0).replace(',','')),
                    'breed': drf_breed_word_to_code(race_data.get("breed", "Thoroughbred")),
                    'cancelled': False,
                    'race_surface': race_data.get('surface', 'D')
                }
            )

            # scratches
            for horse_name in race_data.get('scratches',[]):
                entry = Entries.objects.filter(
                    race=race,
                    horse__horse_name=horse_name.upper().strip(),
                ).first()
                if entry:
                    if entry.scratch_indicator == 'N':
                        entry.scratch_indicator = 'U'
                        entry.save()
            
            # WPS payoffs
            for runner_data in race_data.get('runners',[]):
                entry = Entries.objects.filter(
                    race=race,
                    horse__horse_name=runner_data['horseName'].upper().strip(),
                ).first()
                if entry:
                    entry.drf_results_import = True
                    entry.win_payoff = runner_data.get('winPayoff',0)
                    entry.place_payoff = runner_data.get('winPayoff',0)
                    entry.show_payoff = runner_data.get('showPayoff',0)
                    entry.save()

            # Reg Payoffs
            for payoff_data in race_data.get('payoffs',[]):

                # get base amount from a different spot in the data
                base_amount = 0
                for wager_type_data in race_data.get('wagerTypes',[]):
                    if wager_type_data.get('wagerType','') == payoff_data.get('wagerType',''):
                        base_amount = float(wager_type_data.get('baseAmount',0))

                # create payoffs
                payoff, created = Payoffs.objects.update_or_create(
                    race=race,
                    wager_type=payoff_data.get('wagerType',''),
                    winning_numbers=payoff_data.get('winningNumbers','').strip().upper(),
                    defaults={
                        'total_pool': float(payoff_data.get('totalPool',0).replace(',','')),
                        'payoff_amount': float(payoff_data.get('payoffAmount',0).replace(',','')),
                        'base_amount': base_amount,
                    }
                )

    else:
        print(f"Failed to fetch data from URL {url}. Status code: {response.status_code}")

def import_drf_entries(track, race_date):

    # get data from url
    url = f"https://www.drf.com/entries/entryDetails/id/{track.code}/country/{track.country}/date/{race_date.strftime('%m-%d-%Y')}"
    response = requests.get(url)
    if response.status_code == 200:
        race_data = response.json()

        # iterate through races
        for race_json in race_data.get("races", []):

            # recalculate date in case something weird happens
            race_date = datetime.fromtimestamp(race_json['raceKey']["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()

            if race_json.get('distanceDescription','') == '':
                continue

            # Update or create the race in the database
            race, created = Races.objects.update_or_create(
                track=track,
                race_date=race_date,
                race_number=race_json["raceKey"]["raceNumber"],
                defaults={
                    'drf_entries_import': True,
                    'post_time': get_post_time_from_drf(track=track, race_date=race_date, post_time_local_str=race_json.get('postTime','')),
                    'age_restriction': race_json.get("ageRestriction", ""),
                    'sex_restiction': "O" if race_json.get("sexRestriction", "") == "" else race_json.get("sexRestriction", ""),
                    'minimum_claiming_price': race_json.get("minClaimPrice", 0),
                    'maximum_claiming_price': race_json.get("maxClaimPrice", 0),
                    'distance': convert_string_to_furlongs(race_json.get('distanceDescription','')),
                    'purse': race_json.get("purse", 0),
                    'wager_text': race_json.get("wagerText", ""),
                    'breed': drf_breed_word_to_code(race_json.get("breed", "Thoroughbred")),
                    'cancelled': race_json.get("isCancelled", False),
                    'race_surface': race_json.get('courseType', 'D'),
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