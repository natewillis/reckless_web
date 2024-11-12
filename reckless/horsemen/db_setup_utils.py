import os
import csv
from django.db import transaction
from horsemen.models import Tracks

def import_tracks_from_csv(file_path):
    try:
        # Use atomic transaction for batch processing
        with transaction.atomic():
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                
                for row in reader:
                    # Unpack CSV row into variables
                    code, country_code, name, time_zone = row
                    
                    # Set the equibase_chart_name (lowercase, no spaces)
                    equibase_chart_name = name.lower().replace(" ", "")
                    
                    # Prepare data for the track
                    track_data = {
                        "name": name,
                        "time_zone": time_zone,
                        "country": 'USA',
                        "equibase_chart_name": equibase_chart_name,
                    }

                    # Use update_or_create to insert or update
                    Tracks.objects.update_or_create(
                        code=code,
                        defaults=track_data
                    )

        print("Import complete.")
    except Exception as e:
        print(f"Error during import: {str(e)}")


if __name__ == '__main__':
    # import track codes using forward slashes
    csv_path = os.path.join('horsemen', 'resources', 'track_codes.csv')
    print(f"Importing tracks from {csv_path}")
    import_tracks_from_csv(csv_path)
