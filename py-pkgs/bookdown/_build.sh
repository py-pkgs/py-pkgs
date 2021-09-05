# Simple script to generate bookdown PDF.
# Uses jupytext and some custom Python and regex to parse from .ipynb to .Rmd

# ### When we're ready for the full book ###
# # Copy references
# cp ../references.bib .
# # Create .Rmd files from .ipynb files
# (cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync *.ipynb  --quiet)
# # Unsync the files (before we make changes to the .Rmd)
# (cd .. ; jupytext --update-metadata '{"jupytext": null}' *.ipynb  --quiet)
# jupytext --update-metadata '{"jupytext": null}' *.Rmd  --quiet
# # Rename some files
# mv 00-preface.Rmd index.Rmd
# rm welcome.Rmd

### Preface and first 3 chapters for now ###
rm *.Rmd
# Copy references over
cp ../references.bib .
# Create .Rmd files from .ipynb files
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 00-preface.ipynb --quiet)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 00-authors.ipynb --quiet)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 01-introduction.ipynb --quiet)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 02-setup.ipynb --quiet)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 03-how-to-package-a-python.ipynb)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 04-package-structure.ipynb)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 05-testing.ipynb)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 06-documentation.ipynb)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 07-releasing-versioning.ipynb)
(cd .. ; jupytext --set-formats ipynb,bookdown//Rmd --sync 08-ci-cd.ipynb)
# Unsync the files (before we make changes to the .Rmd)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 00-preface.ipynb --quiet)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 00-authors.ipynb --quiet)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 01-introduction.ipynb --quiet)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 02-setup.ipynb --quiet)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 03-how-to-package-a-python.ipynb)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 04-package-structure.ipynb)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 05-testing.ipynb)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 06-documentation.ipynb)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 07-releasing-versioning.ipynb)
(cd .. ; jupytext --update-metadata '{"jupytext": null}' 08-ci-cd.ipynb)
jupytext --update-metadata '{"jupytext": null}' *.Rmd  --quiet
# Rename some files
mv 00-preface.Rmd index.Rmd

# Parse the .Rmd to change Jupyter Book format to RStudio format
python3 _build.py
# Build the book with bookdown
Rscript _build.r