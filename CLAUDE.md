# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fig is a figlet ascii art text generator that creates png exports with transparent backgrounds. it's built as a standalone python script using uv's script syntax for dependency management.

**Key Architecture:**

- Single-file implementation (`fig.py`) using uv script dependencies
- Uses `pyfiglet` for ascii art generation and `pictex` for png rendering
- Pattern matching-based CLI argument parsing with both explicit and implicit syntax
- Environment variable configuration for defaults (font, text, canvas size, colors)

## Development Commands

**Setup:**
```bash
uv venv --python ">=3.12,<3.13"
uv pip install -r pyproject.toml --all-extras
```

**Running the script:**
```bash
uv run fig.py <command> <args>
# or directly (uses uv script syntax):
./fig.py <command> <args>
```

**Testing:**

```bash
uv run pytest -v                    # run all tests
uv run pytest tests/test_fig.py      # run specific test file
uv run pytest -k "test_preview"     # run tests matching pattern
```

**Code Quality:**

- Prefer regular comments over inline comments
  - If more than one line or 80 characters, add to relevant docstrings
- Never add emojis anywhere in the code base unless asked to
- Use case statements over long if/else conditionals

```bash
markdownlint -c .markdownlint.jsonc <FILE>      # lint markdown files
uv run ruff check                               # lint code
uv run ruff format                              # format code
uv run pre-commit run --all-files                # pre-commit hooks
```

## Command Interface

The script supports dual syntax modes:

**Explicit commands:**

- `fig.py preview [font] [text]` - Preview ASCII art in terminal
- `fig.py generate [font] [text] [file.png]` - Generate PNG image
- `fig.py list` - Show available fonts

**Implicit syntax (backwards compatibility):**

- `fig.py font text file.png` - Generate with specified font
- `fig.py text file.png` - Generate with default font
- `fig.py file.png` - Generate with all defaults

## Environment Configuration

Default behavior controlled by environment variables:

- `FIGLET_FONT` - Default font (larry3d)
- `FIGLET_TEXT` - Default text ("Hello, World!")
- `CANVAS_WIDTH/HEIGHT` - PNG canvas dimensions (728x90)
- `FONT_COLOR` - Text color (black)

## Dependencies

**Core runtime:** pyfiglet, pictex, python-decouple
**Development:** pytest, ruff, mypy
**Test utilities:** pytest-cov, pytest-xdist, hypothesis

## Context

- Context7 mcp libraries
  - astral-sh/uv
  - francozanardi/pictex
  - pwaller/pyfiglet
