# AI Resume Assistant

A simple Python project that takes resume-related inputs like qualification, technical skills, projects, experience, and career objective, then generates:

1. Career objective
2. Technical skills section
3. Project descriptions

## Features

- Automatically infers a likely job role from the skill set
- Groups skills into categories such as languages, frameworks, tools, and AI/ML
- Generates polished resume sections from structured data
- Supports JSON input or interactive CLI input

## Setup

```bash
pip install -r requirements.txt
```

## Run with sample data

```bash
python main.py resume_input.json
```

## Run interactively

```bash
python main.py
```

## Output

The app saves the generated sections to `resume_output.txt`.
