# cleans a comma separated CSV used in connections game, ensuring that the file is in the correct format

import csv
import os
import tempfile


def clean_csv(filepath):
    seen_strings = set()
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='')
    with open(filepath, 'r') as infile, temp_file as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            # Remove rows with less than 5 strings
            if len(row) < 5:
                continue
            # Check for duplicate strings
            if any(string in seen_strings for string in row):
                continue
            # Add strings to seen_strings set
            seen_strings.update(row)
            # Write row to cleaned CSV
            writer.writerow(row)
    os.replace(temp_file.name, filepath)


# Call the function with the file path
if __name__ == '__main__':
    clean_csv('../Entertainment.csv')
