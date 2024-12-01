"""
Parser module for Equibase entries data.
Handles parsing of extracted entries data into structured format.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime


# Configure logging
logger = logging.getLogger(__name__)

def parse_track_data(race_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse track information from race data.
    
    Args:
        race_data: Dictionary containing race information
        
    Returns:
        Dictionary containing parsed track data
    """
    logger.debug("Parsing track data")
    
    try:
        if 'track' not in race_data:
            logger.warning("No track data found")
            return {}

        track_data = race_data['track']
        if not track_data.get('code') or not track_data.get('name'):
            logger.warning("Missing required track fields")
            return {}

        return {
            'object_type': 'track',
            'code': track_data['code'],
            'name': track_data['name']
        }

    except Exception as e:
        logger.error("Error parsing track data: %s", e)
        return {}

def parse_horse_data(entry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse horse information from entry data.
    
    Args:
        entry_data: Dictionary containing entry information
        
    Returns:
        Dictionary containing parsed horse data
    """
    logger.debug("Parsing horse data")
    
    try:
        if 'horse' not in entry_data:
            logger.warning("No horse data found")
            return {}

        horse_data = entry_data['horse']
        required_fields = ['horse_name', 'equibase_horse_id', 
                         'equibase_horse_registry', 'equibase_horse_type']
        
        if not all(field in horse_data for field in required_fields):
            logger.warning("Missing required horse fields")
            return {}

        parsed_data = {
            'object_type': 'horse',
            'horse_name': horse_data['horse_name'],
            'equibase_horse_id': horse_data['equibase_horse_id'],
            'equibase_horse_registry': horse_data['equibase_horse_registry'],
            'equibase_horse_type': horse_data['equibase_horse_type']
        }

        if horse_data.get('horse_state_or_country'):
            parsed_data['horse_state_or_country'] = horse_data['horse_state_or_country']

        return parsed_data

    except Exception as e:
        logger.error("Error parsing horse data: %s", e)
        return {}

def parse_connection_data(entry_data: Dict[str, Any], connection_type: str) -> Optional[Dict[str, Any]]:
    """
    Parse jockey or trainer information from entry data.
    
    Args:
        entry_data: Dictionary containing entry information
        connection_type: Type of connection ('jockey' or 'trainer')
        
    Returns:
        Dictionary containing parsed connection data
    """
    logger.debug("Parsing %s data", connection_type)
    
    try:
        if connection_type not in entry_data:
            logger.debug("No %s data found", connection_type)
            return None
        if entry_data[connection_type] is None:
            logger.debug("No %s data found", connection_type)
            return None

        connection_data = entry_data[connection_type]
        required_fields = [
            'last_name', 'first_initials',
            f'equibase_{connection_type}_id',
            f'equibase_{connection_type}_type'
        ]
        
        if not all(field in connection_data for field in required_fields):
            logger.warning("Missing required %s fields", connection_type)
            return None

        return {
            'object_type': connection_type,
            'first_initials': connection_data['first_initials'],
            'last_name': connection_data['last_name'],
            f'equibase_{connection_type}_id': connection_data[f'equibase_{connection_type}_id'],
            f'equibase_{connection_type}_type': connection_data[f'equibase_{connection_type}_type']
        }

    except Exception as e:
        logger.error("Error parsing %s data of (%s): %s", connection_type, entry_data, e)
        return None

def parse_entry_data(entry_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse entry information.
    
    Args:
        entry_data: Dictionary containing entry information
        
    Returns:
        Dictionary containing parsed entry data
    """
    logger.debug("Parsing entry data")
    
    try:

        # init
        parsed_data = {
            'object_type': 'entry',
        }

        # parse program number
        if 'program_number' in entry_data:
            parsed_data['program_number'] = entry_data['program_number']

        # Parse horse data
        horse_data = parse_horse_data(entry_data)
        if horse_data:
            parsed_data['horse'] = horse_data

        # Parse jockey data
        jockey_data = parse_connection_data(entry_data, 'jockey')
        if jockey_data:
            parsed_data['jockey'] = jockey_data

        # Parse trainer data
        trainer_data = parse_connection_data(entry_data, 'trainer')
        if trainer_data:
            parsed_data['trainer'] = trainer_data

        return parsed_data

    except Exception as e:
        logger.error("Error parsing entry data: %s", e)
        return {}

def parse_race_data(race_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse complete race information.
    
    Args:
        race_data: Dictionary containing race information
        
    Returns:
        Dictionary containing parsed race data
    """
    logger.debug("Parsing race data")
    
    try:
        required_fields = ['race_number', 'race_date']
        if not all(field in race_data for field in required_fields):
            logger.warning("Missing required race fields")
            return {}

        parsed_data = {
            'object_type': 'race',
            'race_number': race_data['race_number'],
            'race_date': race_data['race_date'],
            'children': []
        }

        # Parse track data
        track_data = parse_track_data(race_data)
        if track_data:
            parsed_data['track'] = track_data

        # Parse entries
        if 'entries' in race_data:
            for entry_data in race_data['entries']:
                parsed_entry = parse_entry_data(entry_data)
                if parsed_entry:
                    parsed_data['children'].append(parsed_entry)

        return parsed_data

    except Exception as e:
        logger.error("Error parsing race data: %s", e)
        return {}

def parse_extracted_entries_data(extracted_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse complete extracted entries data into structured race information.
    
    Args:
        extracted_data: List of dictionaries containing extracted entries data
        
    Returns:
        List of dictionaries containing fully parsed race information
    """
    logger.info("Beginning parse of extracted entries data")
    
    try:
        parsed_data = []
        for race_data in extracted_data:
            parsed_race = parse_race_data(race_data)
            if parsed_race:
                parsed_data.append(parsed_race)
                
        logger.info("Successfully parsed %d races", len(parsed_data))
        return parsed_data

    except Exception as e:
        logger.error("Error parsing extracted entries data: %s", e)
        return []
