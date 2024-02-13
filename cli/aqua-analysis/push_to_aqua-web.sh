#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <indir> <modelexp>"
    echo
    echo "<indir>:    the directory containing the output, e.g. output"
    echo "<modelexp>: the subfolder to push, e.g IFS-NEMO/historical-1990" 
    exit 1
fi

# setup a fresh local aqua-web copy
rm -rf aqua-web
git clone git@github.com:DestinE-Climate-DT/aqua-web.git

indir="$1/$2"
dstdir="./aqua-web/content/pdf/$2"

# erase content and copy all files to content
cd aqua-web
git rm -r content/pdf
cd ..
mkdir -p $dstdir

find $indir -name "*.pdf"  -exec cp {} $dstdir/ \;
cd aqua-web
git add content/pdf

# commit and push
commit_message="update pdfs $(date)"
git commit -m "$commit_message"

git push

## cleanup
cd ..
rm -rf aqua-web
#
echo "$(date): pushed new figures to aqua-web"
