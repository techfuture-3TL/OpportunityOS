.PHONY: help install run test lint clean

help:
	@echo "Available commands:"
	@echo "  make install  - Install Python dependencies"
	@echo "  make run      - Start FastAPI backend on port 8001 with reload"
	@echo "  make test     - Run full test suite with pytest"
	@echo "  make clean    - Remove cached files and test artifacts"

install:
	pip install -r requirements.txt
	playwright install chromium

run:
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

test:
	python3 -m pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
