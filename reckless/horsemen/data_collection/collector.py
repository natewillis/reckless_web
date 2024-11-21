import logging
from horsemen.data_collection.drf.tracks import get_drf_tracks
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.equibase.entries import parse_equibase_entry_url, get_equibase_entries_files
from horsemen.data_collection.equibase.horse_results import parse_equibase_horse_results_history, get_horse_results_files
from horsemen.data_collection.equibase.charts.extractor import parse_equibase_chart
from horsemen.data_collection.equibase.charts.data_parser import parse_extracted_chart_data

# init logging
logger = logging.getLogger(__name__)


def parse_equibase_files():

    # make sure we can put the file somewhere when we're done
    processed_folder = SCRAPING_FOLDER / 'processed'
    processed_folder.mkdir(exist_ok=True)


    for file_path in SCRAPING_FOLDER.iterdir():
        logger.info(f'processing {file_path.name} from {file_path}')
        if not file_path.is_file():
            continue
        if 'EQB' not in file_path.name:
            continue

        if 'ENTRIES' in file_path.name:
            with open(file_path, 'r') as file:
                html_content = file.read()
            parse_equibase_entry_url(html_content)
            file_path.rename(processed_folder / file_path.name)

        if 'HORSERESULTS' in file_path.name:
            with open(file_path, 'r') as file:
                html_content = file.read()
            parse_equibase_horse_results_history(html_content)
            file_path.rename(processed_folder / file_path.name)

        if 'CHART' in file_path.name and '.pdf' in file_path.name:
            extracted_chart_data = parse_equibase_chart(file_path, True)
            parsed_chart_data = parse_extracted_chart_data(extracted_chart_data)

            #try:
            #    file_path.rename(processed_folder / file_path.name)
            #except PermissionError as p:
            #    logger.error(f'couldnt delete {file_path.name} due to permission error {p}')


def single_run():

    # get the tracks results and entries from drf
    get_drf_tracks()

    # get entries files
    get_equibase_entries_files()
    parse_equibase_files()

    # get horse_results
    get_horse_results_files()
    parse_equibase_files()

    # get the charts
    #get_equibase_chart_pdfs()


