# Simple script to generate bookdown PDF.
# Uses jupytext and some custom Python and regex to parse from .ipynb to .Rmd

### When we're ready for the full book ###
# Create .Rmd files from .ipynb files
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync *.ipynb)
# Unsync the files (before we make changes to the .Rmd)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' *.ipynb)
jupytext --update-metadata '{"jupytext": null}' *.Rmd
# Rename some files
mv 00-preface.Rmd index.Rmd
rm welcome.Rmd

# ### Preface and first 3 chapters for now ###
# rm *.Rmd
# # Create .Rmd files from .ipynb files
# (cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 00-preface.ipynb)
# (cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 00-authors.ipynb)
# (cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 01-introduction.ipynb)
# (cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 02-setup.ipynb)
# # (cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 03-how-to-package-a-python.ipynb)
# # Unsync the files (before we make changes to the .Rmd)
# (cd .. ; jupytext --update-metadata '{"jupytext": null}' 00-preface.ipynb)
# (cd .. ; jupytext --update-metadata '{"jupytext": null}' 00-authors.ipynb)
# (cd .. ; jupytext --update-metadata '{"jupytext": null}' 01-introduction.ipynb)
# (cd .. ; jupytext --update-metadata '{"jupytext": null}' 02-setup.ipynb)
# # (cd .. ; jupytext --update-metadata '{"jupytext": null}' 03-how-to-package-a-python.ipynb)
# jupytext --update-metadata '{"jupytext": null}' *.Rmd
# # Rename some files
# mv 00-preface.Rmd index.Rmd

# Parse the .Rmd to change Jupyter Book format to RStudio format
python3 _build.py
# Build the book with bookdown
Rscript _build.r