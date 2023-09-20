# a script to resample confocal stacks to a target voxel size

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
start_string += 'Confocal Resampler by Rishika Mohanta\n'
start_string += 'Version 1.0.0\n'

print(start_string)

# parse command line arguments
parser = argparse.ArgumentParser(description='Resample confocal stacks to a target voxel size.')
parser.add_argument('-i','--input_dir', type=str, help='path to input directory (must contain .nii.gz files; default: ./cleaned_data)', default="./cleaned_data", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory (default: ./resampled_data)', default="./resampled_data", nargs='?')
parser.add_argument('-v','--target_voxel_size', type=str, help='target voxel size in microns (e.g. 0.8x0.8x0.8)', default="0.8x0.8x0.8", nargs='?')
# parser.add_argument('-m','--mirror', type=bool, help='generate mirrored images (default: False)', default=False, nargs='?')

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
data_files = list(glob.glob(os.path.join(input_dir, "*.nii.gz")))
assert len(data_files) > 0, "Input directory does not contain any files."

# create output directory if it does not exist
output_dir = args.output_dir
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

output_files = glob.glob(os.path.join(input_dir, "*.nii.gz"))
# append '_resampled' to output files
output_files = [os.path.join(output_dir, os.path.basename(f).replace('.nii.gz', f'_resampled_{original_target_voxel_size}.nii.gz')) for f in output_files]

# def generate_mirror_name(x):
#     """
#     INPUT FORMAT: x = 'path/to/IDENTIFIER_resampled_0.8x0.8x0.8.nii.gz'
#     OUTPUT FORMAT: 'path/to/IDENTIFIER_resampled_mirror_0.8x0.8x0.8.nii.gz'
#     """
#     x = x.split('_')
#     x = x[0:-1] + ['mirror'] + x[-1:]
#     return '_'.join(x)

# check if output files already exist
for f in output_files:
    if os.path.isfile(f):
        print(f"Output file {f} already exists. Will be overwritten.")
        os.remove(f)
    # check if mirrored output files already exist
    # if args.mirror:
    #     if os.path.isfile(generate_mirror_name(f)):
    #         print(f"Output file {generate_mirror_name(f)} already exists. Will be overwritten.")
    #         os.remove(generate_mirror_name(f))

# generate mirrored images
generate_mirror = args.mirror


# resample each file
for index in range(len(data_files)):

    # print progress
    print(f"Resampling file {index+1} of {len(data_files)}")
    print("="*len(f"Resampling file {index+1} of {len(data_files)}"))
          

    full_data = nb.load(data_files[index])
    print(f"Data file: {data_files[index]}")

    # get pixel dimensions in microns (x, y, z)
    assert full_data.header.get_xyzt_units()[0] == 'micron', "Pixel dimensions are not in microns"
    pixel_dims = full_data.header['pixdim'][1:4]
    print(f"Pixel dimensions: {pixel_dims[0]} μm x {pixel_dims[1]} μm x {pixel_dims[2]} μm")

    # get image dims (x, y, z)
    image_dims = full_data.header['dim'][1:4]
    print(f"Image dimensions: {image_dims[0]} x {image_dims[1]} pixels x {image_dims[2]} slices, {np.prod(image_dims)} voxels")

    # target resolution in microns (x, y, z)
    target_resolution = np.array(target_voxel_size)
    print(f"Target resolution: {target_resolution[0]} μm x {target_resolution[1]} μm x {target_resolution[2]} μm")

    # get resampling factor for each dimension
    resampling_factor = np.divide(pixel_dims, target_resolution)
    # add a singleton dimension to account for the channel dimension
    resampling_factor = np.append(resampling_factor, 1)
    print(f"Resampling factor: {resampling_factor[0]:.2f} x {resampling_factor[1]:.2f} x {resampling_factor[2]:.2f}")

    # get data in dtype in float32
    print("Loading data...", end='')
    data_array = full_data.get_fdata(dtype=np.float32)
    print("Data loaded.")

    # resample data using scipy bilinear interpolation
    print("Resampling data...", end='')
    resampled_data_array = zoom(data_array, resampling_factor, order=1)
    print("Data resampled.")

    # uncache data array
    print("Uncaching data...", end='')
    full_data.uncache()
    print("Data uncached.")

    # get new image dimensions
    new_image_dims = resampled_data_array.shape[0:3]
    print(f"New image dimensions: {new_image_dims[0]} x {new_image_dims[1]} pixels x {new_image_dims[2]} slices, {np.prod(new_image_dims)} voxels")

    # get new pixel dimensions
    new_pixel_dims = np.multiply(pixel_dims, np.divide(image_dims, new_image_dims))
    print(f"New pixel dimensions: {new_pixel_dims[0]:.2f} μm x {new_pixel_dims[1]:.2f} μm x {new_pixel_dims[2]:.2f} μm")

    # normalize data to [0, 1]
    print("Normalizing intensity")
    resampled_data_array = (resampled_data_array - np.min(resampled_data_array)) / (np.max(resampled_data_array) - np.min(resampled_data_array))

    # convert to int16
    print("Converting to uint16")
    resampled_data_array = (resampled_data_array * 65535).astype(np.uint16)

    # define as nifti object

    # new affine
    new_affine = np.copy(full_data.affine)
    # modify affine to reflect new pixel dimensions
    new_affine = new_affine @ np.diag(np.append(new_pixel_dims, 1.0))

    # new header
    new_header = full_data.header.copy()
    # modify header to reflect new dimensions
    new_header['pixdim'][1:4] = new_pixel_dims
    new_header['dim'][1:4] = new_image_dims

    # save resampled data
    print(f"Saving resampled data to {output_files[index]}...", end='')
    resampled_data = nb.Nifti1Image(resampled_data_array, new_affine, new_header)
    nb.save(resampled_data, output_files[index])
    print("Resampled data saved.")

    # # generate mirrored images
    # if generate_mirror:
    #     print("Generating mirrored image")
    #     resampled_data_array = np.flip(resampled_data_array, axis=0)
        
    #     new_affine_m = np.copy(full_data.affine)
    #     new_affine_m = new_affine_m @ np.diag(np.append(new_pixel_dims, 1.0))
    #     # apply flip to affine
    #     new_affine_m[0, :] = -new_affine_m[0, :]

    #     print(f"Saving mirrored data to {generate_mirror_name(output_files[index])}...", end='')
    #     resampled_data = nb.Nifti1Image(resampled_data_array, new_affine, new_header)
    #     nb.save(resampled_data, generate_mirror_name(output_files[index]))
    #     print("Mirrored data saved.")

    ## clean up
    print("Cleaning up...", end='')

    # initialize garbage collection
    del resampled_data_array, data_array, resampled_data, full_data, new_affine, new_header, new_image_dims, new_pixel_dims, pixel_dims, resampling_factor, image_dims, target_resolution

    # force garbage collection
    gc.collect()

    print("Done.")

    # clear output
    os.system('cls' if os.name == 'nt' else 'clear')

print("All files resampled.")




