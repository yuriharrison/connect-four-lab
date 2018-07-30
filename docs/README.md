# Connect Four Lab Documentation

The documentation is in this directory under sources/ folder (automatically generated). The documentation uses extended Markdown, as implemented by [MkDocs](http://mkdocs.org).

## Building the documentation
------

- install [MkDocs](http://mkdocs.org)
    - `pip install mkdocs`
- install [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
    - `pip install mkdocs-material`
- install [CodeHilite](https://python-markdown.github.io/extensions/code_hilite/)
    - `pip install pygments`
- `cd` to the docs/ folder and run:
    - `python autogen.py`

- to preview the documetation run:
    - `mkdocs serve` # Starts a local webserver in `localhost:8000`
- to generate the static site in the `site/` folder run:
    - `mkdocs build`