import re
import os


class RmdCleaner:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.text = f.read()

    def remove_header(self):
        header = re.compile("---(?:.*\n)+---", re.DOTALL)
        self.text = header.sub("", self.text)

    def index_header(self):
        header = re.compile("---(?:.*\n)+---")
        new_header = """---
        title: "Python Packages"
        author:
        - Tomas Beuzen
        - Tiffany Timbers
        date: "`r Sys.Date()`"
        documentclass: krantz
        bibliography: [book.bib, packages.bib]
        biblio-style: apalike
        link-citations: yes
        colorlinks: yes
        lot: yes
        lof: yes
        site: bookdown::bookdown_site
        description: "Open source book on building Python packages."
        github-repo: UBC-MDS/py-pkgs
        graphics: yes
        ---
        """
        self.text = header.sub(new_header, self.text)

    def figures(self):
        figures = re.findall("```{figure}(?:.+\n)+```", self.text, re.MULTILINE)
        for figure in figures:
            try:
                reference = re.findall("name: (.+)\n", figure)[0]
                caption = re.findall("alt: (.+)\\n---", figure)[0]
                size = re.findall("width: (.+px)\\nname", figure)[0]
                file_location = re.findall("images\/.+.(?:png|svg)", figure)[0]
            except IndexError:
                print(f"Bad figure formatting:\n\n{figure}")
            new_figure = f'```{{r {reference}, fig.cap = "{caption}", fig.retina = 2, out.width="{size}", echo = FALSE, message = FALSE, warning = FALSE}}\nknitr::include_graphics("{file_location}")\n```'
            self.text = re.sub(
                pattern=figure, repl=new_figure, string=self.text
            )

    def references(self):
        """Convert in-text references like {ref}`How to package a Python` to [How to package a Python]"""
        self.text = re.sub(r"{ref}`(?:\d+|A\d):(.*?)`", r"[\1]", self.text)

    def title_references(self):
        """Remove MyST referencing syntax like (00:preface)="""
        titles = re.compile(r"\(\d*:.*\n", re.DOTALL)
        self.text = titles.sub("", self.text)

    def index_titles(self):
        """Index titles should have a {-} after them to indicate no numbering"""
        self.text = re.sub(r"(#.*)\n", r"\1 {-}", self.text)

    def line_spacing(self):
        """Remove double line breaks"""
        self.text = re.sub(r"\n\n\n", r"\n\n", self.text)

    def save(self):
        """Save file to disk"""
        with open(self.filename, "w") as f:
            f.write(self.text)

    def clean_index(self):
        self.index_header()
        self.title_references()
        self.index_titles()
        self.references()
        self.figures()
        self.line_spacing()
        self.save()

    def clean_author(self):
        self.clean_chapter()
        self.index_titles()
        self.save()

    def clean_chapter(self):
        self.remove_header()
        self.title_references()
        self.references()
        self.figures()
        self.line_spacing()
        self.save()


if __name__ == "main":
    rmd_files = [f for f in os.listdir() if f.endswith(".Rmd")]
    for f in rmd_files:
        r = RmdCleaner(f)
        if f == "index.Rmd":
            r.clean_index()
        elif f == "00-author.Rmd":
            r.clean_author()
        else:
            r.clean_chapter()
