# Bash Script to run the registration of the group of confocal images

## STEP 1: Create the directory structure

# Get date and time in the format YYYYMMDD_HHMM
DATE=$(date +"%Y%m%d_%H%M")

# Setup a identifier (with wildcards) for the images to be registered (e.g. synA647_*.nii.gz)
ID=synA647_*.nrrd

# Setup the number of threads to be used
THREADS_SYN=56

# Setup the number of iterations to be used
ITERATIONS_SYN=4

# Create a directory for the template building in the current directory
# FORMAT: obiroi_brain_refined_<DATE>

mkdir obiroi_brain_refined_$DATE


# Create a subdirectory for the syn registration
# FORMAT: obiroi_brain_refined_<DATE>/syn

mkdir obiroi_brain_refined_$DATE/syn

## STEP 2: Copy Data to the directory

# Copy the data from ../resampled_data to the current directory ./

cp ../resampled_data/$ID ./

# Copy the latest refined template from ../refined_templates to the current directory ./

# find latest refined template
REFINED_TEMPLATE=$(ls -t ../refined_templates/refined_template_*.nii.gz | head -1)

# copy the latest refined template to the current directory
cp $REFINED_TEMPLATE ./obiroi_brain_refined_$DATE/refined_template.nii.gz
cp $REFINED_TEMPLATE ./refined_template.nii.gz

## STEP 3: Run the registration

# Run the syn registration
./ANTs/Scripts/buildtemplateparallel.sh -d 3 -i $ITERATIONS_SYN -m 30x90x20x8 -t GR -s CC -z refined_template.nii.gz -c 2 -j $THREADS_SYN -o complete_  $ID > stdout-syn-template.txt 2>stderr-syn-template.txt

# Move all generated files to the syn subdirectory
# Things to move: complete_* stdout-syn-template.txt, stderr-syn-template.txt, *.cfg, job*.* and GR* folders

mv complete_* obiroi_brain_refined_$DATE/syn
mv stdout-syn-template.txt obiroi_brain_refined_$DATE/syn
mv stderr-syn-template.txt obiroi_brain_refined_$DATE/syn
mv *.cfg obiroi_brain_refined_$DATE/syn
mv GR* obiroi_brain_refined_$DATE/syn

# delete all temporary folders (starting with temp)
rm -rf temp*

# Copy the syn template from the syn registration to the run directory
cp obiroi_brain_refined_$DATE/syn/complete_template.nii.gz obiroi_brain_refined_$DATE/complete_template.nii.gz

# Delete the intermediate files
rm *.nii.gz
rm *.nrrd

# Move the run directory to the results directory
mv obiroi_brain_refined_$DATE ../results
