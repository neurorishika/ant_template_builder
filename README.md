# Kronauer Lab - Ooceraea biroi CNS Brain Template 2023

![ants](https://www.rockefeller.edu/research/uploads/www.rockefeller.edu/sites/8/2017/12/clonal_ants7-2400x800.png)

This repository contains the protocol to generate a 3D template of the brain of the ant *Ooceraea biroi* (Clonal Raider Ant) from anti-Synapsin1 stained confocal stacks of the ant brain (α-SYN A647 marker) imaged at the [Kronauer Lab](https://www.rockefeller.edu/research/2280-kronauer-laboratory/) at the [Rockefeller University](https://www.rockefeller.edu/). The brains were imaged at 0.13 μm x 0.13 μm x 0.29 μm.

## Protocol for generating the template

### 1. Install ANTs Software for image registration

The ANTs software can be downloaded from [here](https://github.com/ANTsX/ANTs), you will need to use [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) to run the ANTs software on [Windows](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Windows-10). The ANTs software is also available on [Mac and Linux](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS).

### 2. Clone this repository

Make sure you have [git](https://git-scm.com/) installed on your computer. Then clone this repository by running the following command in your terminal:

```
git clone https://github.com/neurorishika/ant_template_builder.git 
```

### 3. Place the pre-processed images in the `cleaned_data` folder

The pre-processed images should be in the `.nii.gz` format. The code assumes that the images are in the same orientation, please use [Fiji](https://imagej.net/Fiji/Downloads) to reorient the images if they are not in the same orientation. You can export to Nifti format from Fiji by using the [Nifti Plugin](https://imagej.nih.gov/ij/plugins/nifti.html). 

### 4. Install poetry and build the environment

[Poetry](https://python-poetry.org/) is a tool for dependency management and packaging in Python. To install poetry, follow the instructions [here](https://python-poetry.org/docs/#installation). Once poetry is installed, open a linux terminal (wsl for windows and bash for Mac/Linux) and navigate to the `ant_template_builder` folder. Then run the following command to build the environment:

```
poetry install
```

### 5. Run the resampling script

To run the resampling script, run the following command in the terminal (make sure you are in the `ant_template_builder` folder).

```
poetry run python scripts/resample.py
```

By default, the target resolution is an isotropic resolution of 0.8 μm. You can use "--help" to see the options for the script, including the option to change the target resolution to a different value (potentially anisotropic). The script will generate the resampled images in the `resampled_data` folder.

```
poetry run python scripts/resample.py --help
```

You can also generate mirrored images by using the `-m' flag. This will generate mirrored images in the 'resampled_data' folder.

### 6. Run the registration script

The bash script for running the registration is in the `group_registration` folder. To run the script, navigate to the `group_registration` folder and run the following command:

```
./run_registration.sh
```

Once the registration is complete, the final results will be in the 'results/obiroi_brain_YYYYMMDD_HHMM' folder, all intermediate information will be inside the 'affine' and  'syn' subfolders. The final template will be in the 'results/obiroi_brain_YYYYMMDD_HHMM/complete_template.nii.gz' file. Note that this template will be in the same orientation and resolution as the input images. To generate videos or a higher resolution template, please see the next section.

### (Optional) Generate a video of the final template

### (Optional) Generate a higher resolution template

### (Optional) Register a new brain to the template