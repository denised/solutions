""" Creating the expected_results.zip file is two steps.  The first step consists of running
a VBA macro inside of the spreadsheet to output all the CSV files.  The second step
collects those CSV files into the format used by testing.  This code does that second step.
It is meant to be run as a script ala `python create_expected_results.py <csv-file-directory>`"""

import argparse
import pathlib
import sys
import zipfile
import pandas as pd


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Combine csv files into expected_results.zip.')
    parser.add_argument('--directory', default="", required=False, help='Directory where csv files are.  Defaults to current directory.')
    args = parser.parse_args()

    directory = pathlib.Path(args.directory)
    fullname = str(directory.resolve().absolute())

    if not directory.is_dir():
        print(f"Argument '{fullname}' does not appear to be a valid directory")
        exit(-1)
    
    # Read the index file
    matches = list(directory.glob('*_index.csv'))
    if len(matches) == 0:
        print(f"Directory {fullname} does not appear to have a file matching *_index.csv file in it.  Did you run the Excel macro?")
    
    if len(matches) > 1:
        print(f"Directory {fullname} has multiple files matching *_index.csv.  Please clean up and try again.")
    
    filedata = pd.read_csv(matches[0], header=None, names=['file','scenario','tab'])

    # Create the zip file
    # ZIP_LZMA and ZIP_BZIP2 give better compression but are not supported by the MacOS zip client
    # so we use ZIP_DEFLATED for maximum compatibility
    zipfilename = directory / 'expected.zip'
    zip_f = zipfile.ZipFile(file=zipfilename, mode='w', compression=zipfile.ZIP_DEFLATED)

    # Put stuff in the zip file
    for _, row in filedata.iterrows():
        filename = directory / row['file']
        arcname = row['scenario'] + '/' + row['tab']
        zip_f.write(filename=filename, arcname=arcname)
    
    zip_f.close()