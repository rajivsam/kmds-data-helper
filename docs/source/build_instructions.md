# Documentation Build Guide

This project uses **Sphinx** with the **MyST-Parser** to generate documentation from a mix of reStructuredText (.rst) and Markdown (.md) files.

## 1. Prerequisites

Ensure you have the required documentation tools installed via `uv`:

```bash
uv pip install sphinx myst-parser sphinx-rtd-theme
```

## 2. Directory Structure

The build system expects the following layout inside the `docs/` folder:

- `source/conf.py`: Configuration and extension settings.
- `source/index.rst`: The main Table of Contents.
- `source/*.rst`: "Wrapper" files that include Markdown content.
- `source/*.md`: Raw documentation content.

## 3. Build Commands

Run these from the **project root** directory:

**Standard Build:**

```bash
uv run sphinx-build -b html docs/source docs/_build/html
```

**Clean Build (Force Refresh):**
Use this if changes to included Markdown files aren't showing up:

```bash
uv run sphinx-build -E -a -b html docs/source docs/_build/html
```

## 4. Maintenance Notes

- **Including Markdown**: To include a Markdown file in an `.rst` file, use the following syntax:
  ```rst
  .. include:: ./filename.md
     :parser: myst_parser.sphinx_
  ```
- **Orphan Warnings**: If you include a `.md` file inside an `.rst` file, add the `.md` filename to `exclude_patterns` in `conf.py` to prevent "document not in toctree" warnings.
- **Persona Names**: Remember that persona files (`snake_case.yaml`) are automatically registered as **Title Case** in the system.
