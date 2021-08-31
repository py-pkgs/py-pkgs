import re
import os
from textwrap import dedent


class RmdCleaner:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.text = f.read()

    def admonitions(self):
        def repl(match):
            admonition = match.group(1)
            return admonition.replace("}\n", ">").replace("\n\n", "\n>\n>")

        self.text = re.sub("```{(?:note|attention|tip)(}\n(?:.+\n|\n)+?)```", repl, self.text)

    def allow_python_errors(self):
        self.text = re.sub(r'tags=c\("raises-exception"\)', r"error=TRUE", self.text)

    def figures(self):
        def repl(match):
            figure = match.group(0)
            reference = re.findall("name: \d+-(.+)\n", figure)[0]
            caption = re.findall("alt: (.+)\\n---", figure)[0]
            size = re.findall("width: (.+)(?=%)", figure)[0]
            file_location = re.findall("images\/.+.(?:png|svg)", figure)[0]
            return f'```{{r {self.filename[:2] + "-" + reference}, fig.cap = "{caption}", out.width = "{size}%", fig.retina = 2, fig.align = "center", echo = FALSE, message = FALSE, warning = FALSE}}\nknitr::include_graphics("{"../" + file_location}")\n```'
        try:
            self.text = re.sub("```{figure}(?:.+\n)+```", repl, self.text)
        except Exception as e:
            print("Bad figure formatting!")
            print(e)

    def header(self):
        if self.filename == "index.Rmd":
            new_header = dedent("""\
            ---
            title: "Python Packages"
            author: "Tomas Beuzen and Tiffany Timbers"
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
            )
            self.text = re.sub("(.+\n)+(?:---)", new_header, self.text, count=1)
        elif self.filename == "01-introduction.Rmd":
            self.text = re.sub("(.+\n)+(?:---)", "\\\mainmatter", self.text, count=1)
        else:
            self.text = re.sub("(.+\n)+(?:---)", "", self.text, count=1)

    def horizontal_line(self):
        """Remove <hr> tags"""
        self.text = re.sub(r"<hr.*\/>", r"", self.text)

    def line_spacing(self):
        """Remove double line breaks"""
        self.text = re.sub(r"\n\n\n", r"\n\n", self.text)

    def code_blocks(self):
        """Format Python and bash code blocks"""
        self.text = re.sub(r"```{prompt} python >>> auto", r"```python", self.text)
        self.text = re.sub(r"```{code-block} python\n(.+\n)+---", r"```python", self.text)
        self.text = re.sub(r"```{prompt} bash \\$ auto", r"```python", self.text)

    def references(self):
        """Convert in-text references like {ref}`How-to-package-a-Python` to [How to package a Python]"""

        def repl(match):
            return "[" + match.group(1).replace("-", " ") + "]"

        self.text = re.sub(r"{ref}`(?:\d+|A\d):(.*?)`", repl, self.text)

    def remove_author_images(self):
        self.text = re.sub(r"```{figure} images\/(?:tomas-beuzen|tiffany-timbers)(?:.+\n)+```", "", self.text)

    def titles(self):
        """Remove MyST referencing syntax like (00:preface)="""
        titles = re.compile(r"\(\d*:.*\n")
        self.text = titles.sub("", self.text)
        if self.filename == "index.Rmd" or self.filename == "00-authors.Rmd":
            self.text = re.sub(r"(#.*)\n", r"\1 {-}", self.text)

    def save(self):
        """Save file to disk"""
        with open(self.filename, "w") as f:
            f.write(self.text)

    def clean(self):
        self.horizontal_line()
        self.header()
        self.titles()
        self.references()
        self.remove_author_images()
        self.code_blocks()
        self.figures()
        self.admonitions()
        self.allow_python_errors()
        self.line_spacing()
        self.save()


if __name__ == "__main__":
    rmd_files = [f for f in os.listdir() if f.endswith(".Rmd")]
    for f in rmd_files:
        r = RmdCleaner(f)
        r.clean()
        print(f"Cleaned: {f}")
