#!/bin/bash

# This script is tentative way to incorporate the ECmean4 package 
# within AQUA: it is incomplete and only based on mamba, but has been tested 

# flag to clean environ,ent
do_clean=false

# check if you want to remove enviornment and repo
if [[ $do_clean == true ]] ; then
        rm -rf ECmean4
        mamba env remove -n ECmean4
fi

# clone
git clone https://github.com/oloapinivad/ECmean4.git
cd ECmean4

# checkout installable version: we might want to change it 
# to have it running on 
git checkout devel/refactor

# find mamba/conda (to be refined)
whereconda=$(which mamba | rev | cut -f 3-10 -d"/" | rev)
source $whereconda/etc/profile.d/conda.sh

# create env and install ECmean4
mamba env create -f environment.yml
conda activate ECmean4
pip install -e .
conda deactivate

