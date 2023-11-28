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
# FORMAT: obiroi_al_<DATE>

mkdir obiroi_al_$DATE

# Create a subdirectory for the affine registration
# FORMAT: obiroi_al_<DATE>/affine

mkdir obiroi_al_$DATE/affine

# Create a subdirectory for the syn registration
# FORMAT: obiroi_al_<DATE>/syn

mkdir obiroi_al_$DATE/syn

# let the user know that the directory structure has been created
echo "Directory structure created"

## STEP 2: Copy Data to the directory

# Copy the data from subdirectory to the current directory ./

cp $DATA_DIRECTORY/$ID ./

# let the user know that the data has been copied
echo "Data copied to the current directory"

## STEP 3: Run the registration

# Let the user know that the registration is starting
echo "Affine registration starting"

# Run the initial affine registration
./ANTs/Scripts/buildtemplateparallel.sh -d 3 -i $ITERATIONS_AFFINE -m 1x0x0 -t RA -s CC -c 2 -j $THREADS_AFFINE -o affine_ $ID > >(tee -a stdout-affine-template.txt) 2> >(tee -a stderr-affine-template.txt >&2)

# let the user know that the affine registration has been completed
echo "Affine registration completed"

# Move all generated files to the affine subdirectory
# Things to move: affine_* stdout-affine-template.txt, stderr-affine-template.txt, *.cfg, job*.* and GR* folders

mv affine_* obiroi_al_$DATE/affine
mv stdout-affine-template.txt obiroi_al_$DATE/affine
mv stderr-affine-template.txt obiroi_al_$DATE/affine
mv *.cfg obiroi_al_$DATE/affine
mv RA* obiroi_al_$DATE/affine

# let the user know that the affine registration has been completed
echo "Affine registration files moved to the affine subdirectory"

# Copy the affine template from the affine registration to the current directory ./ and run directory
cp obiroi_al_$DATE/affine/affine_template.nii.gz ./affine_template.nii.gz
cp obiroi_al_$DATE/affine/affine_template.nii.gz obiroi_al_$DATE/affine_template.nii.gz

# let the user know that the affine template has been copied
echo "Affine template copied to the current directory"

# check if there is a diff folder in the resampled_data directory (ARCHIVED: NO LONGER USED BUT KEPT FOR LEGACY PURPOSES)
if [ -d "../resampled_data/diff" ]; then
    # Copy the diff data from ../resampled_data/diff to the current directory ./
    cp ../resampled_data/diff/$ID ./
    # let the user know that the diff data has been copied
    echo "Diff data copied to the current directory"
fi

# Let the user know that the syn registration is starting
echo "Syn registration starting"

# Run the syn registration
./ANTs/Scripts/buildtemplateparallel.sh -d 3 -i $ITERATIONS_SYN -m 30x90x20x8 -t GR -s CC -z affine_template.nii.gz -c 2 -j $THREADS_SYN -o complete_  $ID > >(tee -a stdout-syn-template.txt) 2> >(tee -a stderr-syn-template.txt >&2)

# let the user know that the syn registration has been completed
echo "Syn registration completed"

# Move all generated files to the syn subdirectory
# Things to move: complete_* stdout-syn-template.txt, stderr-syn-template.txt, *.cfg, job*.* and GR* folders

mv complete_* obiroi_al_$DATE/syn
mv stdout-syn-template.txt obiroi_al_$DATE/syn
mv stderr-syn-template.txt obiroi_al_$DATE/syn
mv *.cfg obiroi_al_$DATE/syn
mv GR* obiroi_al_$DATE/syn

# let the user know that the syn registration has been completed
echo "Syn registration files moved to the syn subdirectory"

# Copy the syn template from the syn registration to the run directory
cp obiroi_al_$DATE/syn/complete_template.nii.gz obiroi_al_$DATE/complete_template.nii.gz

# let the user know that the syn template has been copied
echo "Syn template copied to the current directory"

# Delete the intermediate files
rm affine_template.nii.gz
rm *.nii.gz
rm *.nrrd
rm -rf temp*

# let the user know that the intermediate files have been deleted
echo "Intermediate files deleted"

# Move the run directory to the results directory
mv obiroi_al_$DATE ../results

# let the user know that the run directory has been moved to the results directory
echo "Run directory moved to the results directory"

# Let the user know that the template building is complete
echo "Template building complete"

# End of script