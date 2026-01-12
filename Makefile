.PHONY: setup test lint format clean deploy

setup:
	@echo "Setting up development environment..."
	python -m venv venv
	source venv/bin/activate && pip install --upgrade pip
	source venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete! Edit .env with your credentials"

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v

lint:
	@echo "Running linters..."
	ruff check src/ tests/
	mypy src/

format:
	@echo "Formatting code..."
	black src/ tests/
	ruff check --fix src/ tests/

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info

run:
	@echo "Starting arbitrage detection system..."
	python -m src.workflows.arbitrage_detection_graph

docker-build:
	docker build -t polymarket-arbitrage-agent .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

deploy-staging:
	./scripts/deploy.sh staging

deploy-production:
	./scripts/deploy.sh production
