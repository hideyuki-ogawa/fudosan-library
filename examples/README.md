# Examples

This directory contains notebooks and snippets demonstrating how to use
`fudosan-library` in interactive environments such as JupyterLab.

## Getting Started

1. Install dependencies with `uv` (or your preferred tool):

   ```bash
   uv pip install -e ..[dev,geo]
   ```

2. Launch JupyterLab from the project root:

   ```bash
   uv run jupyter lab examples/notebooks
   ```

3. Open `fudosan_client_intro.ipynb` and follow the steps to interact with the API.

The notebooks assume that the environment variable `FUDOSAN_API_KEY`
is set to your MLIT API key before starting JupyterLab.
