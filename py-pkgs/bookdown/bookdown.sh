# script to generate bookdown PDF

# Create .Rmd files from .ipynb files
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync *.ipynb)
# Unsync the files (before we make changes to the .Rmd)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' *.ipynb)
jupytext --update-metadata '{"jupytext": null}' *.Rmd
# Parse the .Rmd to change Jupyter Book format to RStudio format
python bookdown.py
# Build the bookdown
r bookdown