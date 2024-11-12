# zenrows
from zenrows import ZenRowsClient

# support
from pathlib import Path
from datetime import datetime, timedelta
import time
import random
import os
from horsemen.data_collection.proxies.proxies import create_proxy_list
from horsemen.data_collection.utils import SCRAPING_FOLDER


def detect_problem(html_content):
    if detect_incapsula_block(html_content):
        return True
    
    if detect_zenrows_422(html_content):
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

    while not Path(full_filepath).exists():

        client = ZenRowsClient(os.environ('ZENROWS_API_KEY'))

        try:
            response = client.get(url)

            if response.status_code != 200:
                continue

            if full_filepath.name.split('.')[-1] == 'pdf':

                pdf = open(full_filepath, 'wb')
                pdf.write(response.content)
                pdf.close()

            else:

                html_content = response.text
                # detect problems with html
                if detect_problem(html_content):
                    continue
                
                # no problems detected
                with open(full_filepath, 'w', encoding='utf-8') as file:
                    file.write(html_content)
            
            print(f"Content successfully saved to {full_filepath}")


        except Exception as e:  # Handle all exceptions

            print(f"An error occurred: {e}")
