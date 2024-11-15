import requests
import logging
from datetime import datetime
import pytz
from django.core.exceptions import ValidationError
from horsemen.models import Races, Tracks, Horses, Jockeys, Trainers, Entries, Payoffs
from horsemen.data_collection.utils import drf_breed_word_to_code, convert_course_code_to_surface, convert_string_to_furlongs, get_post_time_from_drf, get_best_choice_from_description_code

# init logging
logger = logging.getLogger(__name__)

def get_drf_tracks():

    logger.info('running get_drf_tracks')

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
                }
            )
            if created:
                logger.warning(f'in get_drf_tracks, had to create track {track.name}')

            if track.code != 'AQU':
                continue

            # iterate through race_card and create race if necessary
            for race_card in track_info.get("cards", []):
                race_date = datetime.fromtimestamp(race_card["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()
                
                drf_results_import = True
                drf_entries_import = True
                for race_number in race_card.get("raceList", []):

                    # Create Races entries
                    try:
                        race, created = Races.objects.update_or_create(
                            track=track,
                            race_date=race_date,
                            race_number=race_number,
                            defaults={
                                'drf_tracks_import': True,
                                'day_evening': race_card.get("dayEvening", 'D'),
                            }
                        )
                        logger.info(f'in get_drf_tracks, {"created" if created else "updated"} race {race.race_number} on {race.race_date} at {track.name}')
                    except ValidationError as e:
                        logger.error(f'in get_drf_tracks, failed to save race due to {e.error_list}')
                        continue
                        
                    # check if results are needed
                    if not race.drf_results_import and race.race_date <= datetime.today().date():
                        drf_results_import = False
                    # check if entries are needed
                    if race.race_date >= datetime.today().date():
                        drf_entries_import = False

                # if results are needed
                if not drf_results_import:
                    logger.info(f'importing drf results for {track.name} on {race_date}')
                    import_drf_results(track, race_date)

                if not drf_entries_import:
                    logger.info(f'importing entries for {track.name} on {race_date}')
                    import_drf_entries(track, race_date)


    else:
        # Handle HTTP response errors
        logger.error(f"in get_drf_tracks, failed to fetch data. Status code: {response.status_code}")

def import_drf_results(track, race_date):

    # get data from url
    url = track.get_drf_results_url_for_date(race_date)
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # iterate through races
        for race_data in data.get('races',[]):
            
            # recalculate date in case something weird happens
            race_date = datetime.fromtimestamp(race_data['raceKey']["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()

            # Update or create the race in the database
            try:
                race, created = Races.objects.update_or_create(
                    track=track,
                    race_date=race_date,
                    race_number=race_data["raceKey"]["raceNumber"],
                    defaults={
                        'drf_results_import': True,
                        'post_time': get_post_time_from_drf(track=track, race_date=race_date, post_time_local_str=race_data.get('postTime','')),
                        'age_restriction': race_data.get("ageRestriction", ""),
                        'sex_restriction': "O" if race_data.get("sexRestriction", "") == "" else race_data.get("sexRestriction", ""),
                        'minimum_claiming_price': race_data.get("minClaimPrice", 0) if race_data.get("minClaimPrice", 0)>0 else race_data.get("maxClaimPrice", 0),
                        'maximum_claiming_price': race_data.get("maxClaimPrice", 0),
                        'distance': convert_string_to_furlongs(race_data.get("distanceDescription")),
                        'purse': float(race_data.get("totalPurse", 0).replace(',','')),
                        'breed': drf_breed_word_to_code(race_data.get("breed", "Thoroughbred")),
                        'cancelled': False,
                        'race_surface': convert_course_code_to_surface(race_data.get('surface', 'D')),
                        'race_type':get_best_choice_from_description_code(race_data.get('raceTypeDescription',''), Races.EQUIBASE_RACE_TYPE_CHOICES),
                        'condition': race_data.get("trackConditionDescription", '').strip().upper()
                    }
                )
                
                # logging
                logger.info(f'in import_drf_results, {"created" if created else "updated"} race {race.race_number} on {race.race_date} at {track.name}')
            except ValidationError as e:
                logger.error(f'in import_drf_results, failed to save race due to {e.messages}')
                return
            
            # scratches
            for horse_name in race_data.get('scratches',[]):
                entry = Entries.objects.filter(
                    race=race,
                    horse__horse_name=horse_name.upper().strip(),
                ).first()
                if entry:
                    if entry.scratch_indicator == 'N':
                        try:
                            entry.scratch_indicator = 'U'
                            entry.save()
                            logger.info(f'in import_drf_results, scratched {horse_name} in race {race.race_number} on {race.race_date} at {track.name}')
                        except ValidationError as e:
                            logger.error(f'in import_drf_results, failed to save entry (scratch) due to {e.error_list}')
                else:
                    logger.error(f'in import_drf_results, cant find {horse_name} in race {race.race_number} on {race.race_date} at {race.track.name} for scratches')
            
            # WPS payoffs
            for runner_data in race_data.get('runners',[]):
                horse_name = runner_data.get('horseName','').upper().strip()
                entry = Entries.objects.filter(
                    race=race,
                    horse__horse_name=horse_name,
                ).first()
                if not entry:
                    horse = Horses.objects.update_or_create(
                        horse_name=horse_name
                    )
                    entry = Entries.objects.create(
                        race=race,
                        horse=horse
                    )
                    entry.save()
                if entry:
                    try:
                        entry.win_payoff = runner_data.get('winPayoff',0)
                        entry.place_payoff = runner_data.get('winPayoff',0)
                        entry.show_payoff = runner_data.get('showPayoff',0)
                        entry.save()
                    except ValidationError as e:
                            logger.error(f'in import_drf_results, failed to save entry (wps) due to {e.error_list}')
                else:
                    logger.error(f'in import_drf_results, cant find {horse_name} in race {race.race_number} on {race.race_date} at {race.track.name} for wps payoffs')
            

            # Reg Payoffs
            for payoff_data in race_data.get('payoffs',[]):

                # get base amount from a different spot in the data
                base_amount = 0
                for wager_type_data in race_data.get('wagerTypes',[]):
                    if wager_type_data.get('wagerType','') == payoff_data.get('wagerType',''):
                        base_amount = float(wager_type_data.get('baseAmount',0))
                if base_amount == 0:
                    logger.error(f'in import_drf_results, couldnt find base amount for {payoff_data.get("wagerType","")} in race {race.race_number} on {race.race_date} at {race.track.name}')

                # create payoffs
                try:
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
                except ValidationError as e:
                    logger.error(f'in import_drf_results, failed to save payoff due to {e.error_list}')
               

    else:
        logger.error(f"in import_drf_results, failed to fetch data from URL {url}. Status code: {response.status_code}")

def import_drf_entries(track, race_date):

    # get data from url
    url = track.get_drf_entries_url_for_date(race_date)
    response = requests.get(url)
    if response.status_code == 200:
        race_data = response.json()

        # iterate through races
        for race_json in race_data.get("races", []):

            # recalculate date in case something weird happens
            race_date = datetime.fromtimestamp(race_json['raceKey']["raceDate"]["date"] / 1000.0, tz=pytz.UTC).date()

            # Update or create the race in the database
            try:
                race, created = Races.objects.update_or_create(
                    track=track,
                    race_date=race_date,
                    race_number=race_json["raceKey"]["raceNumber"],
                    defaults={
                        'drf_entries_import': True,
                        'post_time': get_post_time_from_drf(track=track, race_date=race_date, post_time_local_str=race_json.get('postTime','')),
                        'age_restriction': race_json.get("ageRestriction", ""),
                        'sex_restriction': "O" if race_json.get("sexRestriction", "") == "" else race_json.get("sexRestriction", ""),
                        'minimum_claiming_price': race_json.get("minClaimPrice", 0),
                        'maximum_claiming_price': race_json.get("maxClaimPrice", 0),
                        'distance': convert_string_to_furlongs(race_json.get('distanceDescription','')),
                        'purse': race_json.get("purse", 0),
                        'wager_text': race_json.get("wagerText", ""),
                        'breed': drf_breed_word_to_code(race_json.get("breed", "Thoroughbred")),
                        'cancelled': race_json.get("isCancelled", False),
                        'race_surface': convert_course_code_to_surface(race_json.get('courseType', 'D')),
                    }
                )
            
                # logging
                logger.info(f'in import_drf_entries, {"created" if created else "updated"} race {race.race_number} on {race.race_date} at {track.name}')
            
            except ValidationError as e:
                logger.error(f'in import_drf_entries, failed to save race due to {e.error_list}')
                return

            # Process runners (horses, jockeys, trainers, entries)
            for runner in race_json.get("runners", []):
                
                # Handle Horse
                horse_name_upper = runner['horseName'].strip().upper()
                horse = Horses.objects.filter(
                    registration_number=runner.get('registrationNumber','')
                ).first()
                
                # new horse
                if not horse:

                    # Sire
                    sire_name_upper = runner['sireName'].strip().upper()
                    if sire_name_upper != '':
                        sire, created = Horses.objects.update_or_create(
                            horse_name=sire_name_upper
                        )
                        logger.info(f'in import_drf_entries, {"created" if created else "updated"} sire {sire.horse_name} in race {race.race_number} on {race.race_date} at {track.name}')
                    else:
                        sire = None
    
                    # Dam
                    dam_name_upper = runner['damName'].strip().upper()
                    if dam_name_upper != '':
                        dam, created = Horses.objects.update_or_create(
                            horse_name=dam_name_upper
                        )
                        logger.info(f'in import_drf_entries, {"created" if created else "updated"} dam {dam.horse_name} in race {race.race_number} on {race.race_date} at {track.name}')
                    else:
                        dam = None
    
                    # Dam Sire
                    dam_sire_name_upper = runner['damSireName'].strip().upper()
                    if dam_sire_name_upper != '':
                        dam_sire, created = Horses.objects.update_or_create(
                            horse_name=dam_sire_name_upper
                        )
                        logger.info(f'in import_drf_entries, {"created" if created else "updated"} dam sire {dam_sire.horse_name} in race {race.race_number} on {race.race_date} at {track.name}')
                    else:
                        dam_sire = None
    
                    # Handle Horse
                    try:
                        horse, created = Horses.objects.update_or_create(
                            horse_name=horse_name_upper,
                            defaults={
                                'registration_number': runner.get('registrationNumber',''),
                                'dam': dam,
                                'sire': sire,
                                'dam_sire': dam_sire
                            }
                        )
                        logger.info(f'in import_drf_entries, {"created" if created else "updated"} horse {horse.horse_name} in race {race.race_number} on {race.race_date} at {track.name}')
                    except ValidationError as e:
                        logger.error(f'in import_drf_entries, failed to save horse due to {e.error_list}')
                        return
               

                # Handle Trainer
                trainer = Trainers.objects.filter(
                    drf_trainer_id=runner["trainer"].get("id")
                ).first()
                if not trainer:
                    try:
                        trainer, created = Trainers.objects.update_or_create(
                            first_name=runner["trainer"]["firstName"].strip().upper(),
                            last_name=runner["trainer"]["lastName"].strip().upper(),
                            defaults={
                                'middle_name': (runner["trainer"]["middleName"] or "").strip().upper(),
                                'drf_trainer_id': runner["trainer"].get("id"),
                                'drf_trainer_type': runner["trainer"].get("type"),
                                'alias': (runner["trainer"].get("alias") or "").strip().upper()
                            }
                        )
                        logger.info(f'in import_drf_entries, {"created" if created else "updated"} trainer {trainer.alias} in race {race.race_number} on {race.race_date} at {track.name} for horse {horse.horse_name}')
                    except ValidationError as e:
                        logger.error(f'in import_drf_entries, failed to save trainer due to {e.error_list}')
               

                # Handle Jockey
                jockey = Jockeys.objects.filter(
                    drf_jockey_id=runner["jockey"].get("id")
                ).first()
                if not jockey:
                    try:
                        jockey, created = Jockeys.objects.update_or_create(
                            first_name=runner["jockey"]["firstName"].strip().upper(),
                            last_name=runner["jockey"]["lastName"].strip().upper(),
                            defaults={
                                'middle_name': (runner["jockey"]["middleName"] or "").strip().upper(),
                                'drf_jockey_id': runner["jockey"].get("id"),
                                'drf_jockey_type': runner["jockey"].get("type"),
                                'alias': (runner["jockey"].get("alias") or "").strip().upper()
                            }
                        )
                        logger.info(f'in import_drf_entries, {"created" if created else "updated"} jockey {jockey.alias} in race {race.race_number} on {race.race_date} at {track.name} for horse {horse.horse_name}')
                    except ValidationError as e:
                        logger.error(f'in import_drf_entries, failed to save jockey due to {e.error_list}')
               
                    
                # Create or update entry
                try:
                    entry, created = Entries.objects.update_or_create(
                        race=race,
                        horse=horse,
                        defaults={
                            'program_number': runner["programNumber"].strip().upper(),
                            'post_position': int(runner['postPos']),
                            'trainer': trainer,
                            'jockey': jockey,
                            'drf_entries_import': True,
                            'scratch_indicator': runner.get("scratchIndicator",''),
                            'medication': runner.get("medication"),
                            'equipment': runner.get("equipment"),
                            'weight': float(runner.get("weight", 0))
                        }
                    )
                    logger.info(f'in import_drf_entries, {"created" if created else "updated"} entry {entry.program_number} in race {race.race_number} on {race.race_date} at {track.name} for horse {horse.horse_name}')
                except ValidationError as e:
                    logger.error(f'in import_drf_entries, failed to save entry due to {e.error_list}')
               