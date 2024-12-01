# zenrows
from zenrows import ZenRowsClient

# brightdata requests
import requests

# support
import logging
import environ
from pathlib import Path
from horsemen.data_collection.utils import SCRAPING_FOLDER

# init logging
logger = logging.getLogger(__name__)

# setup path to env file to get zenrows api
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f'base dir is {BASE_DIR}')
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

# FAIL_LIMIT
FAIL_LIMIT = 2

def detect_problem(html_content):
    if detect_incapsula_block(html_content):
        logger.error('incapsula block!')
        return True
    
    if detect_zenrows_422(html_content):
        logger.error('zenrows 422')
        return True
    
    return False


def detect_incapsula_block(html_content):
    if 'Request unsuccessful. Incapsula incident ID:' in html_content:
        return True
    return False

def detect_zenrows_422(html_content):
    if 'Could not get content.' in html_content:
        return True
    return False

def scrape_url_zenrows(url, filename):

    # create filepath
    full_filepath = SCRAPING_FOLDER / filename
    processed_filepath = SCRAPING_FOLDER / 'processed' / filename

    # move it from backup
    if Path(processed_filepath).exists():
            Path(processed_filepath).rename(full_filepath)

    # init counter
    fail_counter = 0

    while not Path(full_filepath).exists():

        fail_counter += 1
        if fail_counter > FAIL_LIMIT:
            return

        client = ZenRowsClient(env('ZENROWS_API_KEY'))

        try:
            response = client.get(url)

            logger.info(f'response code for {url} was {response.status_code}')
            if response.status_code != 200:
                if response.status_code == 404:
                    print(f'{url} not found!')
                    break
                else:
                    print(response.text)
                    continue

            if full_filepath.name.split('.')[-1] == 'pdf':

                # write file
                pdf = open(full_filepath, 'wb')
                pdf.write(response.content)
                pdf.close()

                # validate size
                if full_filepath.stat().st_size < (25*1024):
                    logger.warning(f'{full_filepath} was too small, deleting and trying again')
                    full_filepath.unlink()
                    continue

            else:

                html_content = response.text
                # detect problems with html
                if detect_problem(html_content):
                    continue
                
                # no problems detected
                with open(full_filepath, 'w', encoding='utf-8') as file:
                    file.write(html_content)
            
            logger.info(f"Content successfully saved to {full_filepath}")


        except Exception as e:  # Handle all exceptions

            logger.error(f"An error occurred: {e}")


def scrape_url_brightdata(url, filename):
    """
    Scrape URL using Brightdata's web unlocker API, following same pattern as scrape_url_zenrows.
    """
    # create filepath
    full_filepath = SCRAPING_FOLDER / filename

    # init counter
    fail_counter = 0

    while not Path(full_filepath).exists():
        fail_counter += 1
        if fail_counter > FAIL_LIMIT:
            return

        try:
            # Brightdata web unlocker API configuration
            headers = {
                'Authorization': f'Bearer {env("BRIGHTDATA_API_KEY")}',
                'Content-Type': 'application/json'
            }
            
            # Brightdata web unlocker endpoint
            brightdata_url = 'https://brightdata.com/api/web-unlocker/v1'
            
            # Request payload
            payload = {
                'url': url,
                'render_js': True,  # Enable JavaScript rendering
                'browser': True     # Use browser-like environment
            }

            # Make request to Brightdata
            response = requests.post(brightdata_url, headers=headers, json=payload)

            logger.info(f'response code for {url} was {response.status_code}')
            if response.status_code != 200:
                if response.status_code == 404:
                    print(f'{url} not found!')
                    break
                else:
                    print(response.text)
                    continue

            if full_filepath.name.split('.')[-1] == 'pdf':
                # write file
                pdf = open(full_filepath, 'wb')
                pdf.write(response.content)
                pdf.close()

                # validate size
                if full_filepath.stat().st_size < (25*1024):
                    logger.warning(f'{full_filepath} was too small, deleting and trying again')
                    full_filepath.unlink()
                    continue

            else:
                html_content = response.text
                # detect problems with html
                if detect_problem(html_content):
                    continue
                
                # no problems detected
                with open(full_filepath, 'w', encoding='utf-8') as file:
                    file.write(html_content)
            
            logger.info(f"Content successfully saved to {full_filepath}")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
