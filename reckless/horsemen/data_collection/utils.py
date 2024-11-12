from pathlib import Path
import re

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