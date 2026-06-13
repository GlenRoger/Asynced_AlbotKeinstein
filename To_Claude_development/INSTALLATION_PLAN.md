# Albot — Installation Approach

## Decision: uv + PowerShell

Installation is handled by a single PowerShell script. The goal is that a non-programmer
can run one script and end up with a working bot — no manual Python setup required.

## How it works

1. The PowerShell script checks if `uv` is installed. If not, it downloads and installs
   it automatically (via the official `uv` installer, one line).
2. `uv sync` reads `pyproject.toml` and installs the correct Python version plus all
   dependencies into a local `.venv` — no global Python installation needed.
3. The script creates two desktop shortcuts:
   - **Start Bot** — runs `uv run main.py`
   - **Start Dashboard** — runs `uv run dashboard.py` (or equivalent)

## Why uv

- `uv` can install Python itself, so the user does not need to visit python.org
- Fast installs — the large dependencies (PySide6 etc.) download and install quickly
- A lock file (`uv.lock`) ensures everyone gets the exact same versions every time
- Shortcuts call `uv run` directly, so the user never has to think about virtual environments

## Files to create

| File | Purpose |
|---|---|
| `pyproject.toml` | Declares Python version and all dependencies |
| `uv.lock` | Locks exact versions for reproducible installs |
| `install.ps1` | The one-shot install script (runs uv bootstrap + sync + creates shortcuts) |

## Auth / tokens

API keys and Twitch tokens are handled separately during a guided first-run session.
The install script does not touch these.
