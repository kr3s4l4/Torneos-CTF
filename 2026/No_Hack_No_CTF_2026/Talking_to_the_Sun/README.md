# SinGen

SinGen is a Flask and SQLite lyric-key service.

## Run

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The service stores durable runtime state under `data/`.
