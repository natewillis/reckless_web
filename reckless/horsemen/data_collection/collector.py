from horsemen.data_collection.drf.tracks import get_drf_tracks
from horsemen.data_collection.drf.entries import update_all_races_with_drf_entries
from horsemen.data_collection.utils import SCRAPING_FOLDER
from horsemen.data_collection.equibase.entries import parse_equibase_entry_url
from horsemen.data_collection.equibase.horse_results import parse_equibase_horse_results_history

def parse_equibase_files():

    # make sure we can put the file somewhere when we're done
    processed_folder = SCRAPING_FOLDER / 'processed'
    processed_folder.mkdir(exist_ok=True)

    for file_path in SCRAPING_FOLDER.iterdir():
        print(f'processing {file_path.name} from {file_path}')
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
            #file_path.rename(processed_folder / file_path.name)


def single_run():

    # get the tracks
    get_drf_tracks()

    # get the entries
    update_all_races_with_drf_entries()


