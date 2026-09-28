winget install --id Git.Git -e
winget install --id astral-sh.uv -e

git clone https://github.com/AzgarRiad/acms.git
cd acms
uv sync
uv run uvicorn app.api.webapi:app --port 8000