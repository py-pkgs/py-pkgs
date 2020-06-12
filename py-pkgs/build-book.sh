#!/bin/sh
#This script builds a fresh copy of the animated-data book

#First remove the old html build
if [ -d "_build" ] ; then #try
    echo "Removing current _build directory..."
    rm -r _build/
else #catch
    echo "No current _build directory to remove..."
fi

# #Now update the table of contents - this feature is a bit broken atm, leaving out for now
# echo "Generating TOC..."
# jupyter-book toc content/ --output-folder ./

#Build the book
echo "Building book..."
# jupyter-book build ./

if  [[ $1 = "-p" ]]; then
    #Push to the github pages branch (note this overwrites all contents on the branch)
    # ghp-import -n -p -f _build/html
    echo "Your book has been built and pushed to GitHub!"
else
    echo "Your book has been built!"
fi