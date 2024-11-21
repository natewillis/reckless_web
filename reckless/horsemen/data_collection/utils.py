from pathlib import Path
import re
import fractions
from word2number import w2n
import pytz
from datetime import datetime
from fuzzywuzzy import process
import logging
import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from horsemen.constants import FRACTIONALS, POINTS_OF_CALL, POINTS_OF_CALL_QH, METERS_PER_FURLONG, METERS_PER_LENGTH

# Configure logging
logger = logging.getLogger(__name__)

# Folder Paths
BASE_FOLDER = Path.cwd()
if BASE_FOLDER.name == 'reckless_web':
    HISTORY_FOLDER = BASE_FOLDER / 'scraping_history'
    SCRAPING_FOLDER = BASE_FOLDER / 'files_to_scrape'
else:
    HISTORY_FOLDER = BASE_FOLDER.parent / 'scraping_history'
    SCRAPING_FOLDER = BASE_FOLDER.parent / 'files_to_scrape'
logger.info("Paths initialized: HISTORY_FOLDER=%s, SCRAPING_FOLDER=%s", HISTORY_FOLDER, SCRAPING_FOLDER)


def make_safe_filename(filename) -> str:
    # Convert filename to string if it's a Path object
    if isinstance(filename, Path):
        filename = str(filename)
    
    # Define a pattern for characters that are unsafe in filenames on Windows and Linux
    unsafe_chars = r'[<>:"/\\|?*\x00-\x1F]'
    
    # Replace unsafe characters with underscores
    safe_filename = re.sub(unsafe_chars, '_', filename)
    
    # Limit length to a typical safe maximum for filenames (255 characters)
    return safe_filename[:255]


def convert_string_to_furlongs(distance_string):

    # UNITS
    FURLONGS_PER_MILE = 8
    FURLONGS_PER_YARD = 0.00454545

    # Fraction dictionary
    denominator_dictionary = {
        'HALF': 2,
        'THIRD': 3,
        'FOURTH': 4,
        'FIFTH': 5,
        'SIXTH': 6,
        'SEVENTH': 7,
        'EIGHTH': 8,
        'NINTH': 9,
        'TENTH': 10,
        'ELEVENTH': 11,
        'TWELFTH': 12,
        'THIRTEENTH': 13,
        'FOURTEENTH': 14,
        'FIFTEENTH': 15,
        'SIXTEENTH': 16
    }

    # massage string
    distance_string = distance_string.strip().upper()

    # special case X miles X yards
    match = re.search(r'(\d+)\s*MILES?\s+(\d+)\s*YARDS?', distance_string)
    if match:
        miles = int(match.group(1))
        yards = int(match.group(2))
        furlongs = (miles * 8) + (yards / 220)
        return furlongs
    match = re.search(r'(\w+)\s*MILES?\s+(AND\s+)?(\w+)\s*YARDS?', distance_string)
    if match:
        miles = w2n.word_to_num(match.group(1))
        yards = w2n.word_to_num(match.group(3))
        furlongs = (miles * 8) + (yards / 220)
        return furlongs

    # figure out unit
    conversion_factor = 0
    if 'MILE' in distance_string:
        conversion_factor = FURLONGS_PER_MILE
        distance_string = distance_string.replace('MILES','').replace('MILE','')
    elif 'FURLONG' in distance_string:
        conversion_factor = 1
        distance_string = distance_string.replace('FURLONGS','').replace('FURLONG','')
    elif 'YARD' in distance_string:
        conversion_factor = FURLONGS_PER_YARD
        distance_string = distance_string.replace('YARDS','').replace('YARD','')
    elif distance_string[-1] == 'F':
        conversion_factor = 1
        distance_string = distance_string = distance_string[:-1]
    elif distance_string[-1] == 'M':
        conversion_factor = FURLONGS_PER_MILE
        distance_string = distance_string = distance_string[:-1]
    elif distance_string[-1] == 'Y':
        conversion_factor = FURLONGS_PER_YARD
        distance_string = distance_string = distance_string[:-1]
    distance_string = distance_string.strip()
    
    # check for fractions
    if '/' in distance_string:
        remaining_strings = []
        for part in distance_string.split(' '):
            if '/' in part:
                fraction_value = fractions.Fraction(part)
            else:
                remaining_strings.append(part)
        distance_string = ' '.join(remaining_strings)
        if distance_string.isnumeric():
            return (float(distance_string) + fraction_value) * conversion_factor

    # if its numeric, and less than 20 its furlongs
    if distance_string.isnumeric():
        distance_number = float(distance_string)
        if conversion_factor>0:
            return distance_number * conversion_factor
        else:
            if distance_number < 4:
                return distance_number * FURLONGS_PER_MILE
            elif distance_number > 20:
                return distance_number * FURLONGS_PER_YARD
            else:
                return distance_number
            
    # if its not numeric and we dont have a unit, be done
    if conversion_factor == 0:
        print(f'ERROR: {distance_string} could not be parsed!')
        return -1
    
    # figure out fraction
    fraction_value = 0
    if ' AND ' in distance_string:
        split_string = distance_string.split('AND')
        if len(split_string) > 2:
            print(f'ERROR: {distance_string} could not be parsed!')
            return -1
        fraction_string = split_string[1]
        denominator_value = 0
        for denominator_word in denominator_dictionary.keys():
            if denominator_word in fraction_string:
                denominator_value = denominator_dictionary[denominator_word]
                fraction_string = fraction_string.replace(denominator_word,'')
        if denominator_value == 0:
            # this is just a big number e.g. one hundred and twenty yards
            pass
        else:
            distance_string = split_string[0]
            numerator_value = w2n.word_to_num(fraction_string)
            if numerator_value < 0:
                print(f'ERROR: {distance_string} could not be parsed!')
                return -1
            fraction_value = numerator_value/denominator_value
    
    # figure out main part
    return_value = w2n.word_to_num(distance_string)
    if return_value < 0:
        print(f'ERROR: {distance_string} could not be parsed!')
        return -1

    # final calcs
    return (return_value + fraction_value) * conversion_factor

def convert_string_to_seconds(time_string):

    # Pattern to match both formats (e.g., '1:11.44' or '11.44')
    pattern = r'(?:(\d+):)?(\d+\.\d+)' 
    
    match = re.match(pattern, time_string)
    if not match:
        raise ValueError("Invalid time format")
    
    # Extract minutes and seconds
    minutes = int(match.group(1)) if match.group(1) else 0
    seconds = float(match.group(2))
    
    # Convert to total seconds
    total_seconds = minutes * 60 + seconds
    return total_seconds

def convert_lengths_back_string(lengths_back_string):

    # Process
    lengths_back_string = lengths_back_string.upper().strip()

    # check for strings first then convert
    if lengths_back_string == 'NOSE':
        return 0.05
    elif lengths_back_string == 'HEAD':
        return 0.2
    elif lengths_back_string == 'NECK':
        return 0.3
    else:
        return float(sum(fractions.Fraction(term) for term in lengths_back_string.split()))
    
def get_post_time_from_drf(track, race_date, post_time_local_str):

    # Post time calculations
    try:
        original_tz = pytz.timezone(track.time_zone)
        post_time_local = datetime.strptime(post_time_local_str, "%I:%M %p")
        post_time_datetime = datetime.combine(race_date, post_time_local.time())
        post_time_localized = original_tz.localize(post_time_datetime)
        post_time_utc = post_time_localized.astimezone(pytz.UTC)
    except (ValueError, TypeError):
        post_time_utc = None

    return post_time_utc

def get_best_choice_from_description_code(input_string, choices):
    
    # process input string
    input_string = input_string.strip().upper()
    if input_string != '':
    
        # Extract race type descriptions from the choices
        descriptions = [description.upper() for choice, description in choices]

        # check for exact match first
        if input_string in descriptions:
            for choice, description in choices:
                if description.upper() == input_string:
                    return choice
    
        # Find the best match
        best_match = process.extractOne(input_string, descriptions)
    
        if best_match:
            # Retrieve the description and match score
            match_description, match_score = best_match
            logger.debug(f'in get_best_choice_from_description_code, {match_description} matches {input_string} with a score of {match_score}')
    
            # Find the corresponding code
            for choice, description in choices:
                if description.upper() == match_description:
                    return choice

    logger.warning(f'in get_best_choice_from_description_code, {input_string} did not return a match')
    return None

def convert_course_code_to_surface(course_code):
    # Define the mapping of course codes to surface codes
    course_to_surface_map = {
        'A': 'D',  # All Weather Training
        'D': 'D',  # Dirt
        'E': 'D',  # All Weather Track
        'F': 'D',  # Dirt Training
        'N': 'D',  # Inner Track
        'W': 'D',  # Wood Chips
        'B': 'T',  # Timber
        'C': 'T',  # Downhill Turf
        'G': 'T',  # Turf Training
        'I': 'T',  # Inner Turf
        'J': 'T',  # Jump
        'M': 'T',  # Hurdle
        'O': 'T',  # Outer Turf
        'S': 'T',  # Steeplechase
        'T': 'T',  # Turf
        'U': 'T',  # Hunt on Turf
    }
    
    # Return the corresponding surface code if the course code exists in the dictionary
    return course_to_surface_map.get(course_code, "D")

def drf_breed_word_to_code(breed_name):
    # Mapping dictionary
    breed_codes = {
        "thoroughbred": "TB",
        "quarter horse": "QH",
        "arabian": "AR",
        "paint": "PT",
        "mixed breeds": "MX"
    }

    # Convert the input to lowercase for case-insensitive matching
    breed_name_lower = breed_name.lower()

    # Return the corresponding code or None if not found
    return breed_codes.get(breed_name_lower, None)

def get_fractional_time_object_from_furlongs(distance_furlongs):

    # convert furlongs to feet
    distance_feet = distance_furlongs * 660

    # Figure out which fractional time object we need
    last_fractional_object = None
    for fractional_object in FRACTIONALS:
        if distance_feet<fractional_object['floor']-10:
            logger.debug(f'for {distance_feet} feet returning point of call for {last_fractional_object['floor']}')
            return last_fractional_object
        last_fractional_object = fractional_object

def get_point_of_call_object_from_furlongs(distance_furlongs, quarter_horse_flag=False):

    # convert furlongs to feet
    distance_feet = distance_furlongs * 660
    logger.debug(f' in get_point_of_call_object_from_furlongs, looking for {distance_feet} feet')

    #  quarterhorse
    if quarter_horse_flag:
        points_of_call_to_use = POINTS_OF_CALL_QH
    else:
        points_of_call_to_use = POINTS_OF_CALL
    
    # Figure out which fractional time object we need
    last_point_of_call_object = None
    for point_of_call_object in points_of_call_to_use:
        if distance_feet<point_of_call_object['floor']-10:
            logger.debug(f'for {distance_feet} feet returning point of call for {last_point_of_call_object['floor']}')
            return last_point_of_call_object
        last_point_of_call_object = point_of_call_object
        
def create_fractional_data_from_array_and_object(fractional_times, race_distance):

    # init return
    fractional_data = []

    # get fractional object
    fractional_object = get_fractional_time_object_from_furlongs(race_distance)

    # edge cases
    if fractional_times is None or len(fractional_times) == 0:
        logger.warning('in create_fractional_data_from_array_and_object, both fractional_times and fractional_object are none')
        return fractional_data
    if fractional_object is None or len(fractional_times) == 1:
        # the only thing we know for sure in this case is that the final time is
        # a the race distance
        fractional_data.append({
            'point': 6,
            'text': 'FIN',
            'distance': race_distance,
            'time': fractional_times[-1]
        })
        logger.warning('in create_fractional_data_from_array_and_object, fractional_object is empty so only returning final')
        return fractional_data
    if len(fractional_times) == len(fractional_object['fractionals']):
        logger.info('in create_fractional_data_from_array_and_object, fractional times match!')
        for index, fractional_time in enumerate(fractional_times):
            fractional = fractional_object['fractionals'][index]
            fractional_data.append({
                'point': fractional['point'],
                'text': 'FIN' if index+1 == len(fractional_times) else fractional['text'].upper(),
                'distance': race_distance if index+1 == len(fractional_times) else fractional['feet']/660,
                'time': fractional_time
            })
        return fractional_data
    else:
        # do our best to map the times to the fractional object
        # setup variables needed inside either loop
        final_time = fractional_times[-1]
        average_velocity = race_distance/final_time # furlongs per second
        fractionals_copy = fractional_object['fractionals'].copy()[:-1] # all but the last one, we automatically map that to final
        fractional_times_copy = fractional_times.copy()[:-1] # samesies
        
        # more fractionals means map closest fractional to each time
        if len(fractionals_copy)>len(fractional_times_copy):
            logger.warning('in create_fractional_data_from_array_and_object, more fractional objects then times')
            for time_index, fractional_time in enumerate(fractional_times_copy):
                
                # init loop
                closest_delta_velocity = 1000000
                best_fractional_index=-1
                
                # loop through each time, and for each time choose the closest fractional
                for fractional_index, fractional in enumerate(fractionals_copy):
                    calculated_velocity = (fractional['feet']/660)/fractional_time
                    if abs(calculated_velocity-average_velocity)<closest_delta_velocity:
                        closest_delta_velocity=abs(calculated_velocity-average_velocity)
                        best_fractional_index=fractional_index
                
                # now that we have the likely fractional index
                fractional_to_assign=fractionals_copy.pop(best_fractional_index)
                
                # assign fractional
                fractional_data.append({
                    'point': fractional_to_assign['point'],
                    'text': fractional_to_assign['text'].upper(),
                    'distance': fractional_to_assign['feet']/660,
                    'time': fractional_time
                })
        else:
            logger.warning('in create_fractional_data_from_array_and_object, more fractional times then objects')
            # more times means map closest time to each fractional
            for fractional_index, fractional in enumerate(fractionals_copy):
                
                # init inner loop
                closest_delta_velocity = 1000000
                best_fractional_time_index=-1
                
                # loop through each fractional, and for each fractional choose the closest time
                for time_index, fractional_time in enumerate(fractional_times_copy):
                    calculated_velocity = (fractional['feet']/660)/fractional_time
                    if abs(calculated_velocity-average_velocity)<closest_delta_velocity:
                        closest_delta_velocity=abs(calculated_velocity-average_velocity)
                        best_fractional_time_index=time_index
                        
                # now that we have the likely time index
                time_to_assign=fractional_times_copy.pop(best_fractional_time_index)
                
                # assign fractional
                fractional_data.append({
                    'point': fractional['point'],
                    'text': fractional['text'].upper(),
                    'distance': fractional['feet']/660,
                    'time': time_to_assign
                })
                
        # append the final time
        fractional_data.append({
            'point': 6,
            'text': 'FIN',
            'distance': race_distance,
            'time': fractional_time
        })
        
        # finished
        return fractional_data
    
def get_position_velocity_array_from_fractions_and_points_of_call(fractions, points_of_call, num_points=5):
    
    # get the race distance (everything in meters)
    race_distance = fractions[-1].distance * METERS_PER_FURLONG
    
    # get the array of distances based on num points
    evaluation_distances = np.linspace(0,race_distance,num_points+1)
    
    # points of call data formatting
    horse_lb_distance=[0]
    horse_lb=[0]
    for point_of_call in points_of_call:
        if point_of_call.distance > 0:
            horse_lb_distance.append(point_of_call.distance * METERS_PER_FURLONG)
            horse_lb.append(point_of_call.lengths_back * METERS_PER_LENGTH)
    
    # fractional data formatting
    fractional_distances = [0]
    fractional_times = [0]
    for fraction in fractions:
        fractional_distances.append(fraction.distance * METERS_PER_FURLONG)
        fractional_times.append(fraction.time)
        
    # get horses lengths back from leader at each interval
    horse_lb_at_distance = np.interp(
        evaluation_distances,
        horse_lb_distance,
        horse_lb
    )
    
    # get leaders position when horse is crossing each interval
    leader_distance_at_horse_distance = np.array(evaluation_distances) + horse_lb_at_distance
    
    # must use a spline to do the extrapolation in case the horse inst the leader
    # and leader distance is longer than the race distance
    
    fractional_distance_time_spline = InterpolatedUnivariateSpline(
        fractional_distances,
        fractional_times,
        k=1 # linear extrapolation
    )
    
    # get leaders time at those positions (which is the horses time at the intervals)
    horse_times = fractional_distance_time_spline(leader_distance_at_horse_distance)

    # get velocity
    horse_velocities = (evaluation_distances[1]-evaluation_distances[0]) / np.diff(horse_times)

    return horse_velocities
        
    