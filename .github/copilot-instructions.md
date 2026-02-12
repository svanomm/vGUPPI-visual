## Coding Standards and Practices
- You are working in a Windows 11 environment with Python 3.12.
- This repository uses uv as an environment manager in a virtual environment and ruff as a linter/formatter. 
- Use `uv run` to execute Python in the terminal.
- Use `uv add <package-name>` to add package to the environment.
- Add type hints to all Python functions and methods wherever possible.
- Add docstrings to all Python functions and methods using the Google style.
- After modifying Python scripts, run `uv run ruff check --fix;uv run ruff format` to ensure code quality and formatting standards are met. If any errors are reported, fix them before moving forward.
ALWAYS keep things simple. ALWAYS write small tests to confirm that your code works as expected.

## Project Details


## Housekeeping
- Source code is always saved in the `02 scripts` folder.
- Tests are always saved in the `03 temp` folder.
- If asked to create documentation, save it in the `05 notes` folder.