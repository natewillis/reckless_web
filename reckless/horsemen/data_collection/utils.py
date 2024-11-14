from pathlib import Path
import re
import fractions
from word2number import w2n
import pytz
from datetime import datetime

# constants
HISTORY_FOLDER = Path.cwd().parent / 'scraping_history'

# pathing for where to put the file
SCRAPING_FOLDER = Path.cwd()
print(SCRAPING_FOLDER)
if SCRAPING_FOLDER.parts[-1] == 'reckless_web':
    HISTORY_FOLDER = SCRAPING_FOLDER / 'scraping_history'
    SCRAPING_FOLDER = SCRAPING_FOLDER / 'files_to_scrape'
else:
    HISTORY_FOLDER = SCRAPING_FOLDER.parent / 'scraping_history'
    SCRAPING_FOLDER = SCRAPING_FOLDER.parent / 'files_to_scrape'


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

def convert_lengths_back_string_to_furlongs(lengths_back_string):

    # constants
    FURLONGS_PER_LENGTH = 0.0121212

    # Process
    lengths_back_string = lengths_back_string.upper().strip()

    # check for strings first then convert
    if lengths_back_string == 'NOSE':
        return 0.05 * FURLONGS_PER_LENGTH,
    elif lengths_back_string == 'HEAD':
        return 0.2 * FURLONGS_PER_LENGTH
    elif lengths_back_string == 'NECK':
        return 0.3 * FURLONGS_PER_LENGTH
    else:
        return float(sum(fractions.Fraction(term) for term in lengths_back_string.split())) * FURLONGS_PER_LENGTH
    
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