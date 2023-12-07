#!/bin/bash

# remove old files
rm -r ANTs/

# create the ANTs directory by cloning the ANTs git repository
git clone https://github.com/ANTsX/ANTs.git

# chmod the ANTs Scripts directory
chmod +x ANTs/Scripts/*.sh