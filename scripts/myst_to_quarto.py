# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""One-off migration: Jupyter Book (MyST) notebooks -> Quarto .qmd files.

Run once against draft-2nd-edition @ b7df3b5; the notebooks were removed in the same
commit, so to re-run it check them out first (git checkout b7df3b5 -- "py-pkgs/*.ipynb").

Usage (from the repository root):

    uv run scripts/myst_to_quarto.py            # convert, write .qmd next to the notebooks
    uv run scripts/myst_to_quarto.py --check    # dry run, report only

Only formatting is translated; chapter prose is left untouched. Mappings:

    (NN:Label)=  + heading      -> heading {#sec-nn-label}
    {numref}`NN:Label`          -> @sec-nn-label
    {numref}`name-fig|table`    -> @fig-name / @tbl-name
    {ref}`NN:Label`             -> [Section title](#sec-nn-label)   (title text, as in Ed.1)
    {cite:p}`a,b` / {cite}`a`   -> [@a; @b]
    ```{figure}                 -> ![caption](path){#fig-... width=... fig-alt=...}
    ```{table}                  -> pipe table + ": caption {#tbl-...}"
    ```{note|tip|attention}     -> ::: {.callout-*}
    ```{admonition} Title       -> ::: {.callout-<class>} with "## Title"
    ```{code-block} lang        -> ``` {.lang emphasize-lines="..."}  (attribute kept, inert)
    ```{bibliography}           -> ::: {#refs}
    <hr ...>                    -> removed
    stray @word in prose        -> \\@word  (so pandoc doesn't read it as a citation)
    unlabelled ``` block        -> ```bash ($ prompt) or ```python (>>> prompt)

\\index{} and \\newpage are left as raw LaTeX: they reach the PDF and pandoc drops them
from HTML output.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent / "py-pkgs"

# notebook -> (qmd name, unnumbered?)
FILES = {
    "welcome.ipynb": ("index.qmd", True),
    "00-preface.ipynb": ("00-preface.qmd", True),
    "00-authors.ipynb": ("00-authors.qmd", True),
    "01-introduction.ipynb": ("01-introduction.qmd", False),
    "02-setup.ipynb": ("02-setup.qmd", False),
    "03-how-to-package-a-python.ipynb": ("03-how-to-package-a-python.qmd", False),
    "04-package-structure.ipynb": ("04-package-structure.qmd", False),
    "05-testing.ipynb": ("05-testing.qmd", False),
    "06-documentation.ipynb": ("06-documentation.qmd", False),
    "07-releasing-versioning.ipynb": ("07-releasing-versioning.qmd", False),
    "08-ci-cd.ipynb": ("08-ci-cd.qmd", False),
    "09-bibliography.ipynb": ("09-bibliography.qmd", True),
}

CALLOUT = {
    "note": ("note", None),
    "tip": ("tip", None),
    "hint": ("tip", "Hint"),
    "attention": ("warning", "Attention"),
    "warning": ("warning", None),
    "caution": ("caution", None),
    "important": ("important", None),
    "danger": ("important", "Danger"),
    "seealso": ("note", "See also"),
}

FENCE_RE = re.compile(r"^(\s*)(`{3,})\s*(.*?)\s*$")
DIRECTIVE_RE = re.compile(r"^\{([\w:-]+)\}\s*(.*)$")
LABEL_RE = re.compile(r"^\(([^)\s]+)\)=\s*$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
ROLE_RE = re.compile(r"\{(numref|ref|cite:p|cite:t|cite)\}`([^`]*)`")
INLINE_CODE_RE = re.compile(r"(`+)(?:.+?)\1", re.S)
LIST_ITEM_RE = re.compile(r"^(\s*(?:\d+[.)]|[-*+])\s+)\S")
HR_RE = re.compile(r"^\s*<hr\b[^>]*/?>\s*$", re.I)

warnings: list[str] = []
stats: dict[str, int] = {}


def bump(key: str, n: int = 1) -> None:
    stats[key] = stats.get(key, 0) + n


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def sec_id(label: str) -> str:
    return "sec-" + slug(label)


def fig_id(name: str) -> str:
    return "fig-" + slug(re.sub(r"-fig$", "", name))


def tbl_id(name: str) -> str:
    return "tbl-" + slug(re.sub(r"-table$", "", name))


def clean_title(title: str) -> str:
    title = re.sub(r"\\index\{[^}]*\}", "", title)
    title = re.sub(r"\s*\{[^}]*\}\s*$", "", title)  # trailing attribute block
    return title.strip()


def notebook_markdown(path: Path) -> str:
    nb = json.loads(path.read_text())
    cells = []
    for cell in nb["cells"]:
        src = "".join(cell["source"])
        if cell["cell_type"] == "code":
            if src.strip():
                warnings.append(f"{path.name}: non-empty code cell dropped: {src[:60]!r}")
            continue
        cells.append(src.strip("\n"))
    return "\n\n".join(cells) + "\n"


# --------------------------------------------------------------------------- pass 1


def collect_labels(texts: dict[str, str]) -> dict[str, str]:
    """Map lower-cased MyST label -> heading title (for {ref} link text)."""
    titles: dict[str, str] = {}
    for name, text in texts.items():
        lines = text.split("\n")
        in_fence = None
        for i, line in enumerate(lines):
            fm = FENCE_RE.match(line)
            if fm:
                ticks = fm.group(2)
                if in_fence is None:
                    in_fence = len(ticks)
                elif len(ticks) >= in_fence and not fm.group(3):
                    in_fence = None
                continue
            if in_fence is not None:
                continue
            lm = LABEL_RE.match(line)
            if lm:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                hm = HEADING_RE.match(lines[j]) if j < len(lines) else None
                if hm:
                    titles[lm.group(1).lower()] = clean_title(hm.group(2))
                else:
                    warnings.append(f"{name}: label {lm.group(1)} is not followed by a heading")
    return titles


# --------------------------------------------------------------------------- inline


def convert_roles(text: str, titles: dict[str, str], where: str) -> str:
    def repl(m: re.Match) -> str:
        role, target = m.group(1), m.group(2).strip()
        if role.startswith("cite"):
            keys = [k.strip() for k in target.split(",") if k.strip()]
            bump("cite")
            if role == "cite:t":
                return "; ".join("@" + k for k in keys)
            return "[" + "; ".join("@" + k for k in keys) + "]"
        if "<" in target:  # explicit text: {ref}`text <label>`
            txt, label = re.match(r"(.*?)\s*<([^>]+)>", target).groups()
        else:
            txt, label = None, target
        key = label.lower()
        if role == "numref":
            if key in titles:
                bump("numref:sec")
                return "@" + sec_id(label)
            if key.endswith("-fig"):
                bump("numref:fig")
                return "@" + fig_id(label)
            if key.endswith("-table"):
                bump("numref:tbl")
                return "@" + tbl_id(label)
            warnings.append(f"{where}: unresolved numref {target!r}")
            return m.group(0)
        # {ref}
        if key in titles:
            bump("ref")
            return f"[{txt or titles[key]}](#{sec_id(label)})"
        warnings.append(f"{where}: unresolved ref {target!r}")
        return m.group(0)

    return ROLE_RE.sub(repl, text)


def escape_at(text: str) -> str:
    """Escape @word outside inline code so pandoc doesn't treat it as a citation."""
    out, pos = [], 0
    for m in INLINE_CODE_RE.finditer(text):
        out.append(_escape_at(text[pos : m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_escape_at(text[pos:]))
    return "".join(out)


def _escape_at(seg: str) -> str:
    # leave citations we generated ([@key; @key]) alone
    def repl(m: re.Match) -> str:
        bump("escaped-at")
        return "\\@"

    parts = re.split(r"(\[@[^\]]*\])", seg)
    return "".join(
        p if p.startswith("[@") else re.sub(r"(?<![\w\\\[;@/.])@(?=[A-Za-z_])", repl, p) for p in parts
    )


def convert_prose_line(line: str, titles, where) -> str:
    return convert_roles(escape_at(line), titles, where)


# --------------------------------------------------------------------------- directives


def split_options(body: list[str]) -> tuple[dict[str, str], list[str]]:
    """Parse MyST directive options (YAML '---' block or ':key: value' lines)."""
    opts: dict[str, str] = {}
    if body and body[0].strip() == "---":
        end = next(i for i in range(1, len(body)) if body[i].strip() == "---")
        for line in body[1:end]:
            if ":" in line:
                k, v = line.split(":", 1)
                opts[k.strip()] = v.strip()
        return opts, body[end + 1 :]
    i = 0
    while i < len(body):
        om = re.match(r"^:([\w-]+):\s*(.*)$", body[i])
        if not om:
            break
        opts[om.group(1)] = om.group(2).strip()
        i += 1
    return opts, body[i:]


def attr_quote(v: str) -> str:
    return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_directive(name, arg, body, indent, titles, where) -> list[str]:
    ind = indent
    if name in CALLOUT or name == "admonition":
        opts, rest = split_options(body)
        if name == "admonition":
            kind, title = CALLOUT.get(opts.get("class", "note"), ("note", None))[0], arg
        else:
            kind, title = CALLOUT[name]
            if arg:
                title = arg
        bump(f"callout:{name}")
        inner = convert_block(rest, titles, where)
        header = f"{ind}::: {{.callout-{kind}}}"
        out = [header]
        if title:
            out += [f"{ind}## {title}", ""]
        out += inner + [f"{ind}:::"]
        return out
    if name == "figure":
        opts, rest = split_options(body)
        caption = convert_prose_line(" ".join(l.strip() for l in rest if l.strip()), titles, where)
        attrs = []
        if caption and "name" in opts:
            attrs.append("#" + fig_id(opts["name"]))
        elif "name" in opts and not caption:
            bump("figure:uncaptioned")
        if "width" in opts:
            attrs.append(f"width={attr_quote(opts['width'])}")
        if "alt" in opts:
            attrs.append(f"fig-alt={attr_quote(opts['alt'])}")
        bump("figure")
        return [f"{ind}![{caption}]({arg}){{{' '.join(attrs)}}}"]
    if name == "table":
        opts, rest = split_options(body)
        bump("table")
        caption = convert_prose_line(arg, titles, where)
        ident = f" {{#{tbl_id(opts['name'])}}}" if "name" in opts else ""
        table = [convert_prose_line(l, titles, where) for l in rest]
        while table and not table[-1].strip():
            table.pop()
        return table + ["", f"{ind}: {caption}{ident}"]
    if name == "code-block":
        opts, rest = split_options(body)
        bump("code-block")
        lang = arg or "text"
        if opts:
            extra = " ".join(f"{k}={attr_quote(v)}" for k, v in opts.items())
            opener = f"{ind}``` {{.{lang} {extra}}}"
        else:
            opener = f"{ind}```{lang}"
        return [opener] + rest + [f"{ind}```"]
    if name == "bibliography":
        bump("bibliography")
        return [f"{ind}::: {{#refs}}", f"{ind}:::"]
    warnings.append(f"{where}: unhandled directive {{{name}}} kept verbatim")
    return None


# --------------------------------------------------------------------------- block walker


def convert_block(lines: list[str], titles, where, unnumbered=False) -> list[str]:
    out: list[str] = []
    pending_label: str | None = None
    list_col: int | None = None
    i = 0
    while i < len(lines):
        line = lines[i]
        lim = LIST_ITEM_RE.match(line)
        if lim:
            list_col = len(lim.group(1))
        elif line.strip() and not line.startswith(" "):
            list_col = None
        fm = FENCE_RE.match(line)
        if fm:
            indent, ticks, info = fm.groups()
            # find the matching closer
            j = i + 1
            while j < len(lines):
                cm = FENCE_RE.match(lines[j])
                if cm and len(cm.group(2)) >= len(ticks) and not cm.group(3):
                    break
                j += 1
            body = lines[i + 1 : j]
            dm = DIRECTIVE_RE.match(info)
            if dm and indent and list_col is not None and dm.group(1) in (*CALLOUT, "admonition"):
                # pandoc only reads a fenced div inside a list item at the item's content column
                body = [l[len(indent):] if l.startswith(indent) else l.lstrip() for l in body]
                body = [(" " * list_col + l) if l.strip() else "" for l in body]
                indent = " " * list_col
                bump("callout:reindented-in-list")
            rendered = render_directive(dm.group(1), dm.group(2).strip(), body, indent, titles, where) if dm else None
            if rendered is None and not dm and not info:
                # Unlabelled blocks are shell or Python sessions. Give them a language so Quarto
                # renders them as highlighted, copyable code blocks (prompts are stripped on copy
                # by html/copy-without-prompts.html).
                first = next((l.strip() for l in body if l.strip()), "")
                lang = "bash" if first.startswith("$") else "python" if first.startswith(">>>") else None
                if lang:
                    bump(f"bare-fence:{lang}")
                    out += [f"{indent}{ticks}{lang}"] + body + [lines[j]] if j < len(lines) else []
                    i = j + 1
                    continue
                warnings.append(f"{where}: unlabelled code block without a prompt: {first[:40]!r}")
            if rendered is None:
                out += lines[i : j + 1]  # ordinary code block, verbatim
            else:
                # MyST fences may interrupt a paragraph; pandoc divs/figures may not
                if out and out[-1].strip():
                    out.append("")
                out += rendered + [""]
            i = j + 1
            continue
        lm = LABEL_RE.match(line)
        if lm:
            pending_label = lm.group(1)
            i += 1
            continue
        if HR_RE.match(line):
            bump("hr")
            i += 1
            continue
        hm = HEADING_RE.match(line)
        if hm and (pending_label or (unnumbered and hm.group(1) == "#")):
            attrs = []
            if pending_label:
                attrs.append("#" + sec_id(pending_label))
                bump("section-label")
            if unnumbered and hm.group(1) == "#":
                # .unlisted: krantz's \chapter* already adds the TOC line; without it the PDF
                # TOC lists front-matter chapters twice. The HTML sidebar is unaffected.
                attrs += [".unnumbered", ".unlisted"]
            text = convert_prose_line(hm.group(2), titles, where)
            out.append(f"{hm.group(1)} {text} {{{' '.join(attrs)}}}")
            pending_label = None
            i += 1
            continue
        if pending_label and line.strip():
            warnings.append(f"{where}: label {pending_label} dropped (no heading follows)")
            pending_label = None
        out.append(convert_prose_line(line, titles, where))
        i += 1
    return out


def convert_file(nb_name: str, text: str, titles) -> str:
    qmd, unnumbered = FILES[nb_name]
    body = convert_block(text.split("\n"), titles, qmd, unnumbered=unnumbered)
    result = "\n".join(body)
    result = re.sub(r"\n{3,}", "\n\n", result).strip("\n") + "\n"
    if qmd == "00-authors.qmd":
        # Last front-matter chapter: switch the PDF to arabic page numbers / numbered chapters
        # (Ed.1's bookdown build did the same). Must come after the heading Quarto emits for
        # the next chapter's \chapter, so it lives at the end of this file.
        result += "\n```{=latex}\n\\mainmatter\n```\n"
    if qmd == "index.qmd":
        # The welcome page (cover, purchase links) is web-only; the PDF opens with the preface.
        result = '::: {.content-visible when-format="html"}\n\n' + result + "\n:::\n"
    return result


def leftovers(name: str, text: str) -> None:
    """Report MyST syntax still present outside code blocks."""
    in_fence = None
    for n, line in enumerate(text.split("\n"), 1):
        fm = FENCE_RE.match(line)
        if fm:
            if in_fence is None:
                in_fence = len(fm.group(2))
                if re.match(r"\{[\w:-]+\}", fm.group(3)) and not fm.group(3).startswith("{."):
                    warnings.append(f"{name}:{n}: leftover directive fence {line.strip()!r}")
            elif len(fm.group(2)) >= in_fence and not fm.group(3):
                in_fence = None
            continue
        if in_fence is None and re.search(r"\{(numref|ref|cite[:\w]*|glue|doc|term|eq)\}`", line):
            warnings.append(f"{name}:{n}: leftover role: {line.strip()[:80]!r}")


def main() -> int:
    check = "--check" in sys.argv
    texts = {nb: notebook_markdown(BOOK / nb) for nb in FILES}
    titles = collect_labels(texts)
    for nb, text in texts.items():
        qmd = FILES[nb][0]
        converted = convert_file(nb, text, titles)
        leftovers(qmd, converted)
        if not check:
            (BOOK / qmd).write_text(converted)
    for k in sorted(stats):
        print(f"{stats[k]:5d}  {k}")
    for w in warnings:
        print("WARNING:", w)
    return 1 if any("unresolved" in w or "leftover" in w for w in warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
