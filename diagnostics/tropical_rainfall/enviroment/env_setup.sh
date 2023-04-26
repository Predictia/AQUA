#!/bin/bash

diag_dir=$(pwd)

conda install  conda-merge 
cd ../../..
conda-merge environment.yml  $diag_dir/env-tropical-rainfall.yml > $diag_dir/merged.yml

conda env create -f $diag_dir/merged.yml

#conda activate tropical-rainfall_2
