# a script to generate a refined brain template from a low quality brain template


import os # file handling
import numpy as np # linear algebra
import glob # file handling
import argparse # command line arguments
import datetime # date and time
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# print start string
start_string = 'Kronauer Lab - Microscopy Image Processing Pipeline\n'
start_string += "="*(len(start_string)-1) + '\n'
start_string += 'Refined Brain Template Generator by Rishika Mohanta\n'
start_string += 'Version 1.0.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Resample generated brain template to a target voxel size.')
parser.add_argument('-i','--input_dir', type=str, help='path to results directory (must contain syn directory and deformed files; default: latest directory in results/)', default="", nargs='?')
parser.add_argument('-meta','--metadata', type=str, help='path to metadata file (default: ./metadata.csv)', default="./metadata.csv", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory (default: ./refined_templates/)', default="./refined_templates/", nargs='?')
parser.add_argument('-t','--keep_temp', type=bool, help='keep temporary files (default: False)', default=False, nargs='?')
args = parser.parse_args()

# get timestamp
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")

## ARGUMENT VERIFICATION

# create output directory if it does not exist
output_dir = args.output_dir
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
# make a temporary directory (temp_DDMMYY_HHMM) inside output directory
temp_dir = os.path.join(output_dir, f"temp_{timestamp}")
if not os.path.isdir(temp_dir):
    os.makedirs(temp_dir)
else:
    # if temp directory already exists, delete it and create a new one
    os.system(f"rm -rf {temp_dir}")
    os.makedirs(temp_dir)

# check if output file (refined_template_YYYYMMDD_HHMM.nii.gz) already exists
output_file = os.path.join(output_dir, f"refined_template_{timestamp}.nii.gz")

assert not os.path.isfile(output_file), "Output file already exists. Please delete it or change the timestamp."

# check if metadata file exists
metadata_file = args.metadata
assert os.path.isfile(metadata_file), "Metadata file does not exist."

# read metadata file
metadata = pd.read_csv(metadata_file)

# Keep only the columns we need (Clean name and Egocentric Leaning)
metadata_original = metadata[['Clean Name', 'Refinement Inclusion']]

# convert to map dictionary
inclusion = metadata_original.set_index('Clean Name').to_dict()['Refinement Inclusion']
# convert values to boolean
inclusion = {key: bool(value) for key, value in inclusion.items()}
print("Inclusion dictionary: {}".format(inclusion))

print("Metadata file: {}".format(metadata_file))

# check if input directory is valid
input_dir = args.input_dir

# if input directory is empty, find latest directory in results directory
if input_dir == "":
    # get list of all directories in results/
    directory_list = list(glob.glob(os.path.join("results", "*")))
    directory_list = [d for d in directory_list if os.path.isdir(d)]
    # get latest directory
    input_dir = max(directory_list, key=os.path.getctime)


# check if input directory exists
assert os.path.isdir(input_dir), "Input directory does not exist."

# check if input directory has required files
directory_list = list(glob.glob(os.path.join(input_dir, "*")))
directory_list = [d for d in directory_list if os.path.isdir(d)]

# make sure there is syn directory
assert os.path.isdir(os.path.join(input_dir, "syn")), "Input directory does not contain syn directory."

# get list of all *deformed.nii.gz files in syn directory
nii_files = list(glob.glob(os.path.join(input_dir, "syn", "*deformed.nii.gz")))


# create function to get original name
def get_original_name(file):
    # remove everything after _resampled
    original_name = file.split("_resampled")[0]
    # remove "complete_" from the beginning
    original_name = original_name.replace("complete_", "")
    # add .nrrd extension
    original_name += ".nrrd"
    return original_name

# get list of all original files
original_files = [get_original_name(file) for file in nii_files]

# check if each original file exists in keys of inclusion
is_included = []
for original_file in original_files:
    assert original_file in inclusion, f"Original file {original_file} not found in metadata file."
    print(f"Found {original_file} in metadata file.")
    is_included.append(inclusion[original_file])

# check if there is at least one file to be included
assert any(is_included), "No files to be included in refinement. Please check metadata file."

print("Input directory: {}".format(input_dir))
print("Output directory: {}".format(output_dir))
print("Temporary directory: {}".format(temp_dir))

print("Number of files to be included in refinement: {}".format(sum(is_included)))

# loop through all nii_files and copy all included files to temp directory
all_files = []
for index, file in enumerate(nii_files):
    # if file is included, copy it to temp directory
    if is_included[index]:
        print("Copying file {} to temporary directory...".format(file))
        # copy file to temp directory
        os.system(f"cp {file} {temp_dir}")
        # Normalize the temp file using ANTs
        print("Normalizing file {}...".format(file))
        os.system(f"ImageMath 3 {os.path.join(temp_dir, os.path.basename(file))} Normalize {os.path.join(temp_dir, os.path.basename(file))}")
        # add file to all_files
        all_files.append(os.path.join(temp_dir, os.path.basename(file)))

# generate a wildcard string for all files
all_files = " ".join(all_files)

# Average all files using ANTs
print("Averaging all files to generate low quality upsampled template...")

log_file = os.path.join(temp_dir, "average_out.log")
err_file = os.path.join(temp_dir, "average_err.log")

print(f"Log file: {log_file}")
print(f"Error file: {err_file}")

os.system(f"AverageImages 3 {output_file} 0 {all_files} > {log_file} 2> {err_file}")

# check if output file exists
assert os.path.isfile(output_file), "Output file not found. Please check log file."


# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# Remove temp directory
if not args.keep_temp:
    print("Removing temporary files...")
    os.system(f"rm -rf {temp_dir}")

print("Done with generating refined template. Exiting...")




