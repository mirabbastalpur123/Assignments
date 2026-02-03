# CLAUDE.md - AI Assistant Guide

## Project Overview

This repository contains Python programming assignments and educational materials. The primary content consists of Jupyter notebooks created using Google Colaboratory, focusing on Python fundamentals and programming concepts.

## Repository Structure

```
Assignments/
├── CLAUDE.md                          # This guide for AI assistants
├── First-Assignment.ipynb             # Python basics Q&A notebook
└── First_Python_Assignment.ipynb      # Python basics Q&A (Colab version)
```

## File Types

### Jupyter Notebooks (.ipynb)
- Primary file format used in this repository
- Created and edited using Google Colaboratory
- Contains Python code cells with Q&A format covering Python fundamentals
- Can be opened in:
  - Google Colab (recommended for this project)
  - JupyterLab
  - VS Code with Jupyter extension

## Content Topics

The notebooks cover fundamental Python concepts including:
- Python history and creator (Guido van Rossum)
- Programming paradigms supported by Python
- Python syntax rules (case sensitivity, identifiers)
- File extensions and code execution (interpreted vs compiled)
- Code blocks (functions, classes, loops, conditionals)
- Comments and documentation
- Package management (PIP)
- Built-in functions

## Development Workflow

### Working with Notebooks
1. **Opening notebooks**: Use Google Colab via the badge link in the notebook or open locally with Jupyter
2. **Editing**: Add or modify code cells as needed
3. **Running**: Execute cells sequentially to test code
4. **Saving**: Notebooks auto-save in Colab; commit changes to git when complete

### Git Workflow
- Main development happens on feature branches
- Commits should be descriptive of changes made
- The repository originated from Google Colaboratory

## Conventions for AI Assistants

### When Modifying Notebooks
- Preserve existing cell structure unless changes are explicitly requested
- Keep Q&A format consistent with existing patterns
- Use `print()` statements for displaying questions and answers
- Maintain clear spacing between question blocks

### Code Style
- Use descriptive variable names
- Follow PEP 8 style guidelines for Python code
- Include explanatory text in answers
- Keep answers informative but concise

### Adding New Content
- Follow the established Q&A format pattern:
  ```python
  print('N) Question text?')
  print("Answer => Detailed answer text.")
  print("  ")
  ```
- Number questions sequentially
- Ensure answers are accurate and educational

### General Guidelines
- Do not modify notebook metadata unless necessary
- Preserve Colab compatibility links
- Test code changes before committing
- Keep the educational focus of the content

## Running the Notebooks

### Using Google Colab
1. Click the "Open in Colab" badge in the notebook
2. Run all cells or individual cells as needed
3. Changes can be saved back to GitHub

### Local Development
```bash
# Install Jupyter if not available
pip install jupyter

# Open notebook
jupyter notebook First-Assignment.ipynb
```

## Dependencies

- Python 3.x
- Jupyter Notebook / JupyterLab (for local development)
- Google Colab account (for cloud-based editing)

No additional Python packages are required for the current content.
