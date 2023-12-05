# a script to mirror confocal stacks

import os # file handling
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import glob # file handling
import argparse # command line arguments
from joblib import Parallel, delayed # parallel processing

# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# print start string
start_string = 'Kronauer Lab - Microscopy Image Processing Pipeline\n'
start_string += "="*(len(start_string)-1) + '\n'
start_string += 'Confocal Mirror Generator by Rishika Mohanta\n'
start_string += 'Version 1.1.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Generate mirrored images.')
parser.add_argument('-i','--input_dir', type=str, help='path to input directory (must contain .nrrd files; default: ./cleaned_data/whole_brain/)', default="./cleaned_data/whole_brain/", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory; default: ./cleaned_data/whole_brain/', default="./cleaned_data/whole_brain/", nargs='?')
parser.add_argument('-skip','--skip_existing', type=bool, help='skip existing files (default: True)', default=True, nargs='?')
parser.add_argument('-n','--num_workers', type=int, help='number of workers (default: 1)', default=1, nargs='?')
parser.add_argument('-a', '--axis', type=str, help='axis to mirror (vertical/horizontal; default: horizontal)', default="horizontal", nargs='?')
parser.add_argument('-c','--clean_up', type=bool, help='remove non-error log files (default: True)', default=True, nargs='?')
args = parser.parse_args()

# check if input directory is valid
input_dir = args.input_dir
# check if input directory exists
assert os.path.isdir(input_dir), "Input directory does not exist."

print("Input directory: {}".format(input_dir))

# check if input directory has required files
data_files = list(glob.glob(os.path.join(input_dir, "*.nrrd")))

# remove all files that have '_mirror' in their name
data_files = [i for i in data_files if '_mirror' not in i]

assert len(data_files) > 0, "Input directory does not contain any files."

# create output directory if it does not exist
output_dir = args.output_dir

if output_dir == "":
    output_dir = input_dir
else:
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

print("Output directory: {}".format(output_dir))

# check if axis is valid
axis = args.axis
assert axis in ['vertical', 'horizontal'], "Axis must be either 'vertical' or 'horizontal'."

if axis == 'vertical':
    axis = 1
else:
    axis = 0

# get clean_up
clean_up = args.clean_up

# function to generate mirrored file name
def generate_mirror_name(x,output_dir=output_dir):
    """
    INPUT FORMAT: x = 'path/to/IDENTIFIER.nrrd'
    OUTPUT FORMAT: '<output_dir>/IDENTIFIER_mirror.nrrd'
    Note: IDENTIFIER can include underscores and dots.
    """
    x = x.split('.nrrd')[0]
    x = x + '_mirror.nrrd'
    # change output directory
    x = os.path.join(output_dir, os.path.basename(x))
    return x

# generate output files
output_files = [generate_mirror_name(i) for i in data_files]

# check if output files already exist, if true warn user that they will be overwritten if skip_existing is False and delete them else if skip_existing is True, create a list of files to be skipped
skip_existing = args.skip_existing
skip_list = []
for file in output_files:
    if os.path.isfile(file):
        if skip_existing:
            print("WARNING: Output file {} already exists and will be skipped.".format(file))
            skip_list.append(file)
        else:
            print("WARNING: Output file {} already exists and will be overwritten.".format(file))
            os.remove(file)     

# check if skip list is empty
if len(skip_list) > 0:
    print("WARNING: {} files will be skipped.".format(len(skip_list)))

# copy skipped files to output directory
for file in skip_list:
    # find index of file in output_files
    index = output_files.index(file)
    # get input file name
    input_file = data_files[index]
    # get output directory
    output_dir = os.path.dirname(file)
    # check if input file exists
    assert os.path.isfile(input_file), "Input file {} does not exist.".format(input_file)
    # check if output file exists, if true, check if skip_existing is True, if true, skip file, else overwrite file
    if os.path.isfile(output_dir+'/'+os.path.basename(input_file)):
        if skip_existing:
            print("Skipping {} as it already exists.".format(output_dir+'/'+os.path.basename(input_file)))
            continue
        else:
            print("WARNING: Overwriting {} as it already exists.".format(output_dir+'/'+os.path.basename(input_file)))
            # delete file
            os.remove(file)
    # copy file
    print("Copying {} to {}".format(input_file, output_dir+'/'+os.path.basename(input_file)))
    os.system('cp {} {}'.format(input_file, output_dir+'/'+os.path.basename(input_file)))

# remove all files in skip list from output files and equivalent files in data_files
indices_to_remove = []
for index, file in enumerate(output_files):
    if file in skip_list:
        indices_to_remove.append(index)
output_files = [i for j, i in enumerate(output_files) if j not in indices_to_remove]
input_files = [i for j, i in enumerate(data_files) if j not in indices_to_remove]

# Print number of files to process and their names
print("Number of files to process: {}".format(len(input_files)))
for index, file in enumerate(input_files):
    print("File {}: {} -> {}".format(index, file, output_files[index]))

# define function to run ANTs
def runAntsFlip(input_file,output_file,index):
    """
    Run ANTs PermuteFlipImageOrientationAxes on input_file and save output to output_file.
    """
    print("Processing file: {} ({} of {})".format(input_file, index, len(input_files)))
    
    mirror_file = output_file[:-5] + '.mat'

    # print log file location
    print("Log file: {}".format(output_file[:-5] + '_out.log'))
    print("Error file: {}".format(output_file[:-5] + '_err.log'))

    # # generate mirrored file using ANTs
    # os.system('PermuteFlipImageOrientationAxes 3 {} {} 0 1 2 1 0 0 >{}_out.log 2>{}_err.log'.format(input_file, output_file, output_file[:-5], output_file[:-5]))
    
    # generate mirrored file using ImageMath
    os.system('ImageMath 3 {} ReflectionMatrix {} {} >{}_out.log 2>{}_err.log'.format(mirror_file, input_file, axis, mirror_file[:-4], mirror_file[:-4]))
    os.system('antsApplyTransforms -d 3 -i {} -o {} -t {} -r {} --float 1 >{}_out.log 2>{}_err.log'.format(input_file, output_file, mirror_file, input_file, output_file[:-5], output_file[:-5]))
    
    # check if output file exists
    assert os.path.isfile(output_file), "ERROR: Output file {} does not exist. Check log files for more information.".format(output_file)

if args.num_workers == 1:
    # iterate over files
    for iterator, (input_file, output_file) in enumerate(zip(input_files, output_files)):
        # run ANTs
        runAntsFlip(input_file, output_file, iterator)
elif args.num_workers > 1:
    # check if number of workers is valid
    assert args.num_workers <= len(data_files), "Number of workers must be less than number of files."
    assert args.num_workers <= os.cpu_count(), "Number of workers must be less than or equal to number of cores."
    # run ANTs in parallel
    Parallel(n_jobs=args.num_workers)(delayed(runAntsFlip)(input_file, output_file, iterator) for iterator, (input_file, output_file) in enumerate(zip(data_files, output_files)))
else:
    raise ValueError("Number of workers must be a positive integer.")

if clean_up:
    # Remove all log files with no error messages
    print("Removing empty log files...")

    for file in os.listdir(output_dir):
        if file.endswith("_err.log"):
            if os.stat(os.path.join(output_dir, file)).st_size == 0:
                os.remove(os.path.join(output_dir, file))
                # remove corresponding out file
                try:
                    os.remove(os.path.join(output_dir, file[:-8] + "_out.log"))
                except:
                    print("WARNING: Could not remove corresponding out file for {}. Please check manually.".format(file))

print("Done. Exiting...")