"""
Parser module for Equibase horse results data.
Handles parsing of extracted horse results data into structured format.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def parse_horse_data(horse_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse horse information.
    
    Args:
        horse_data: Dictionary containing horse information
        
    Returns:
        Dictionary containing parsed horse data
    """
    logger.debug("Parsing horse data")
    
    try:
        if not horse_data or 'equibase_horse_id' not in horse_data:
            logger.warning("No horse ID found")
            return {}

        parsed_data = {
            'object_type': 'horse',
            'equibase_horse_id': horse_data['equibase_horse_id']
        }

        # Add optional fields if present
        optional_fields = ['horse_name', 'equibase_horse_type', 'equibase_horse_registry']
        for field in optional_fields:
            if field in horse_data:
                parsed_data[field] = horse_data[field]

        logger.debug("Successfully parsed horse data: %s", parsed_data)
        return parsed_data

    except Exception as e:
        logger.error("Error parsing horse data: %s", e)
        return {}

def parse_track_data(track_code: str, track_country: str) -> Dict[str, Any]:
    """
    Parse track information.
    
    Args:
        track_code: Track code
        track_country: Track country code
        
    Returns:
        Dictionary containing parsed track data
    """
    logger.debug("Parsing track data for %s", track_code)
    
    try:
        return {
            'object_type': 'track',
            'code': track_code,
            'country': track_country
        }

    except Exception as e:
        logger.error("Error parsing track data: %s", e)
        return {}

def parse_entry_data(entry_data: Dict[str, Any], horse_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse entry information.
    
    Args:
        entry_data: Dictionary containing entry information
        horse_data: Dictionary containing horse information
        
    Returns:
        Dictionary containing parsed entry data
    """
    logger.debug("Parsing entry data")
    
    try:
        if not all(key in entry_data for key in ['track_code', 'race_date', 'race_number']):
            logger.warning("Missing required entry fields")
            return {}

        parsed_data = {
            'object_type': 'entry',
            'race': {
                'object_type': 'race',
                'track': parse_track_data(entry_data['track_code'], entry_data['track_country']),
                'race_date': entry_data['race_date'],
                'race_number': entry_data['race_number']
            },
            'horse': parse_horse_data(horse_data),
            'equibase_horse_entries_import': True
        }

        logger.debug("Successfully parsed entry data")
        return parsed_data

    except Exception as e:
        logger.error("Error parsing entry data: %s", e)
        return {}

def parse_workout_data(workout_data: Dict[str, Any], horse_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse workout information.
    
    Args:
        workout_data: Dictionary containing workout information
        horse_data: Dictionary containing horse information
        
    Returns:
        Dictionary containing parsed workout data
    """
    logger.debug("Parsing workout data")
    
    try:
        required_fields = [
            'track_code', 'workout_date', 'distance', 'surface',
            'time_seconds', 'note', 'workout_rank', 'workout_total'
        ]
        
        if not all(key in workout_data for key in required_fields):
            logger.warning("Missing required workout fields")
            return {}

        parsed_data = {
            'object_type': 'workout',
            'track': parse_track_data(workout_data['track_code'], workout_data['track_country']),
            'horse': parse_horse_data(horse_data),
            'workout_date': workout_data['workout_date'],
            'surface': workout_data['surface'],
            'distance': workout_data['distance'],
            'time_seconds': workout_data['time_seconds'],
            'note': workout_data['note'],
            'workout_rank': workout_data['workout_rank'],
            'workout_total': workout_data['workout_total']
        }

        logger.debug("Successfully parsed workout data")
        return parsed_data

    except Exception as e:
        logger.error("Error parsing workout data: %s", e)
        return {}

def parse_result_data(result_data: Dict[str, Any], horse_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse race result information.
    
    Args:
        result_data: Dictionary containing result information
        horse_data: Dictionary containing horse information
        
    Returns:
        Dictionary containing parsed result data
    """
    logger.debug("Parsing result data")
    
    try:
        if not all(key in result_data for key in ['track_code', 'race_date', 'race_number']):
            logger.warning("Missing required result fields")
            return {}

        parsed_data = {
            'object_type': 'entry',
            'race': {
                'object_type': 'race',
                'track': parse_track_data(result_data['track_code'], result_data['track_country']),
                'race_date': result_data['race_date'],
                'race_number': result_data['race_number']
            },
            'horse': parse_horse_data(horse_data),
            'equibase_horse_results_import': True
        }

        if result_data.get('speed_rating') is not None:
            parsed_data['equibase_speed_rating'] = result_data['speed_rating']

        logger.debug("Successfully parsed result data")
        return parsed_data

    except Exception as e:
        logger.error("Error parsing result data: %s", e)
        return {}

def parse_extracted_horse_results_data(extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse complete extracted horse results data into structured information.
    
    Args:
        extracted_data: Dictionary containing extracted horse results data
        
    Returns:
        List of dictionaries containing fully parsed horse results information
    """
    logger.info("Beginning parse of extracted horse results data")
    
    try:
        parsed_data = []
        horse_data = extracted_data.get('horse')
        
        if not horse_data:
            logger.error("No horse data found in extracted data")
            return []

        # Parse entries
        for entry_data in extracted_data.get('entries', []):
            parsed_entry = parse_entry_data(entry_data, horse_data)
            if parsed_entry:
                parsed_data.append(parsed_entry)

        # Parse workouts
        for workout_data in extracted_data.get('workouts', []):
            parsed_workout = parse_workout_data(workout_data, horse_data)
            if parsed_workout:
                parsed_data.append(parsed_workout)

        # Parse results
        for result_data in extracted_data.get('results', []):
            parsed_result = parse_result_data(result_data, horse_data)
            if parsed_result:
                parsed_data.append(parsed_result)

        logger.info("Successfully parsed horse results data")
        return parsed_data

    except Exception as e:
        logger.error("Error parsing extracted horse results data: %s", e)
        return []
