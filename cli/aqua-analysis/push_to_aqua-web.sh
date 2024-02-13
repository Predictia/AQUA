#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <indir>"
    exit 1
fi

# setup a fresh local aqua-web copy
rm -rf aqua-web
git clone https://github.com/DestinE-Climate-DT/aqua-web.git

indir="$1"
dstdir="./aqua-web/content/pdf"

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
echo "$(date): pushed new figures to aqua-web"
