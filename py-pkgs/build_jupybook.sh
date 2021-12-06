#!/usr/bin/env bash

# build book
jupyter-book clean .
jupyter-book build .

# replace bookdown index command \index{*} with nothing
perl -i -pe 's/\\index\{.*?\}//g' ./_build/html/*.html

# replace Latex triple backticks
perl -i -pe 's/`{}`{}`{}/```/g' ./_build/html/*.html

# replace Latex \newpage commands
perl -i -pe 's/\\newpage//g' ./_build/html/*.html

# # replace bookdown index command \index{*} with *
# perl -i -pe 's/\\index\{(.*?)\}/\1/g' ./_build/html/*.html