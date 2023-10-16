# a script to asymmetrize resampled images

import os # file handling
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import glob # file handling
import argparse # command line arguments

# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# print start string
start_string = 'Kronauer Lab - Microscopy Image Processing Pipeline\n'
start_string += "="*(len(start_string)-1) + '\n'
start_string += 'Asymmetrize Resampled Images by Rishika Mohanta\n'
start_string += 'Version 1.1.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Filter confocal images to keep only uniformly asymmetric brains.')
parser.add_argument('-i','--input_dir', type=str, help='path to input directory (must contain .nrrd files; default: ./resampled_data/)', default="./resampled_data/", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory; default: same as input directory', default="", nargs='?')
parser.add_argument('-b','--backup_dir', type=str, help='path to backup directory (default: <input_dir>/backup/)', default="", nargs='?')
parser.add_argument('-m','--diff_dir', type=str, help='path to diff directory (default: <input_dir>/diff/)', default="", nargs='?')
parser.add_argument('-meta','--metadata', type=str, help='path to metadata file (default: ./metadata.csv)', default="./metadata.csv", nargs='?')
parser.add_argument('-lr','--left_or_right', type=str, help='left or right (default: left)', default="left", nargs='?')
parser.add_argument('-q','--quality_affine', type=bool, help='whether to use quality affine (default: True)', default=True, nargs='?')
args = parser.parse_args()

# check if input directory is valid
input_dir = args.input_dir
# check if input directory exists
assert os.path.isdir(input_dir), "Input directory does not exist."

print("Input directory: {}".format(input_dir))

# check if input directory has required files
data_files = list(glob.glob(os.path.join(input_dir, "*.nrrd")))

assert len(data_files) > 0, "Input directory does not contain any files."

# create output directory if it does not exist
output_dir = args.output_dir

if output_dir == "":
    output_dir = input_dir
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

print("Output directory: {}".format(output_dir))

# create backup directory if it does not exist
backup_dir = args.backup_dir

if backup_dir == "":
    backup_dir = os.path.join(input_dir, "backup")
if not os.path.isdir(backup_dir):
    os.makedirs(backup_dir)

print("Backup directory: {}".format(backup_dir))

# check if metadata file exists
metadata_file = args.metadata
assert os.path.isfile(metadata_file), "Metadata file does not exist."

# read metadata file
metadata = pd.read_csv(metadata_file)

# Keep only the columns we need (Clean name and Egocentric Leaning)
metadata_original = metadata[['Clean Name', 'Egocentric Leaning','Skip Affine']]

# convert to map dictionary
metadata = metadata_original.set_index('Clean Name').to_dict()['Egocentric Leaning']
manually_skipped = metadata_original.set_index('Clean Name').to_dict()['Skip Affine']
print("Metadata file: {}".format(metadata_file))

# make sure manually skipped is integer 0 or 1
for key in manually_skipped:
    assert manually_skipped[key] in [0,1], "Manually skipped must be 0 or 1."
    # convert to boolean
    manually_skipped[key] = bool(manually_skipped[key])

# get left or right
left_or_right = args.left_or_right

# check if left or right is valid
assert left_or_right in ['left', 'right'], "Left or right must be either 'left' or 'right'."

# get quality affine
quality_affine = args.quality_affine

# check if quality affine is valid
assert type(quality_affine) == bool, "Quality affine must be either True or False."

if quality_affine:
    print("Keeping only {} brain in affine and both {} and symmetric brains in diffeomorphic.".format(left_or_right, left_or_right))
else:
    print("Keeping only {} or symmetric brains.".format(left_or_right))

# create diff directory if it does not exist
diff_dir = args.diff_dir

if diff_dir == "":
    diff_dir = os.path.join(input_dir, "diff")
if not os.path.isdir(diff_dir):
    os.makedirs(diff_dir)
    

# loop through all files
for data_file in data_files:
    # get clean name
    clean_name = os.path.basename(data_file)
    # check if it is a mirror file
    is_mirror = '_mirror' in clean_name
    # remove everything after "_mirror" or "_resampled" and add ".nrrd"
    clean_name = clean_name.split("_resampled")[0].split("_mirror")[0] + ".nrrd"
    # check if clean name is in metadata
    assert clean_name in metadata.keys(), "Clean name {} not found in metadata.".format(clean_name)
    # get egocentric leaning
    egocentric_leaning = metadata[clean_name]
    # get manually skipped
    manually_skipped_this = manually_skipped[clean_name]
    # check if egocentric leaning is valid
    assert egocentric_leaning in ['left', 'right', 'sym'], "Egocentric leaning must be either 'left', 'right', or 'sym'."
    # see if we need to keep this file
    if not quality_affine:
        if egocentric_leaning == left_or_right or egocentric_leaning == 'sym':
            # check if mirror file
            if is_mirror:
                # move to backup directory
                os.rename(data_file, os.path.join(backup_dir, os.path.basename(data_file)))
            else:
                # move to output directory
                os.rename(data_file, os.path.join(output_dir, os.path.basename(data_file)))
        else:
            # check if mirror file
            if is_mirror:
                # move to output directory
                os.rename(data_file, os.path.join(output_dir, os.path.basename(data_file)))
            else:
                # move to backup directory
                os.rename(data_file, os.path.join(backup_dir, os.path.basename(data_file)))
    else:
        if egocentric_leaning == left_or_right:
            # check if mirror file
            if is_mirror:
                # move to backup directory
                os.rename(data_file, os.path.join(backup_dir, os.path.basename(data_file)))
            else:
                # move to output directory
                os.rename(data_file, os.path.join(output_dir, os.path.basename(data_file)))
        elif egocentric_leaning == 'sym' or manually_skipped_this == True:
            # move to diff directory if not mirror file else move to backup directory
            if is_mirror:
                # move to backup directory
                os.rename(data_file, os.path.join(backup_dir, os.path.basename(data_file)))
            else:
                # move to diff directory
                os.rename(data_file, os.path.join(diff_dir, os.path.basename(data_file)))
        else:
            # check if mirror file
            if is_mirror:
                # move to output directory
                os.rename(data_file, os.path.join(output_dir, os.path.basename(data_file)))
            else:
                # move to backup directory
                os.rename(data_file, os.path.join(backup_dir, os.path.basename(data_file)))

# print end string
end_string = 'Done processing all files. Exiting...\n'

print(end_string)

    