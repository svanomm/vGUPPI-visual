---
name: initialize-project
description: Initialize a project with a virtual environment and default packages.
---

Use this skill when there is no `.venv` folder in the repository, or if the user asks to initialize the project.

Run the following commands in the terminal:
```
uv init --python 3.12
uv add pandas matplotlib marimo[recommended]
git init
```