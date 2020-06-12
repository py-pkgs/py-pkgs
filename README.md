# Python packages
[Tomas Beuzen](https://www.tomasbeuzen.com/) & [Tiffany Timbers](https://www.tiffanytimbers.com/)

<p align="center">
  <img src="py-pkgs/content/img/project/py-pkgs-hex.png" width="300">
</p>

A simple and practical introduction to creating and distributing Python code via Python packages. This book is aimed at Python intermediate users who want to package up their code to share it with their collaborators (including their future selves) and the wider Python community. It's scope and intent is inspired by the [R packages](https://r-pkgs.org/) book written by Hadley Wickham and Jenny Bryan.

## Building the book

If you'd like develop and build the py-pkgs book from source, you should:

- Clone this repository and run
- Run `pip install requirements.txt` (it is recommended you do this within a virtual environment)
- (Recommended) Remove the existing `py-pkgs/_build/` directory
- Run `jupyter-book build py-pkgs/`

A fully-rendered HTML version of the book will be built in `py-pkgs/_build/html/`.

## Hosting the book (for developers)

The html version of the book in hosted on the `gh-pages` branch of this repo. Push updated version of the book to this branch by:

- Navigating to the local build
- `ghp-import -n -p -f py-pkgs/_build/html`

More info on this process can be found [here](https://jupyterbook.org/publish/gh-pages.html#manually-host-your-book-with-github-pages). This process should be automated with GitHub Actions.

## Contributing

Contributions are welcome and greatly appreciated! If you're interested in contributing to this project, take a look at the [contributor guide](CONTRIBUTING.md).

## Contributors

All contributions are welcomed and recognized! You can see a list of current contributors in the [contributors tab](https://github.com/UBC-MDS/py-pkgs/graphs/contributors).

## Acknowledgements

This online book is created using the excellent open source [Jupyter Book project](https://jupyterbook.org/). Go check it out!
