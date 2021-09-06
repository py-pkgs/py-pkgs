# Script to generate bookdown PDF.
# Uses jupytext and some custom Python and regex to parse from .ipynb to .Rmd

# Remove old .Rmd files
rm *.Rmd
# Copy references
cp ../references.bib .
# Create .Rmd files from .ipynb files
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync *.ipynb  --quiet)
# Unsync the files (before we make changes to the .Rmd)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' *.ipynb  --quiet)
jupytext --update-metadata '{"jupytext": null}' *.Rmd  --quiet
# Rename some files
mv 00-preface.Rmd index.Rmd
rm welcome.Rmd 09-bibliography.Rmd
# Parse the .Rmd to change Jupyter Book format to RStudio format
python3 _build.py
# Build the book with bookdown
Rscript _build.r