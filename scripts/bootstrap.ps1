$ErrorActionPreference = "Stop"
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
Write-Host "Bootstrap complete. Next: arcstone-adaptive-lab run --config configs/run-001.json --dry-run"
