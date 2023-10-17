# a script to resample confocal stacks to a target voxel size

import os # file handling
import numpy as np # linear algebra
import glob # file handling
import argparse # command line arguments
from joblib import Parallel, delayed # parallel processing

# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# print start string
start_string = 'Kronauer Lab - Microscopy Image Processing Pipeline\n'
start_string += "="*(len(start_string)-1) + '\n'
start_string += 'Confocal Resampler by Rishika Mohanta\n'
start_string += 'Version 1.1.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Resample confocal stacks to a target voxel size.')
parser.add_argument('-i','--input_dir', type=str, help='path to input directory (must contain .nrrd files; default: ./cleaned_data)', default="./cleaned_data", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory (default: ./resampled_data)', default="./resampled_data", nargs='?')
parser.add_argument('-v','--target_voxel_size', type=str, help='target voxel size in microns (e.g. 0.8x0.8x0.8)', default="0.8x0.8x0.8", nargs='?')
parser.add_argument('-n','--num_workers', type=int, help='number of workers to use (default: 1)', default=1, nargs='?')
parser.add_argument('-t','--type', type=str, help='type of resampling (spacing or size; default: spacing)', default="spacing", nargs='?')
args = parser.parse_args()

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

# check if input directory is valid
input_dir = args.input_dir
# check if input directory exists
assert os.path.isdir(input_dir), "Input directory does not exist."

# check if input directory has required files
data_files = list(glob.glob(os.path.join(input_dir, "*.nrrd")))

assert len(data_files) > 0, "Input directory does not contain any files."

# create output directory if it does not exist
output_dir = args.output_dir
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

output_files = list(glob.glob(os.path.join(input_dir, "*.nrrd")))

# append '_resampled' to output files
output_files = [os.path.join(output_dir, os.path.basename(f).replace('.nrrd', f'_resampled_{original_target_voxel_size}.nrrd')) for f in output_files]

# check if output files already exist
for f in output_files:
    if os.path.isfile(f):
        print(f"Output file {f} already exists. Will be overwritten.")
        os.remove(f)

# check type of resampling
resampling_type = args.type
assert resampling_type in ['spacing', 'size'], "Resampling type must be 'spacing' or 'size'."

# define a function to resample a file
def resample_file(index):
    # print progress
    print(f"Resampling file {index+1} of {len(data_files)}")

    # target resolution in microns (x, y, z)
    target_resolution = np.array(target_voxel_size)
    print(f"Target resolution: {target_resolution[0]} μm x {target_resolution[1]} μm x {target_resolution[2]} μm")

    # print log file location
    print("Log file: {}".format(output_files[index][:-5] + '_out.log'))
    print("Error file: {}".format(output_files[index][:-5] + '_err.log'))

    # resample data using ANTs
    if resampling_type == 'size':
        os.system('ResampleImage 3 {} {} {}x{}x{} 0 0 6 >{}_out.log 2>{}_err.log'.format(data_files[index], output_files[index], target_resolution[0], target_resolution[1], target_resolution[2], output_files[index][:-5], output_files[index][:-5]))
    if resampling_type == 'spacing':
        os.system('ResampleImageBySpacing 3 {} {} {} {} {}'.format(data_files[index], output_files[index], target_resolution[0], target_resolution[1], target_resolution[2]))   

if args.num_workers == 1:
    # resample each file sequentially
    for index in range(len(data_files)):
        resample_file(index)
else:
    assert args.num_workers > 1, "Number of workers must be greater than 1."
    assert args.num_workers <= len(data_files), "Number of workers must be less than or equal to number of files."
    assert args.num_workers <= os.cpu_count(), "Number of workers must be less than or equal to number of CPUs."
    # resample each file in parallel using joblib
    Parallel(n_jobs=args.num_workers)(delayed(resample_file)(index) for index in range(len(data_files)))
    
# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# Remove all empty log files

print("Removing empty log files...")

for file in os.listdir(output_dir):
    if file.endswith("_out.log") or file.endswith("_err.log"):
        if os.stat(os.path.join(output_dir, file)).st_size == 0:
            os.remove(os.path.join(output_dir, file))

print("All files resampled. Exiting...")




