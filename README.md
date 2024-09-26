# fh_utils

A collection of utilities for FastHTML projects

## Features

- :sparkles: **Fast reload** :sparkles: for a frictionless developer experience.
- CLI to easily run apps in both development and production modes.
- Seamless integration of Tailwind CSS / DaisyUI without any boilerplate.
- Jupyter notebook extension to run FastHTML apps.
- Icon packs support: Heroicons, Ionicons, Phosphor, Lucide, FontAwesome, Bootstrap, and Boxicons.

## Installation

```bash
pip install fh_utils
uv add fh_utils
```

::: {.callout-tip}
If you don’t like to _pip install_, feel free to copy and paste the code! The project is structured to make copying and pasting easy.
:::

## Dev

```bash
uv sync
uv run pytest
uv run examples/demo.py

rm -rf dist && uv build
uvx twine upload dist/*

quarto publish gh-pages docs
```
