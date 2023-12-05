# a script to reset asymmetrized resampled images

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
start_string += 'Reset Asymmetrize Resampled Images by Rishika Mohanta\n'
start_string += 'Version 1.1.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Reset asymmetrized confocal images from backup and diff directories.')
parser.add_argument('-i','--input_dir', type=str, help='path to input directory (must contain .nrrd files; default: ./resampled_data/whole_brain/)', default="./resampled_data/whole_brain/", nargs='?')
parser.add_argument('-b','--backup_dir', type=str, help='path to backup directory (default: <input_dir>/backup/)', default="", nargs='?')
parser.add_argument('-n','--quality_affine', type=bool, help='(ARCHIVED) whether to use quality affine (default: False)', default=False, nargs='?')
parser.add_argument('-m','--diff_dir', type=str, help='(ARCHIVED) path to diff directory (default: <input_dir>/diff/)', default="", nargs='?')
args = parser.parse_args()

# check if input directory is valid
input_dir = args.input_dir
# check if input directory exists
assert os.path.isdir(input_dir), "Input directory does not exist."

print("Input directory: {}".format(input_dir))

# check if input directory has required files
data_files = list(glob.glob(os.path.join(input_dir, "*.nrrd")))

assert len(data_files) > 0, "Input directory does not contain any files."

# check if backup directory is valid and has required files
backup_dir = args.backup_dir

if backup_dir == "":
    backup_dir = os.path.join(input_dir, "backup")

assert os.path.isdir(backup_dir), "Backup directory does not exist."

backup_files = list(glob.glob(os.path.join(backup_dir, "*.nrrd")))
assert len(backup_files) > 0, "Backup directory does not contain any files."


# get quality affine
quality_affine = args.quality_affine

# check if quality affine is valid
assert type(quality_affine) == bool, "Quality affine must be either True or False."

if quality_affine:
    print("Using quality affine.")

    # check if diff directory is valid and has required files
    diff_dir = args.diff_dir

    if diff_dir == "":
        diff_dir = os.path.join(input_dir, "diff")

    assert os.path.isdir(diff_dir), "Diff directory does not exist."

    diff_files = list(glob.glob(os.path.join(diff_dir, "*.nrrd")))

    assert len(diff_files) > 0, "Diff directory does not contain any files."

else:
    print("Not using quality affine.")

# move all files from backup directory to input directory

for f in backup_files:
    os.rename(f, os.path.join(input_dir, os.path.basename(f)))

# move all files from diff directory to input directory
if quality_affine:
    for f in diff_files:
        os.rename(f, os.path.join(input_dir, os.path.basename(f)))

# delete backup directory if it is empty
if len(os.listdir(backup_dir)) == 0:
    os.rmdir(backup_dir)

# delete diff directory if it is empty
if quality_affine:
    if len(os.listdir(diff_dir)) == 0:
        os.rmdir(diff_dir)

# print end string
end_string = 'Done. Exiting...\n'

print(end_string)
    