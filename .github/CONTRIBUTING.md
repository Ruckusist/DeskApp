# Contributing to Deskapp

Thanks for your interest in contributing!

## Getting started

- Requires Python >= 3.8
- We recommend using a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

If tests are present, install pytest and run:

```bash
pip install pytest
pytest -q
```

## Development workflow

- Create a feature branch from the default branch
- Keep commits small, with descriptive messages
- Open a Pull Request early for feedback
- Ensure CI is green before requesting review

## Coding standards

- Follow idiomatic Python practices (PEP 8)
- Type hints encouraged where practical

## Pull Requests

- Link related issues in the PR description
- Include tests when adding or changing behavior
- Update docs as needed

## Reporting security issues

Please do not open a public issue for security problems. See SECURITY.md for details.

