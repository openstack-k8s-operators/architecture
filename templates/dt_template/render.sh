#!/bin/bash

# Substitute %PLACEHOLDERS% in README file from cmd line

TODAY=$(date +%b\ %d\ %Y)

function help {
    echo "Usage:"
    echo "NEW_DT_NAME=name ./render.sh"
    echo "NEW_DT_NAME is the DTs name, will be used as the directory name"
}

# DT Name in Readme
sed -i -e "s;%NEW_DT_NAME%;${NEW_DT_NAME:=tempname};g" README.md

# Date for revision table v0.1
sed -i -e "s;%TODAY%;${TODAY};g" README.md

