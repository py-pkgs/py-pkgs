import re
import os


class RmdCleaner:
    def __init__(self, filename):
        self.filename = filename
        with open(filename) as f:
            self.text = f.read()

    def fix_figures(self):
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

    def fix_references(self):
        pass

    def save(self, out=None):
        if out is None:
            with open(self.filename, "w") as f:
                f.write(self.text)
        else:
            with open(out, "w") as f:
                f.write(self.text)

    def clean(self):
        self.fix_figures()
        self.save()


if __name__ == "main":
    rmd_files = [f for f in os.listdir() if f.endswith(".Rmd")]
    for f in rmd_files:
        b = RmdCleaner(f)
        b.clean()
