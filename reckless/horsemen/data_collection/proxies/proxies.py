import requests
import re
from bs4 import BeautifulSoup
from horsemen.data_collection.utils import SCRAPING_FOLDER

def create_proxy_list():

    # make the folder if necessary
    SCRAPING_FOLDER.mkdir(exist_ok=True)

    # create proxy filename
    filename = SCRAPING_FOLDER / 'proxies_list.txt'

    # The URL to fetch proxy data
    url = "https://spys.me/proxy.txt"

    # Regular expression to identify IP addresses
    regex = r"[0-9]+(?:\.[0-9]+){3}:[0-9]+"

    # Fetch the proxy list from the URL
    response = requests.get(url)

    # Ensure request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return

    # Split text into lines for processing
    lines = response.text.splitlines()

    # Open the file in write mode
    with open(filename, 'w') as file:
        for line in lines:
            # Search for an IP address and extract necessary components
            match = re.match(regex, line)
            if match:
                # Assume the line format is: IP:Port CountryCode-Anonymity-SSL-Google
                parts = line.split()  # Split line into parts
                if len(parts) > 2:
                    detail_parts = parts[1].split('-')
                    if len(detail_parts) > 2:
                        ssl_support = detail_parts[2]  # Extract the third part after the port
                        if 'S' in ssl_support:
                            print(match.group(), file=file)

            
    # get proxies form proxylist
    # URL to fetch proxy data
    url = "https://free-proxy-list.net/"

    # Fetch the webpage content
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Select all td elements within the table rows
    td_elements = soup.select('.fpl-list .table tbody tr td')

    # Open the file to append the filtered proxies
    with open(filename, "a") as myfile:
        for i in range(0, len(td_elements), 8):
            # Check if the seventh cell contains 'yes'
            if td_elements[i + 6].text.strip().lower() == 'yes':
                # Extract the IP and port
                ip = td_elements[i].text.strip()
                port = td_elements[i + 1].text.strip()
                
                # Format the proxy string
                proxy = f"{ip}:{port}"
                
                # Write the proxy to the file
                print(proxy, file=myfile)


if __name__ == "__main__":
    create_proxy_list()