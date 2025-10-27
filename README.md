# ChatUVisBox

Natural language interface for UVisBox uncertainty visualization.

## Installation

```bash
# Create conda environment
conda env create -f environment.yml
conda activate chatuvisbox

# Install with Poetry
poetry install
```

## Usage

```python
from chatuvisbox import run_graph

result = run_graph("Generate 30 curves and show a functional boxplot")
```

## Development

See `CLAUDE.md` for development guidelines.
