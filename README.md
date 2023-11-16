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

The pre-processed images should be in the `.nrrd` format. NRRD stands for Nearly Raw Raster Data, and is a file format designed to store and visualize medical image data. The images should be in the same orientation. Please use [Fiji](https://imagej.net/Fiji/Downloads) to reorient the images if they are not in the same orientation. Also preferably the images should be 8-bit. This is not necessary but recommended.

### 4. Install poetry and build the environment

[Poetry](https://python-poetry.org/) is a tool for dependency management and packaging in Python. To install poetry, follow the instructions [here](https://python-poetry.org/docs/#installation). Once poetry is installed, open a linux terminal (wsl for windows and bash for Mac/Linux) and navigate to the `ant_template_builder` folder. Then run the following command to build the environment:

```
poetry install
```

### 5. Install PyQT5

To run the GUI for Registration, you will need to install the PyQT5 library. First, make sure all the dependencies are installed by running the following command:

```
sudo apt-get update
sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev libfontconfig1-dev 
sudo apt-get install ffmpeg libsm6 libxext6
```

Next open the environment by running the following command:

```
poetry shell
```

Install the PyQT5 library by running the following command:

```
pip install pyqt5
```

### Run the mirroring script

If you want to generate mirrored images in order to symmetrize the template, you can run the mirroring script. To run the mirroring script, run the following command in the terminal (make sure you are in the `ant_template_builder` folder).

```
poetry run python scripts/generate_mirror.py
```

By default, the script will look for data (*.nrrd files) in the `cleaned_data` folder and generate mirrored images in the same folder. You can use "--help" to see the options for the script, including the option to change the input and output folders. Also it will replace any mirrored images that already exist in the output folder unless the -skip flag is set as True.

```
poetry run python scripts/generate_mirror.py --help
```

By default, the script will mirror all *.nrrd files in the input folder. However, the ant brain has a notable asymmetry in the mushroom body. Therefore, it is recommended to mirror only the brains that are oriented in one direction. You can do this by having a whole_brain_metadata.csv (as in this repository) file. The metadata file must have two columns: `Clean Name` and `Egocentric Leaning` where the first is name of the file, and the second has values of `left`,`right` or `sym` (symmetric). The script will only mirror the brains that have `left` or `right` in the `Egocentric Leaning` column depending on the -lr flag. Ideally, mirror and resample ALL the brains (unless disk space is an issue) and then use the asymmetrize_resampled.py script to filter it down to the brains that are oriented in one direction.

### 5. Run the resampling script

To run the resampling script, run the following command in the terminal (make sure you are in the `ant_template_builder` folder).

```
poetry run python scripts/resampler.py
```

By default, the target resolution is an isotropic resolution of 0.8 μm. You can use "--help" to see the options for the script, including the option to change the target resolution to a different value (potentially anisotropic). The script will generate the resampled images in the `resampled_data` folder.

```
poetry run python scripts/resampler.py --help
```

You can also generate mirrored images by using the `-m' flag. This will generate mirrored images in the 'resampled_data' folder.

### 6. (Optional) Run the asymmetrize script

To run the asymmetrize script, run the following command in the terminal (make sure you are in the `ant_template_builder` folder).

```
poetry run python scripts/asymmetrize_resampled.py
```

By default, the script will look for data (*.nrrd files) in the `resampled_data` folder and generate asymmetrized images in the same folder. It will also backup the original images in the backup folder. You can use "--help" to see the options for the script, including the option to change the input, output and backup folders. This requires the whole_brain_metadata.csv file described above to be present and linked using the -m flag.

```
poetry run python scripts/asymmetrize_resampled.py --help
```

Note: By default, the asymmetrize script will keep the symmetric brains in their original orientation. However this can reduce the final template quality. We therefore have an additional flag -q or --quality_affine that will copy all the symmetric brains into a diff_folder which will NOT be used for creating the initial affine template, but used for the final diffemorphic template. This will improve the quality of the final template. If quality affine is set to True, the metadata file must also include a column called 'Skip Affine' with values of 0 or 1. If the value is 1, the brain will be skipped for affine registration. This is useful for brains that of a poor quality and should not be used for affine registration (this is excluding the symmetric brains which are automatically skipped for affine registration).


### 6. Run the registration script

The bash script for running the registration is in the `group_registration` folder. To run the script, navigate to the `group_registration` folder and run the following command:

```
./run_registration.sh
```

Once the registration is complete, the final results will be in the 'results/obiroi_brain_YYYYMMDD_HHMM' folder, all intermediate information will be inside the 'affine' and  'syn' subfolders. The final template will be in the 'results/obiroi_brain_YYYYMMDD_HHMM/complete_template.nrrd' file. Note that this template will be in the same orientation and resolution as the input images. To generate videos or a higher resolution template, please see the next section.

### (Optional) Generate a video of the final template

### (Optional) Generate a higher resolution template from a lower resolution template

### (Optional) Register a new brain to the template


## Setup on RU HPC Cluster

### 1. Get an account on the HPC cluster

Contact the [HPC team](https://hpc.rockefeller.edu/contact) to get an account on the HPC cluster. They will give you the instructions to connect to the cluster via ssh.

### 2. Access the HPC cluster via ssh and setup Spack, ANTs and Conda

Once you have an account on the HPC cluster, you can access the cluster via ssh. You can use the following command to access the cluster:

```
ssh -l <username> login<node>-hpc.rockefeller.edu
```

Once you are logged in, you can setup Spack by adding the following lines to your `.bashrc` file:

```
# Spack
SPACK_RELEASE=spack_2020b
source /ru-auth/local/home/ruitsoft/soft/spackrc/spackrc.sh
```

Latest instructions for setting up Spack can be found [here](https://hpcguide.rockefeller.edu/guides/spack.html)

Restart your terminal and run the following command to initialize Spack:

```
lmodinit
```

Load the modules needed for building ANTs:

```
module load gcc/10.2.0-h4gobj
module load cmake/3.17.3-3rjy3k
```

Note: You can cross-reference the modules available on the HPC cluster using ```module avail gcc``` and ```module avail cmake``` with the suggested versions for compiling ANTs as mentioned [here](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS), and choose the most appropriate version.

Install ANTs using the instructions [here](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS). When configuring using CMake, make sure to have BUILD_ALL_ANTS_APPS as ON.

Then follow the instructions [here](https://hpcguide.rockefeller.edu/guides/conda.html) to setup Conda. Once you have setup Conda, you can create a new environment for running the ANTs software by running the following command:

```
conda create -n ants python
conda activate ants
```

Then you can install poetry by running the following command:

```
curl -sSL https://install.python-poetry.org | python3 -
```

Newer instructions for installing poetry can be found [here](https://python-poetry.org/docs/#installation).

### 3. Setup the Pipeline

Follow the instructions from step 2 in the previous section to complete the setup. It is preferred to setup the repository in the scratch folder on the HPC cluster for the lab. For the Kronauer lab, the scratch folder is located at `/rugpfs/fs0/kron_lab/scratch/<username>`.

An easy way to deal with scratch is to use a symlink to the scratch folder from your home directory. To do this, run the following command:

```
ln -s /rugpfs/fs0/kron_lab/scratch/<username> ~/scratch
```

Then you can navigate to the scratch folder by using the following command:

```
cd ~/scratch
```

Then you can clone the repository by running the following command:

```
git clone https://github.com/neurorishika/ant_template_builder.git 
```

Go inside the `ant_template_builder` folder and run the following command to build the environment:

```
poetry install
```


