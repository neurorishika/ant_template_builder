# a script to resample confocal stacks to a target voxel size

import os # file handling
import numpy as np # linear algebra
# import nibabel as nb # neuroimaging file handling
import glob # file handling
# from scipy.ndimage import zoom # image processing
# import gc # garbage collection
import argparse # command line arguments
import time # timing

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
parser.add_argument('-i','--input_dir', type=str, help='path to input directory (must contain .nrrd files; default: ./cleaned_data)', default="./cleaned_data", nargs='?')
parser.add_argument('-o','--output_dir', type=str, help='path to output directory (default: ./resampled_data)', default="./resampled_data", nargs='?')
parser.add_argument('-v','--target_voxel_size', type=str, help='target voxel size in microns (e.g. 0.8x0.8x0.8)', default="0.8x0.8x0.8", nargs='?')

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


estimated_timestring = "Estimating time to completion..."

# resample each file
for index in range(len(data_files)):

    if index == 0:
        start_time = time.time()
    else:
        time_per_file = (time.time() - start_time) / index
        estimated_time = time_per_file * (len(data_files) - index)
        estimated_timestring = "Estimated time to completion: {}h {}m {}s".format(int(estimated_time // 3600), int(estimated_time // 60), int(estimated_time % 60))

    # print progress
    print(f"Resampling file {index+1} of {len(data_files)}")
    print("="*len(f"Resampling file {index+1} of {len(data_files)}"))
          
    # print estimated time to completion
    print(estimated_timestring)

    # full_data = nb.load(data_files[index])
    # print(f"Data file: {data_files[index]}")

    # # get pixel dimensions in microns (x, y, z)
    # assert full_data.header.get_xyzt_units()[0] == 'micron', "Pixel dimensions are not in microns"
    # pixel_dims = full_data.header['pixdim'][1:4]
    # print(f"Pixel dimensions: {pixel_dims[0]} μm x {pixel_dims[1]} μm x {pixel_dims[2]} μm")

    # # get image dims (x, y, z)
    # image_dims = full_data.header['dim'][1:4]
    # print(f"Image dimensions: {image_dims[0]} x {image_dims[1]} pixels x {image_dims[2]} slices, {np.prod(image_dims)} voxels")

    # target resolution in microns (x, y, z)
    target_resolution = np.array(target_voxel_size)
    print(f"Target resolution: {target_resolution[0]} μm x {target_resolution[1]} μm x {target_resolution[2]} μm")

    # # convert to mm
    # target_resolution = target_resolution / 1000
    
    # # get resampling factor for each dimension
    # resampling_factor = np.divide(pixel_dims, target_resolution)
    # # add a singleton dimension to account for the channel dimension
    # resampling_factor = np.append(resampling_factor, 1)
    # print(f"Resampling factor: {resampling_factor[0]:.2f} x {resampling_factor[1]:.2f} x {resampling_factor[2]:.2f}")

    # # get new image dimension
    # new_image_dims = np.round(np.multiply(image_dims, resampling_factor)).astype(np.int)
    # print(f"New image dimensions: {new_image_dims[0]} x {new_image_dims[1]} pixels x {new_image_dims[2]} slices, {np.prod(new_image_dims)} voxels")

    print("Resampling data")

    # print log file location
    print("Log file: {}".format(output_files[index][:-5] + '_out.log'))
    print("Error file: {}".format(output_files[index][:-5] + '_err.log'))

    # resample data using ANTs
    os.system('ResampleImage 3 {} {} {}x{}x{} 0 0 6 >{}_out.log 2>{}_err.log'.format(data_files[index], output_files[index], target_resolution[0], target_resolution[1], target_resolution[2], output_files[index][:-5], output_files[index][:-5]))

    # print("Normalizing intensity")


    # # print log file location
    # print("Log file: {}".format(output_files[index][:-5] + '_norm_out.log'))
    # print("Error file: {}".format(output_files[index][:-5] + '_norm_err.log'))

    # # Use ImageMath to Normalize Intensity
    # os.system('ImageMath 3 {} Normalize {} >{}_norm_out.log 2>{}_norm_err.log'.format(output_files[index], output_files[index], output_files[index][:-5], output_files[index][:-5]))
    
    # # get data in dtype in float32
    # print("Loading data...", end='')
    # data_array = full_data.get_fdata(dtype=np.float32)
    # print("Data loaded.")

    # # resample data using scipy bilinear interpolation
    # print("Resampling data...", end='')
    # resampled_data_array = zoom(data_array, resampling_factor, order=1)
    # print("Data resampled.")

    # # uncache data array
    # print("Uncaching data...", end='')
    # full_data.uncache()
    # print("Data uncached.")

    # # get new image dimensions
    # new_image_dims = resampled_data_array.shape[0:3]
    # print(f"New image dimensions: {new_image_dims[0]} x {new_image_dims[1]} pixels x {new_image_dims[2]} slices, {np.prod(new_image_dims)} voxels")

    # # get new pixel dimensions
    # new_pixel_dims = np.multiply(pixel_dims, np.divide(image_dims, new_image_dims))
    # print(f"New pixel dimensions: {new_pixel_dims[0]:.2f} μm x {new_pixel_dims[1]:.2f} μm x {new_pixel_dims[2]:.2f} μm")

    # # normalize data to [0, 1]
    # print("Normalizing intensity")
    # resampled_data_array = (resampled_data_array - np.min(resampled_data_array)) / (np.max(resampled_data_array) - np.min(resampled_data_array))

    # # convert to int16
    # print("Converting to uint16")
    # resampled_data_array = (resampled_data_array * 65535).astype(np.uint16)

    # # define as nifti object

    # # new affine
    # new_affine = np.copy(full_data.affine)
    # # modify affine to reflect new pixel dimensions
    # new_affine = new_affine @ np.diag(np.append(new_pixel_dims, 1.0))

    # # new header
    # new_header = full_data.header.copy()
    # # modify header to reflect new dimensions
    # new_header['pixdim'][1:4] = new_pixel_dims
    # new_header['dim'][1:4] = new_image_dims

    # # save resampled data
    # print(f"Saving resampled data to {output_files[index]}...", end='')
    # resampled_data = nb.Nifti1Image(resampled_data_array, new_affine, new_header)
    # nb.save(resampled_data, output_files[index])
    # print("Resampled data saved.")

    # # uncache resampled data
    # print("Uncaching resampled data...", end='')
    # resampled_data.uncache()

    # ## clean up
    # print("Cleaning up...", end='')

    # # initialize garbage collection
    # del resampled_data_array, data_array, resampled_data, full_data, new_affine, new_header, new_image_dims, new_pixel_dims, pixel_dims, resampling_factor, image_dims, target_resolution

    # # force garbage collection
    # gc.collect()

    print("Done.")

    # clear output
    os.system('cls' if os.name == 'nt' else 'clear')

# Remove all empty log files

print("Removing empty log files...")

for file in os.listdir(output_dir):
    if file.endswith("_out.log") or file.endswith("_err.log"):
        if os.stat(os.path.join(output_dir, file)).st_size == 0:
            os.remove(os.path.join(output_dir, file))

print("All files resampled. Exiting...")




