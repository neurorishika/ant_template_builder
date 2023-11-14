# a script to generate a high resolution brain template from low resolution brain templates


import os # file handling
import numpy as np # linear algebra
import glob # file handling
import argparse # command line arguments
from joblib import Parallel, delayed # parallel processing
import datetime # date and time

# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# print start string
start_string = 'Kronauer Lab - Microscopy Image Processing Pipeline\n'
start_string += "="*(len(start_string)-1) + '\n'
start_string += 'High Resolution Brain Template Generator by Rishika Mohanta\n'
start_string += 'Version 1.0.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Resample generated brain template to a target voxel size.')
parser.add_argument('-i','--input_dir', type=str, help='path to results directory (must contain syn directory and complete_template.nii.gz files; default: latest directory in results/)', default="", nargs='?')
parser.add_argument('-db','--clean_database', type=str, help='path to clean database directory (must contain .nrrd files; default: ./cleaned_data)', default="./cleaned_data", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory (default: ./highres_templates)', default="./highres_templates", nargs='?')
parser.add_argument('-v','--target_voxel_size', type=str, help='target voxel size in microns (e.g. 0.8x0.8x0.8)', default="0.8x0.8x0.8", nargs='?')
parser.add_argument('-n','--num_workers', type=int, help='number of workers to use (default: 1)', default=1, nargs='?')
parser.add_argument('-t','--keep_temp', type=bool, help='keep temporary files (default: False)', default=False, nargs='?')
args = parser.parse_args()

# get timestamp YYYYMMDD_HHMM
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')

## ARGUMENT VERIFICATION

# check if target voxel size is valid
target_voxel_size = args.target_voxel_size
original_target_voxel_size = target_voxel_size
target_voxel_size = target_voxel_size.split('x')
assert len(target_voxel_size) == 3, "Target voxel size must be in the format '0.8x0.8x0.8'."

try:
    target_voxel_size = [float(i) for i in target_voxel_size]
except:
    raise ValueError("Target voxel size must be in the format '0.8x0.8x0.8'.")

# check if target voxel size is positive
assert all(i > 0 for i in target_voxel_size), "Target voxel size must be positive."

# create output directory if it does not exist
output_dir = args.output_dir
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)
# make a temporary directory (temp_DDMMYY_HHMM_<target_voxel_size>) inside output directory
temp_dir = os.path.join(output_dir, f"temp_{timestamp}_{original_target_voxel_size}")
if not os.path.isdir(temp_dir):
    os.makedirs(temp_dir)
else:
    # if temp directory already exists, delete it and create a new one
    os.system(f"rm -rf {temp_dir}")
    os.makedirs(temp_dir)

# check if output file (obiroi_template_DDMMYY_HHMM_<target_voxel_size>.nrrd) already exists
output_file = os.path.join(output_dir, f"obiroi_template_{timestamp}_{original_target_voxel_size}.nrrd")

# check if clean database directory is valid
clean_database_dir = args.clean_database

# check if clean database directory exists
assert os.path.isdir(clean_database_dir), "Clean database directory does not exist."


# check if input directory is valid
input_dir = args.input_dir

# if input directory is not specified, use latest directory in results/
if input_dir == "":
    # get list of all directories in results/
    directory_list = os.listdir("results")
    directory_list = [d for d in directory_list if os.path.isdir(d)]
    # get latest directory
    input_dir = max(directory_list, key=os.path.getctime)

# check if input directory exists
assert os.path.isdir(input_dir), "Input directory does not exist."

# check if input directory has required files
directory_list = os.listdir(input_dir)
directory_list = [d for d in directory_list if os.path.isdir(d)]

# make sure there is syn directory
assert os.path.isdir(os.path.join(input_dir, "syn")), "Input directory does not contain syn directory."

# make sure there is complete_template.nii.gz file
assert os.path.isfile(os.path.join(input_dir, "complete_template.nii.gz")), "Input directory does not contain complete_template.nii.gz file."

# get list of all *.nii.gz files in syn directory
# nii_files = list(glob.glob(os.path.join(input_dir, "syn", "*.nii.gz")))
nii_files = os.listdir(os.path.join(input_dir, "syn"))
nii_files = [os.path.join(input_dir, "syn", file) for file in nii_files if file.endswith(".nii.gz")]

# remove any files that start with complete_template
nii_files = [file for file in nii_files if not os.path.basename(file).startswith("complete_template")]

# create function to get original name
def get_original_name(file):
    # get basename
    file = os.path.basename(file)
    # remove everything after _resampled
    original_name = file.split("_resampled")[0]
    # remove "complete_" from the beginning
    original_name = original_name.replace("complete_", "")
    # add .nrrd extension
    original_name += ".nrrd"
    return original_name

# create function to get basefile names
def get_basefile_name(file):
    # get basename
    file = os.path.basename(file)
    # remove the words "Warp", "InverseWarp", "deformed", "repaired"
    basefile = file.replace("InverseWarp", "").replace("Warp", "").replace("deformed", "").replace("repaired", "")
    return basefile[:-7]

# get list of all basefile names
basefiles = [get_basefile_name(file) for file in nii_files]

# remove duplicates
basefiles = list(set(basefiles))

# for every basefile, make sure there is a Warp file
for basefile in basefiles:
    assert os.path.isfile(os.path.join(input_dir, "syn", basefile + "Warp.nii.gz")), f"Input directory does not contain {basefile}Warp.nii.gz file."
    print(f"Found {basefile}Warp.nii.gz file.")

# for every basefile, make sure there is an Affine.txt.gz or Affine.txt file
for basefile in basefiles:
    assert os.path.isfile(os.path.join(input_dir, "syn", basefile + "Affine.txt.gz")) or os.path.isfile(os.path.join(input_dir, "syn", basefile + "Affine.txt")), f"Input directory does not contain {basefile}Affine.txt.gz or {basefile}Affine.txt file."
    # if there is an Affine.txt.gz file, convert it to Affine.txt
    if os.path.isfile(os.path.join(input_dir, "syn", basefile + "Affine.txt.gz")):
        os.system(f"gunzip {os.path.join(input_dir, 'syn', basefile + 'Affine.txt.gz')}")
        assert os.path.isfile(os.path.join(input_dir, "syn", basefile + "Affine.txt")), f"Input directory does not contain {basefile}Affine.txt file as expected. Please check if the file was correctly unzipped."
    print(f"Found {basefile}Affine.txt file.")

# get a list of all original files
original_files = [get_original_name(file) for file in nii_files]

# check if each original file exists in clean database directory
for original_file in original_files:
    assert os.path.isfile(os.path.join(clean_database_dir, original_file)), f"Original file {original_file} not found in clean database directory."
    print(f"Found {original_file} in clean database directory.")


# create a dictionary to store basefile for each original file
basefile_dict = {}

# for each original file, find the basefile
for original_file in original_files:
    # find the matching basefile
    temp = original_file.replace(".nrrd", "")
    temp = "complete_" + temp
    basefile = [file for file in basefiles if file.startswith(temp)]
    # make sure there is only one basefile
    assert len(basefile) == 1, f"Could not find basefile for {original_file}. Make sure there is only one basefile for each original file."
    # add basefile to dictionary
    basefile_dict[original_file] = basefile[0]

print("All files found in input directory and clean database directory.")

## RESAMPLING

# make a upsampled_template.nii.gz file in temp directory using ResampleImageBySpacing from ANTs

# target resolution in microns (x, y, z)
target_resolution = np.array(target_voxel_size)
print(f"Target resolution: {target_resolution[0]} μm x {target_resolution[1]} μm x {target_resolution[2]} μm")

print("Resampling template to generate low quality upsampled template...")

log_file = os.path.join(temp_dir, "upsampled_template_out.log")
err_file = os.path.join(temp_dir, "upsampled_template_err.log")
print(f"Log file: {log_file}")
print(f"Error file: {err_file}")

complete_template_file = os.path.join(input_dir, "complete_template.nii.gz")
upsampled_template_file = os.path.join(temp_dir, "upsampled_template.nii.gz")

os.system(f"ResampleImageBySpacing 3 {complete_template_file} {upsampled_template_file} {target_resolution[0]} {target_resolution[1]} {target_resolution[2]} 0 0 0 > {log_file} 2> {err_file}")

## WARPING
# WarpImageMultiTransform 3 synA647_LL_L12_200727.nrrd  applytransformonoriginaltoupsampled_template.nii.gz -R upsampled_template.nii.gz complete_synA647_LL_L12_200727_resampled_0.6x0.6x0Warp.nii.gz complete_synA647_LL_L12_200727_resampled_0.6x0.6x0Affine.txt



# define a function to warp a file
def warp_file(index):
    # print progress
    print(f"Warp file {index+1} of {len(original_files)}")

    # print original file, basefile, and warped file
    original_file = os.path.join(clean_database_dir, original_files[index])
    basefile = os.path.join(input_dir, "syn", basefile_dict[original_files[index]])
    warped_file = os.path.join(temp_dir, f"{original_files[index][:-5]}_warped.nii.gz")

    print(f"Original file: {original_file}")
    print(f"Basefile: {basefile}")
    print(f"Warped file: {warped_file}")

    # print log file location
    log_file = os.path.join(temp_dir, f"{original_files[index][:-5]}_out.log")
    err_file = os.path.join(temp_dir, f"{original_files[index][:-5]}_err.log")
    print(f"Log file: {log_file}")
    print(f"Error file: {err_file}")

    # warp data using ANTs
    os.system(f"WarpImageMultiTransform 3 {original_file} {warped_file} -R {upsampled_template_file} {basefile}Warp.nii.gz {basefile}Affine.txt > {log_file} 2> {err_file}")

    
if args.num_workers == 1:
    # resample each file sequentially
    for index in range(len(original_files)):
        warp_file(index)
else:
    assert args.num_workers > 1, "Number of workers must be greater than 1."
    assert args.num_workers <= len(original_files), "Number of workers must be less than or equal to number of files."
    assert args.num_workers <= os.cpu_count(), "Number of workers must be less than or equal to number of CPUs."
    # resample each file in parallel using joblib
    Parallel(n_jobs=args.num_workers)(delayed(warp_file)(index) for index in range(len(original_files)))

## AVERAGING

# define a function to average all warped files using ANTs
print("Averaging all warped files to generate high quality upsampled template...")
log_file = os.path.join(temp_dir, "average_out.log")
err_file = os.path.join(temp_dir, "average_err.log")
print(f"Log file: {log_file}")
print(f"Error file: {err_file}")

final_template_file = os.path.join(output_dir, f"obiroi_template_{timestamp}_{original_target_voxel_size}.nrrd")

regex = os.path.join(temp_dir, "*_warped.nii.gz")

# run AverageImages from ANTs
os.system(f"AverageImages 3 {final_template_file} 1 {regex} > {log_file} 2> {err_file}")

# verify that final template file exists
assert os.path.isfile(final_template_file), "Final template file was not generated. Please check log and error files."
    
# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# Remove temp directory
if not args.keep_temp:
    print("Removing temporary files...")
    os.system(f"rm -rf {temp_dir}")

print("Done with generating high resolution brain template. Exiting...")




