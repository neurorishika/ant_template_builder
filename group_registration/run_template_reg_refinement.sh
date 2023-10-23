# Bash Script to run the registration of the group of confocal images

## STEP 1: Create the directory structure

# Get date and time in the format YYYYMMDD_HHMM
DATE=$(date +"%Y%m%d_%H%M")

# Setup a identifier (with wildcards) for the images to be registered (e.g. synA647_*.nii.gz)
ID=synA647_*.nrrd

# Setup the number of threads to be used
THREADS_SYN=56

# Create a directory for the template building in the current directory
# FORMAT: obiroi_brain_reg_refined_<DATE>

mkdir obiroi_brain_reg_refined_$DATE

# Create a subdirectory for the syn registration
# FORMAT: obiroi_brain_reg_refined_<DATE>/syn

mkdir obiroi_brain_reg_refined_$DATE/syn

## STEP 2: Copy Data to the directory

# Copy the data from ../resampled_data to the current directory ./

cp ../resampled_data/$ID ./

# Copy the latest refined template from ../refined_templates to the current directory ./

# find latest refined template
REFINED_TEMPLATE=$(ls -t ../refined_templates/refined_template_*.nii.gz | head -1)

# copy the latest refined template to the current directory
cp $REFINED_TEMPLATE ./obiroi_brain_reg_refined_$DATE/refined_template.nii.gz
cp $REFINED_TEMPLATE ./refined_template.nii.gz


## STEP 3: Run the registration

# Run the quick syn registration of each image to the template
# loop over all the *.nrrd files in the current directory
for f in *.nrrd
do
  # get the filename without the extension
  filename=$(basename "$f" .nrrd)
  # run the syn registration
  antsRegistrationSyNQuick.sh -d 3 -f refined_template.nii.gz -m $f -o obiroi_brain_reg_refined_$DATE/syn/registered_${filename}_ -n $THREADS_SYN -t s -y 1 -j 0 > obiroi_brain_reg_refined_$DATE/syn/registered_${filename}_output.txt 2>obiroi_brain_reg_refined_$DATE/syn/registered_${filename}_error.txt
done

# Average the Warped Images to create the template
AverageImages 3 complete_template.nii.gz 0 obiroi_brain_reg_refined_$DATE/syn/registered_*_Warped.nii.gz > obiroi_brain_reg_refined_$DATE/syn/average_images_output.txt 2>obiroi_brain_reg_refined_$DATE/syn/average_images_error.txt

# copy the template to the syn directory
cp complete_template.nii.gz obiroi_brain_reg_refined_$DATE/syn/complete_template.nii.gz

# Delete the intermediate files
rm *.nrrd

# Move the run directory to the results directory
mv obiroi_brain_reg_refined_$DATE ../results
