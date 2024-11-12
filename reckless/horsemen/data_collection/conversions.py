

def drf_breed_word_to_code(breed_name):
    # Mapping dictionary
    breed_codes = {
        "thoroughbred": "TB",
        "quarter horse": "QH",
        "arabian": "AR",
        "paint": "PT",
        "mixed breeds": "MX"
    }

    # Convert the input to lowercase for case-insensitive matching
    breed_name_lower = breed_name.lower()

    # Return the corresponding code or None if not found
    return breed_codes.get(breed_name_lower, None)