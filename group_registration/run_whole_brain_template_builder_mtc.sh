# Bash Script to run the registration of the group of confocal images

## STEP 1: Create the directory structure

# Get date and time in the format YYYYMMDD_HHMM
DATE=$(date +"%Y%m%d_%H%M")

# Setup a directory for the data to be registered
DATA_DIRECTORY=../resampled_data/whole_brain

# Setup a identifier (with wildcards) for the images to be registered (e.g. synA647_*.nii.gz)
ID=synA647_*.nrrd

# Setup the number of threads to be used
THREADS_AFFINE=40
THREADS_SYN=40

# Setup the number of iterations to be used
ITERATIONS_AFFINE=4
ITERATIONS_SYN=6

# Create a directory for the template building in the current directory
# FORMAT: obiroi_cns_mtc_<DATE>

mkdir obiroi_cns_mtc_$DATE

# Create a subdirectory for the affine registration
# FORMAT: obiroi_cns_mtc_<DATE>/affine

mkdir obiroi_cns_mtc_$DATE/affine

# Create a subdirectory for the syn registration
# FORMAT: obiroi_cns_mtc_<DATE>/syn

mkdir obiroi_cns_mtc_$DATE/syn

# let the user know that the directory structure has been created
echo "Directory structure created"

## STEP 2: Copy Data to the directory

# Copy the data from subdirectory to the current directory ./

cp $DATA_DIRECTORY/$ID ./

# replace all '.' with '_' in the filenames 
for f in *.nrrd; do mv "$f" `echo $f | tr '.' '_'`; done

# change the last '_' to '.' (reversing the extension change)
for f in *_nrrd; do mv "$f" "${f%_*}.nrrd"; done

# let the user know that the data has been copied
echo "Data copied to the current directory"

## STEP 3: Run the registration

# Let the user know that the registration is starting
echo "Affine registration starting"

# Run the initial affine registration
./ANTs/Scripts/antsMultivariateTemplateConstruction.sh -d 3 -n 1 -c 2  -j $THREADS_AFFINE -i $ITERATIONS_AFFINE -k 1 -w 1 -m 1x0x0 -t GR -s MI -r 1 -o affine_ $ID > >(tee -a stdout-affine-template.txt) 2> >(tee -a stderr-affine-template.txt >&2)

# let the user know that the affine registration has been completed
echo "Affine registration completed"

# Move all generated files to the affine subdirectory
# Things to move: affine_* stdout-affine-template.txt, stderr-affine-template.txt, *.cfg, job*.* and GR* folders

mv affine_* obiroi_cns_mtc_$DATE/affine
mv stdout-affine-template.txt obiroi_cns_mtc_$DATE/affine
mv stderr-affine-template.txt obiroi_cns_mtc_$DATE/affine
mv intermediate* obiroi_cns_mtc_$DATE/affine
mv rigid obiroi_cns_mtc_$DATE/affine
mv ANTs_* obiroi_cns_mtc_$DATE/affine

# let the user know that the affine registration has been completed
echo "Affine registration files moved to the affine subdirectory"

# Copy the affine template from the affine registration to the current directory ./ and run directory
cp obiroi_cns_mtc_$DATE/affine/affine_template0.nii.gz ./affine_template0.nii.gz
cp obiroi_cns_mtc_$DATE/affine/affine_template0.nii.gz obiroi_cns_mtc_$DATE/affine_template0.nii.gz

# let the user know that the affine template has been copied
echo "Affine template copied to the current directory"

# check if there is a diff folder in the resampled_data directory
if [ -d "../resampled_data/whole_brain/diff" ]; then
    # Copy the diff data from ../resampled_data/diff to the current directory ./
    cp ../resampled_data/whole_brain/diff/$ID ./
    # let the user know that the diff data has been copied
    echo "Diff data copied to the current directory"
fi

# Let the user know that the syn registration is starting
echo "Syn registration starting"

# Run the syn registration
./ANTs/Scripts/antsMultivariateTemplateConstruction.sh -d 3 -n 1 -c 2 -j $THREADS_SYN -i $ITERATIONS_SYN -k 1 -w 1 -m 60x120x40x20 -t GR -s CC -r 0 -o complete_ -z affine_template0.nii.gz $ID > >(tee -a stdout-syn-template.txt) 2> >(tee -a stderr-syn-template.txt >&2)

# let the user know that the syn registration has been completed
echo "Syn registration completed"

# Move all generated files to the syn subdirectory
# Things to move: complete_* stdout-syn-template.txt, stderr-syn-template.txt, *.cfg, job*.* and GR* folders

mv complete_* obiroi_cns_mtc_$DATE/syn
mv stdout-syn-template.txt obiroi_cns_mtc_$DATE/syn
mv stderr-syn-template.txt obiroi_cns_mtc_$DATE/syn
mv intermediate* obiroi_cns_mtc_$DATE/syn
mv ANTs_* obiroi_cns_mtc_$DATE/syn


# let the user know that the syn registration has been completed
echo "Syn registration files moved to the syn subdirectory"

# Copy the syn template from the syn registration to the run directory
cp obiroi_cns_mtc_$DATE/syn/complete_template0.nii.gz obiroi_cns_mtc_$DATE/complete_template0.nii.gz

# let the user know that the syn template has been copied
echo "Syn template copied to the run directory"

# Delete the intermediate files
rm affine_template0.nii.gz
# rm *.nii.gz
rm *.nrrd
rm -rf temp*

# Let the user know that the intermediate files have been deleted
echo "Intermediate files deleted"

# Move the run directory to the results directory
mv obiroi_cns_mtc_$DATE ../results

# Let the user know that the run directory has been moved to the results directory
echo "Run directory moved to the results directory"

# Let the user know that the template building is complete
echo "Template building complete"

# End of script

