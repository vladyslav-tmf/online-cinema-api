#!/bin/sh

# Run web server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /app
