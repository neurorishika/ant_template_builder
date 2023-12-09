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


data_dir = '../data/segmentation_data/template'
# get all the filenames
labels = os.listdir(data_dir)
# keep only tif files
labels = [f for f in labels if f.endswith('.nrrd')]
# make sure all of them segmented in the name
labels = [f for f in labels if 'segmented' in f]

processed_data_dir = 'processed_data/template'

# open the warped labels using pynrrd and save them as numpy arrays

final_labels = []
final_labels_paths = []
resolutions = []

# loop over the labels
for label in labels:
    print("Opening label: {}".format(label))
    label_data, label_header = nrrd.read(os.path.join(data_dir, label))
    final_labels.append(label_data)
    # get the voxel spacing to check if it is the same for all the labels
    resolutions.append(label_header['space directions'])
    final_labels_paths.append(os.path.join(processed_data_dir, label.replace('.nrrd', '_processed.nrrd')))

# assert that all the labels have the same voxel spacing
assert len(set(resolutions)) == 1, "All the labels should have the same voxel spacing"

# for each final label, sort the unique values map them to the values 0, 1, 2, ...
n_channels = []

processed_labels = []

for i, label in enumerate(final_labels):
    print("Processing label {}".format(i))
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
    nrrd.write(final_labels_paths[i], np.float32(processed_label), label_header)
    print("Saved label: " + final_labels_paths[i])

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
np.save(processed_data_dir + f'/dice_scores_template.npy', dice_scores)

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
    with open(processed_data_dir + f'/dice_scores_channel_template.txt', 'a') as f:
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
    nrrd.write(processed_data_dir + f'/consensus_segmentation_channel_{i}_template.nrrd', np.float32(consensus), label_header)
    # add the consensus segmentation to the consensus segmentation
    if i > 0:
        consensus_segmentation += np.float32(consensus)*(i+1)
    print("Consensus segmentation computed for channel {}".format(i))

# save the consensus segmentation as a nrrd file
nrrd.write(processed_data_dir + '/consensus_segmentation_template.nrrd', np.float32(consensus_segmentation), label_header)
print("Consensus segmentation saved as a nrrd file.")

print("Done!")


