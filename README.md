<p align="center"></p>
<h2 align="center">GitIZI</h2>
<p align="center">
<a href="https://github.com/rgryta/gitizi/actions/workflows/main.yml"><img alt="Build" src="https://github.com/rgryta/gitizi/actions/workflows/main.yml/badge.svg?branch=main"></a>
<a href="https://pypi.org/project/gitizi/"><img alt="PyPI" src="https://img.shields.io/pypi/v/gitizi"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
<a href="https://github.com/PyCQA/pylint"><img alt="pylint" src="https://img.shields.io/badge/linting-pylint-yellowgreen"></a>
<a href="https://github.com/rgryta/NoPrint"><img alt="NoPrint" src="https://img.shields.io/badge/NoPrint-enabled-blueviolet"></a>

## About

Useful `git` scripts. Some of which utilizing AI.

Uses [GPT 4 Free](https://github.com/xtekky/gpt4free) Bing Provider for it's AI capabilities.

## Usage

### Command

Simply execute `check-bump` within a directory where your `pyproject.toml` is located. Or provide a path using `--path` argument.

```bash
user$ gitizi --help 
Usage: gitizi [OPTIONS] COMMAND [ARGS]...

  Git IZI entrypoint command

Options:
  --help  Show this message and exit.

Commands:
  ask      Ask AI
  current  Operations on current branch
  default  Print default branch name
```



## Development

### Installation

Install virtual environment and check_bump package in editable mode with dev dependencies.

```bash
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
```


### How to?

Automate as much as we can, see configuration in `pyproject.toml` file to see what are the flags used.

```bash
staging format  # Reformat the code
staging lint    # Check for linting issues
staging test    # Run unit tests and coverage report
```