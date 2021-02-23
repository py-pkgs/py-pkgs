#!/usr/bin/env Rscript

bookdown::clean_book(TRUE)
bookdown::render_book("index.Rmd", "bookdown::pdf_book")