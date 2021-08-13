#!/usr/bin/env bash

# build book
jupyter-book clean .
jupyter-book build .

# replace bookdown index command \index{*} with *
perl -i -pe 's/\\index\{(.*?)\}/\1/g' ./_build/html/*.html