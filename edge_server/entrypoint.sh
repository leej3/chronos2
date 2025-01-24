#!/bin/bash
set -e

uvicorn chronos.app:app --host 0.0.0.0 --port 5171
