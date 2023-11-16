# Bash Script to run the registration of the group of confocal images

## STEP 1: Create the directory structure

# Get date and time in the format YYYYMMDD_HHMM
DATE=$(date +"%Y%m%d_%H%M")

# Setup a directory for the data to be registered
DATA_DIRECTORY=../resampled_data/antennal_lobe

# Setup a identifier (with wildcards) for the images to be registered (e.g. synA647_*.nii.gz)
ID=Brain*.nrrd

# Setup the number of threads to be used
THREADS_AFFINE=56
THREADS_SYN=56

# Setup the number of iterations to be used
ITERATIONS_AFFINE=2
ITERATIONS_SYN=4

# Create a directory for the template building in the current directory
# FORMAT: obiroi_brain_<DATE>

mkdir obiroi_brain_$DATE

# Create a subdirectory for the affine registration
# FORMAT: obiroi_brain_<DATE>/affine

mkdir obiroi_brain_$DATE/affine

# Create a subdirectory for the syn registration
# FORMAT: obiroi_brain_<DATE>/syn

mkdir obiroi_brain_$DATE/syn

## STEP 2: Copy Data to the directory

# Copy the data from subdirectory to the current directory ./

cp $DATA_DIRECTORY/$ID ./

## STEP 3: Run the registration

# Run the initial affine registration
./ANTs/Scripts/buildtemplateparallel.sh -d 3 -i $ITERATIONS_AFFINE -m 1x0x0 -t RA -s CC -c 2 -j $THREADS_AFFINE -o affine_ $ID > stdout-affine-template.txt 2>stderr-affine-template.txt

# Move all generated files to the affine subdirectory
# Things to move: affine_* stdout-affine-template.txt, stderr-affine-template.txt, *.cfg, job*.* and GR* folders

mv affine_* obiroi_brain_$DATE/affine
mv stdout-affine-template.txt obiroi_brain_$DATE/affine
mv stderr-affine-template.txt obiroi_brain_$DATE/affine
mv *.cfg obiroi_brain_$DATE/affine
mv RA* obiroi_brain_$DATE/affine

# Copy the affine template from the affine registration to the current directory ./ and run directory
cp obiroi_brain_$DATE/affine/affine_template.nii.gz ./affine_template.nii.gz
cp obiroi_brain_$DATE/affine/affine_template.nii.gz obiroi_brain_$DATE/affine_template.nii.gz

# check if there is a diff folder in the resampled_data directory
if [ -d "../resampled_data/diff" ]; then
    # Copy the diff data from ../resampled_data/diff to the current directory ./
    cp ../resampled_data/diff/$ID ./
fi

# Run the syn registration
./ANTs/Scripts/buildtemplateparallel.sh -d 3 -i $ITERATIONS_SYN -m 30x90x20x8 -t GR -s CC -z affine_template.nii.gz -c 2 -j $THREADS_SYN -o complete_  $ID > stdout-syn-template.txt 2>stderr-syn-template.txt

# Move all generated files to the syn subdirectory
# Things to move: complete_* stdout-syn-template.txt, stderr-syn-template.txt, *.cfg, job*.* and GR* folders

mv complete_* obiroi_brain_$DATE/syn
mv stdout-syn-template.txt obiroi_brain_$DATE/syn
mv stderr-syn-template.txt obiroi_brain_$DATE/syn
mv *.cfg obiroi_brain_$DATE/syn
mv GR* obiroi_brain_$DATE/syn

# delete all temporary folders (starting with temp)
rm -rf temp*

# Copy the syn template from the syn registration to the run directory
cp obiroi_brain_$DATE/syn/complete_template.nii.gz obiroi_brain_$DATE/complete_template.nii.gz

# Delete the intermediate files
rm affine_template.nii.gz
rm *.nii.gz
rm *.nrrd

# Move the run directory to the results directory
mv obiroi_brain_$DATE ../results
