# Bash Script to run the registration of the group of confocal images

## STEP 1: Create the directory structure

# Get date and time in the format YYYYMMDD_HHMM
DATE=$(date +"%Y%m%d_%H%M")

# Setup a identifier (with wildcards) for the images to be registered (e.g. synA647_*.nii.gz)
ID=synA647_*.nrrd

# Setup the number of threads to be used
THREADS_AFFINE=8
THREADS_SYN=2

# Setup the number of iterations to be used
ITERATIONS_AFFINE=10
ITERATIONS_SYN=10

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

# Copy the data from ../resampled_data to the current directory ./

cp ../resampled_data/$ID ./

## STEP 3: Run the registration

# Run the initial affine registration
./ANTs/Scripts/buildtemplateparallel.sh -d 3 -i $ITERATIONS_AFFINE -m 1x0x0 -t RA -s CC -c 2 -j $THREADS_AFFINE -o affine_ $ID > stdout-affline-template.txt 2>stderr-affline-template.txt

# Move all generated files to the affine subdirectory
# Things to move: affine_* stdout-affline-template.txt, stderr-affline-template.txt, *.cfg, job*.* and GR* folders

mv affine_* obiroi_brain_$DATE/affine
mv stdout-affline-template.txt obiroi_brain_$DATE/affine
mv stderr-affline-template.txt obiroi_brain_$DATE/affine
mv *.cfg obiroi_brain_$DATE/affine
mv GR* obiroi_brain_$DATE/affine

# Copy the affine template from the affine registration to the current directory ./ and run directory
cp obiroi_brain_$DATE/affine/affine_template.nii.gz ./affine_template.nii.gz
cp obiroi_brain_$DATE/affine/affine_template.nii.gz obiroi_brain_$DATE/affine_template.nii.gz

# Run the syn registration
./ANTs/Scripts/buildtemplateparallel.sh -d 3 -i $ITERATIONS_SYN -m 60x180x40x16 -t GR -s CC -z affine_template.nii.gz -c 2 -j $THREADS_SYN -o complete_  $ID > stdout-syn-template.txt 2>stderr-syn-template.txt

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

# Move the run directory to the results directory
mv obiroi_brain_$DATE ../results








