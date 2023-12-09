# -*- coding: utf-8 -*-

import os
import itertools
import nrrd
import numpy as np
from scipy.signal import find_peaks

def dice_volume(vol1, vol2):
    """
    Computes the Dice volume overlap between two volumes.
    """
    # make sure the volumes are boolean
    vol1 = vol1.astype(bool)
    vol2 = vol2.astype(bool)
    # make sure they are not empty
    if np.sum(vol1) == 0 or np.sum(vol2) == 0:
        return np.nan
    # compute the dice volume overlap and return it
    return 2 * np.sum(np.logical_and(vol1, vol2)) / (np.sum(vol1) + np.sum(vol2))

def pairwise_dice_volume(vols):
    """
    Computes the Dice volume overlap between all pairs of volumes.
    """
    n_vols = len(vols)
    dice_scores = np.ones((n_vols, n_vols))*np.nan
    for i in range(n_vols):
        for j in range(i+1, n_vols):
            dice_scores[i, j] = dice_volume(vols[i], vols[j])
    return dice_scores


train_or_test = 'train'

data_dir = '../data/segmentation_data/'+train_or_test
# get all the filenames
filenames = os.listdir(data_dir)
# keep only tif files
filenames = [f for f in filenames if f.endswith('.nrrd')]
# separate into images and labels
images = [os.path.join(data_dir, f) for f in filenames if 'segmentation' not in f]
labels = [os.path.join(data_dir, f) for f in filenames if 'segmentation' in f]
# create a matching list of pairs of images and labels
image_to_label = {}
label_to_image = {}
for image, label in itertools.product(images, labels):
    if os.path.splitext(image)[0] == os.path.splitext(label)[0].replace('_segmentation', ''):
        image_to_label[image] = label
        label_to_image[label] = image
# keep only the images that have a label
images = list(image_to_label.keys())
labels = list(image_to_label.values())

# Get the templates
template_dir = '../data/templates'
template_filenames = os.listdir(template_dir)
# keep only nrrd files
template_filenames = [f for f in template_filenames if f.endswith('.nrrd')]
print(template_filenames)


# target resolution
target_resolution = "0.8x0.8x0.8" # in microns
# get the template with the correct resolution in the name 
template_filename = [f for f in template_filenames if target_resolution in f]
assert len(template_filename) == 1, "There should be only one template with the target resolution"
template_filename = template_filename[0]
# template path
template_path = os.path.join(template_dir, template_filename)

processed_data_dir = 'processed_data/'+train_or_test

# loop over the images and labels and check if names have LEFT or RIGHT in them

TARGET_DIRECTION = 'LEFT'

new_images = []
new_labels = []


for image in images:
    if ('RIGHT' if TARGET_DIRECTION == 'LEFT' else 'LEFT') in image:
        # mirror the image
        print("Mirroring image: " + image)
        # create a mirrored image at the processed data directory
        mirrored_image = os.path.join(processed_data_dir, os.path.basename(image).replace(('RIGHT' if TARGET_DIRECTION == 'LEFT' else 'LEFT'), TARGET_DIRECTION))
        # check if the image already exists
        if os.path.isfile(mirrored_image) or os.path.isfile(os.path.dirname(mirrored_image)+'/backup/'+os.path.basename(mirrored_image)):
            print("The mirrored image already exists. Skipping.")
            new_images.append(mirrored_image)
            continue
        reflection_matrix = os.path.join(processed_data_dir, os.path.basename(image)[:-5] + "_reflection_matrix.mat")
        # create the command
        flip_brain_command1 = "ImageMath 3 {} ReflectionMatrix {} 0 >{}_out.log 2>{}_err.log".format(reflection_matrix, image, reflection_matrix[:-4], reflection_matrix[:-4])
        flip_brain_command2 = "WarpImageMultiTransform 3 {} {} -R {} {} >{}_out.log 2>{}_err.log".format(image, mirrored_image, image, reflection_matrix, os.path.basename(mirrored_image).split('.')[0], os.path.basename(mirrored_image).split('.')[0])
        # run the commands
        print(flip_brain_command1)
        os.system(flip_brain_command1)
        print(flip_brain_command2)
        os.system(flip_brain_command2)
        # change the image name to the mirrored image
        new_images.append(mirrored_image)
    else:
        # copy the image to the processed data directory
        print("Copying image: " + image)
        new_image = os.path.join(processed_data_dir, os.path.basename(image))
        # check if the image already exists
        if os.path.isfile(new_image) or os.path.isfile(os.path.dirname(new_image)+'/backup/'+os.path.basename(new_image)):
            print("The image already exists. Skipping.")
            new_images.append(new_image)
            continue
        # shutil.copyfile(image, new_image)
        os.system("cp {} {}".format(image, new_image))
        # change the image name to the copied image
        new_images.append(new_image)

for label in labels:
    if ('RIGHT' if TARGET_DIRECTION == 'LEFT' else 'LEFT') in label:
        # mirror the label
        print("Mirroring label: " + label)
        # create a mirrored label at the processed data directory
        mirrored_label = os.path.join(processed_data_dir, os.path.basename(label).replace(('RIGHT' if TARGET_DIRECTION == 'LEFT' else 'LEFT'), TARGET_DIRECTION))
        # check if the label already exists
        if os.path.isfile(mirrored_label) or os.path.isfile(os.path.dirname(mirrored_label)+'/backup/'+os.path.basename(mirrored_label)):
            print("The mirrored label already exists. Skipping.")
            new_labels.append(mirrored_label)
            continue
        reflection_matrix = os.path.join(processed_data_dir, os.path.basename(label)[:-5] + "_reflection_matrix.mat")
        # create the command
        flip_brain_command1 = "ImageMath 3 {} ReflectionMatrix {} 0 >{}_out.log 2>{}_err.log".format(reflection_matrix, label, reflection_matrix[:-4], reflection_matrix[:-4])
        # flip_brain_command2 = "WarpImageMultiTransform 3 {} {} -R {} {}".format(label, mirrored_label, label, reflection_matrix)
        flip_brain_command2 = "antsApplyTransforms -d 3 -i {} -o {} -t {} -r {} >{}_out.log 2>{}_err.log".format(label, mirrored_label, reflection_matrix, label, os.path.basename(mirrored_label).split('.')[0], os.path.basename(mirrored_label).split('.')[0])
        # run the commands
        print(flip_brain_command1)
        os.system(flip_brain_command1)
        print(flip_brain_command2)
        os.system(flip_brain_command2)
        # change the label name to the mirrored label
        new_labels.append(mirrored_label)
    else:
        # copy the label to the processed data directory
        print("Copying label: " + label)
        new_label = os.path.join(processed_data_dir, os.path.basename(label))
        # check if the label already exists
        if os.path.isfile(new_label) or os.path.isfile(os.path.dirname(new_label)+'/backup/'+os.path.basename(new_label)):
            print("The label already exists. Skipping.")
            new_labels.append(new_label)
            continue
        # shutil.copyfile(label, new_label)
        os.system("cp {} {}".format(label, new_label))
        # change the label name to the copied label
        new_labels.append(new_label)

def run_commands(commands_to_run):
    for command in commands_to_run:
        # print(command)
        os.system(command)

# resample all of the images
if not os.path.isdir("{}/backup".format(processed_data_dir)):
    # create the backup subdirectory
    command = "mkdir -p {}/backup".format(processed_data_dir)
    print(command)
    os.system(command)
    command = 'mv {}/*.nrrd {}/backup'.format(processed_data_dir, processed_data_dir)
    print(command)
    os.system(command)
    command = 'mv {}/*.mat {}/backup'.format(processed_data_dir, processed_data_dir)
    print(command)
    os.system(command)

n_jobs = os.listdir(processed_data_dir+'/backup')
# filter only nrrd files
n_jobs = [f for f in n_jobs if f.endswith('.nrrd')]
n_jobs = len(n_jobs)
n_cpu = os.cpu_count()
print("Number of jobs: {}".format(n_jobs))

# add resampled_<target_resolution> to the filenames
new_images = [x.replace('.nrrd', '_resampled_{}.nrrd'.format(target_resolution)) for x in new_images]
new_labels = [x.replace('.nrrd', '_resampled_{}.nrrd'.format(target_resolution)) for x in new_labels]

# check if all the images and labels have been resampled already
if all([os.path.isfile(x) for x in new_images]) and all([os.path.isfile(x) for x in new_labels]):
    print("All the images and labels have been resampled already. Skipping.")
else:
    # create the command
    command = f'poetry run python ../../scripts/resample.py -i {processed_data_dir+"/backup"} -o {processed_data_dir} -v {target_resolution} -n {min(n_jobs, n_cpu)}'
    print(command)
    os.system(command)

images = new_images
labels = new_labels
# recreate a matching list of pairs of images and labels
image_to_label = {}
label_to_image = {}
for image, label in itertools.product(images, labels):
    if os.path.splitext(image)[0] == os.path.splitext(label)[0].replace('_segmentation', ''):
        image_to_label[image] = label
        label_to_image[label] = image
# keep only the images that have a label
images = list(image_to_label.keys())
labels = list(image_to_label.values())

# loop over the images and register them to the template using ANTs
# loop over the images
for image in images:
    # generate output prefix
    output_prefix = os.path.basename(image).replace('.nrrd', '_')
    output_prefix = os.path.join(processed_data_dir, output_prefix)
    # check if files with this prefix already exist
    if os.path.isfile(output_prefix + 'Warp.nii.gz'):
        print("The registered image already exists. Skipping.")
        continue
    
    # convert template path to full path
    template_path_ = os.path.abspath(template_path)
    # convert image path to full path
    image_ = os.path.abspath(image)
    # convert output prefix to full path
    output_prefix_ = os.path.abspath(output_prefix)


    # create registration command
    command = f'antsIntroduction.sh -d 3 -r {template_path_} -i {image_} '
    command += f'-o {output_prefix_} -t GR -s CC -m 30x90x20x8 -n 1 -q 0 '
    command += f'>{output_prefix_}_out.log 2>{output_prefix_}_err.log'
    # add the command to the list of commands
    print(command)
    os.system(command)


# loop over the labels and warp them to the template using the generated transforms during registration
new_labels = []

for label in labels:
    # generate output prefix
    output_prefix = os.path.basename(label).replace('.nrrd', '_')
    output_prefix = processed_data_dir + '/warped_' + output_prefix
    # get the corresponding image
    image = label_to_image[label]
    # get the corresponding output prefix
    image_output_prefix = os.path.basename(image).replace('.nrrd', '_')
    image_output_prefix = processed_data_dir + '/' + image_output_prefix

    # check if files with this prefix already exist
    if os.path.isfile(output_prefix + '.nrrd'):
        print("The warped label already exists. Skipping.")
        continue
    
    # convert template path to full path
    template_path_ = os.path.abspath(template_path)
    # convert label path to full path
    label_ = os.path.abspath(label)
    # convert output prefix to full path
    output_prefix_ = os.path.abspath(output_prefix)
    # convert image path to full path
    image_output_prefix_ = os.path.abspath(image_output_prefix)
    # create registration command
    # command = f'WarpImageMultiTransform 3 {label_} {output_prefix_}.nrrd -R {template_path_} '
    # command += f'{image_output_prefix_}Warp.nii.gz {image_output_prefix_}Affine.txt '
    # command += f'>{output_prefix_}.log 2>{output_prefix_}.err'
    command = f'antsApplyTransforms -d 3 -i {label_} -r {template_path_}'
    command += f' -o {output_prefix_}.nrrd -n GenericLabel -t {image_output_prefix_}Warp.nii.gz'
    command += f' -t {image_output_prefix}Affine.txt >{output_prefix}_out.log 2>{output_prefix}_err.log'
    # add the command to the list of commands
    print(command)
    os.system(command)
    ## WE MIGHT HAVE TO FLIP THE BRAIN AGAIN HERE
    # check if the image was mirrored by seeing if the backup folder has a mat file with the same name
    if os.path.isfile(os.path.dirname(output_prefix)+'/backup/'+os.path.basename(output_prefix)[:-5] + "_reflection_matrix.mat"):
        # flip the brain
        print("Flipping label: " + output_prefix + '.nrrd')
        flipback_matrix = os.path.join(processed_data_dir, os.path.basename(output_prefix)[:-5] + "_flipback_matrix.mat")
        new_output_prefix = output_prefix + 'flipped'
        # create the command
        flip_brain_command1 = "ImageMath 3 {} ReflectionMatrix {} 0 >{}_out.log 2>{}_err.log".format(flipback_matrix, output_prefix + '.nrrd', flipback_matrix[:-4], flipback_matrix[:-4])
        flip_brain_command2 = "WarpImageMultiTransform 3 {} {} -R {} {} >{}_out.log 2>{}_err.log".format(output_prefix + '.nrrd', new_output_prefix + '.nrrd', output_prefix + '.nrrd', flipback_matrix, new_output_prefix, new_output_prefix)
        flip_brain_command3 = "PermuteFlipImageOrientationAxes 3 {} {} 0 1 2 1 0 0 >{}_out.log 2>{}_err.log".format(new_output_prefix + '.nrrd', new_output_prefix + '.nrrd', new_output_prefix, new_output_prefix)
        # run the commands
        print(flip_brain_command1)
        os.system(flip_brain_command1)
        print(flip_brain_command2)
        os.system(flip_brain_command2)
        print(flip_brain_command3)
        os.system(flip_brain_command3)
        
        # change the label name to the flipped label
        new_labels.append(new_output_prefix + '.nrrd')

# replace the labels with the warped labels
labels = new_labels

# open the warped labels using pynrrd and save them as numpy arrays

final_labels = []

# loop over the labels
for label in labels:
    print("Opening label: " + label)
    label_data, label_header = nrrd.read(label)
    final_labels.append(label_data)


# for each final label, sort the unique values map them to the values 0, 1, 2, ...
n_channels = []

processed_labels = []

for i, label in enumerate(final_labels):
    print("Processing label: " + labels[i])
    processed_label = label.copy()
    # get a histogram of the label data (0-255)
    hist, _ = np.histogram(label, bins=256)
    # find the peaks of the histogram
    peaks, _ = find_peaks(hist, threshold=1e3)
    # add to n_channels
    n_channels.append(len(peaks)+2) # for the background and the highest peak
    # digitize the label data
    processed_label = np.digitize(processed_label, bins=np.linspace(0, 255, len(peaks)+2))-1 # from 0 to n_channels-1
    # add the processed label to the list
    processed_labels.append(processed_label)
    # save the label as a nrrd file with processed added to the name
    nrrd.write(labels[i].replace('.npy', 'processed.nrrd'), np.float32(processed_label), label_header)
    print("Saved label: " + labels[i])

# assert that all the labels have the same number of channels
assert len(set(n_channels)) == 1, "All the labels should have the same number of channels"

# replace the final labels with the processed labels
final_labels = processed_labels

# create the channel wise labels
channel_wise_labels = []
n_channels = n_channels[0]
print("Consensus Number of channels: {}".format(n_channels))

# loop over the channels
for i in range(n_channels):
    channel_wise_labels.append([label == i for label in final_labels])
    print("Channel {} Labels generated.".format(i))

# compute the pairwise dice volume for each channel
dice_scores = []
for channel in channel_wise_labels:
    dice_scores.append(pairwise_dice_volume(channel))
    print("Dice volumes computed for channel {}".format(len(dice_scores)))

# save the dice volumes
np.save(processed_data_dir + f'/dice_scores_{train_or_test}.npy', dice_scores)

# compute the average dice volume for each channel
for i, channel in enumerate(dice_scores):
    # remove the NaNs
    channel_ = channel[~np.isnan(channel)].flatten()
    # check if there are any dice volumes
    if len(channel_) == 0:
        print("No overlap volumes for channel {}".format(i))
        continue
    # compute the statistics
    print('Channel {}'.format(i if i>0 else '0 (Background)'))
    print('==========')
    print("Average Dice score: {:.2f}".format(np.mean(channel_)))
    print("Median Dice score: {:.2f}".format(np.median(channel_)))
    print("95% CI Dice score: ({:.2f}, {:.2f})".format(np.percentile(channel_, 2.5), np.percentile(channel_, 97.5)))
    print("Min Dice score: {:.2f}".format(np.min(channel_)))
    print("Max Dice score: {:.2f}".format(np.max(channel_)))
    print("Std Dice score: {:.2f}".format(np.std(channel_)))
    print("")

    # save the statistics
    with open(processed_data_dir + f'/dice_scores_{train_or_test}.txt', 'a') as f:
        f.write('Channel {}\n'.format(i if i>0 else '0 (Background)'))
        f.write('==========\n')
        f.write("Average Dice score: {:.2f}\n".format(np.mean(channel_)))
        f.write("Median Dice score: {:.2f}\n".format(np.median(channel_)))
        f.write("95% CI Dice score: ({:.2f}, {:.2f})\n".format(np.percentile(channel_, 2.5), np.percentile(channel_, 97.5)))
        f.write("Min Dice score: {:.2f}\n".format(np.min(channel_)))
        f.write("Max Dice score: {:.2f}\n".format(np.max(channel_)))
        f.write("Std Dice score: {:.2f}\n".format(np.std(channel_)))
        f.write("\n")

# find the consensus segmentation for each channel
consensus_segmentation = np.zeros_like(channel_wise_labels[0][0], dtype=np.float32)
for i,channel in enumerate(channel_wise_labels):
    channel = np.array(channel)
    # compute the logical and of all the segmentations along the channel axis
    consensus = np.logical_and.reduce(channel, axis=0)
    # save the consensus segmentation as an nrrd file
    nrrd.write(processed_data_dir + f'/consensus_segmentation_channel_{i}_{train_or_test}.nrrd', np.float32(consensus), label_header)
    # add the consensus segmentation to the consensus segmentation
    if i > 0:
        consensus_segmentation += np.float32(consensus)*(i+1)
    print("Consensus segmentation computed for channel {}".format(i))

# save the consensus segmentation as a nrrd file
nrrd.write(processed_data_dir + '/consensus_segmentation_{}.nrrd'.format(train_or_test), np.float32(consensus_segmentation), label_header)
print("Consensus segmentation saved as a nrrd file.")

print("Done!")


