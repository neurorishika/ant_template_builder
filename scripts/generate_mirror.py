# a script to mirror confocal stacks

import os # file handling
import numpy as np # linear algebra
import nibabel as nb # neuroimaging file handling
import glob # file handling
from scipy.ndimage import zoom # image processing
import gc # garbage collection
import argparse # command line arguments

# clear output
os.system('cls' if os.name == 'nt' else 'clear')

# print start string
start_string = 'Kronauer Lab - Microscopy Image Processing Pipeline\n'
start_string += "="*(len(start_string)-1) + '\n'
start_string += 'Confocal Mirror Generator by Rishika Mohanta\n'
start_string += 'Version 1.0.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Generate mirrored images.')
parser.add_argument('-i','--input_dir', type=str, help='path to input directory (must contain .nii.gz files; default: ./cleaned_data)', default="./cleaned_data", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory (default: ./cleaned_data)', default="./cleaned_data", nargs='?')

args = parser.parse_args()

# check if input directory is valid
input_dir = args.input_dir
# check if input directory exists
assert os.path.isdir(input_dir), "Input directory does not exist."

# check if input directory has required files
data_files = list(glob.glob(os.path.join(input_dir, "*.nii.gz")))

assert len(data_files) > 0, "Input directory does not contain any files."

# create output directory if it does not exist
output_dir = args.output_dir
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# function to generate mirrored file name
def generate_mirror_name(x,output_dir=args.output_dir):
    """
    INPUT FORMAT: x = 'path/to/IDENTIFIER.nii.gz'
    OUTPUT FORMAT: '<output_dir>/IDENTIFIER_mirror.nii.gz'
    Note: IDENTIFIER can include underscores and dots.
    """
    x = x.split('.nii.gz')[0]
    x = x + '_mirror.nii.gz'
    # change output directory
    x = os.path.join(output_dir, os.path.basename(x))
    return x

# generate output files
output_files = [generate_mirror_name(i) for i in data_files]

# check if output files already exist, if true warn user that they will be overwritten and remove them
for file in output_files:
    if os.path.isfile(file):
        print("WARNING: Output file {} already exists and will be overwritten.".format(file))
        os.remove(file)

# iterate over files
for file in data_files:
    print("Processing file: {} ({} of {})".format(file, data_files.index(file)+1, len(data_files)))

    # load file
    print("Loading file...", end='')
    img = nb.load(file)
    data = img.get_fdata(dtype=np.float32)
    print("File loaded.")

    # mirror data
    mirrored_data = np.flip(data, axis=0)

    # generate new affine matrix
    new_affine = np.copy(img.affine)
    new_affine[0, :] = -new_affine[0, :]
    
    # generate new image
    mirrored_img = nb.Nifti1Image(mirrored_data, new_affine, img.header)

    # save new image
    print("Saving file...", end='')
    nb.save(mirrored_img, generate_mirror_name(file))
    print("File saved.")

    # clear variables
    del img, data, mirrored_data, mirrored_img

    # run garbage collection
    gc.collect()

print("Done.")

    