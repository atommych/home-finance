# Home Finance SaaS — Makefile
# Run with: wsl bash -c "cd /mnt/d/workspace/2026/saas1/home-finance-saas && make <target>"
# All commands use Docker. No local Python required.

DC = docker compose -f infra/docker/docker-compose.yml

# ============================================================
# Development
# ============================================================

.PHONY: build up up-d down restart logs shell

build:
	$(DC) build

up:
	$(DC) up --build

up-d:
	$(DC) up --build -d

down:
	$(DC) down

restart: down up

logs:
	$(DC) logs -f

shell:
	$(DC) run --rm app bash

# ============================================================
# Testing & Linting
# ============================================================

.PHONY: test test-cov lint format check

test:
	$(DC) run --rm app bash -c 'uv pip install pytest -q && uv run pytest -v'

test-cov:
	$(DC) run --rm app bash -c 'uv pip install pytest pytest-cov -q && uv run pytest --cov=app --cov-report=term-missing'

lint:
	$(DC) run --rm app bash -c 'uv pip install ruff -q && uv run ruff check . && uv run ruff format --check .'

format:
	$(DC) run --rm app bash -c 'uv pip install ruff -q && uv run ruff check --fix . && uv run ruff format .'

check: lint test

# ============================================================
# Database
# ============================================================

.PHONY: db-up db-down db-reset db-shell

db-up:
	$(DC) up postgres -d

db-down:
	$(DC) stop postgres

db-reset:
	$(DC) down -v
	$(DC) up postgres -d

db-shell:
	$(DC) exec postgres psql -U homefinance -d homefinance

# ============================================================
# Production / Deploy
# ============================================================

.PHONY: build-prod deploy-manual tf-init tf-plan tf-apply

build-prod:
	docker build --target production -f infra/docker/Dockerfile -t home-finance:latest .

deploy-manual:
	@test -n "$(GCP_PROJECT)" || (echo "ERROR: make deploy-manual GCP_PROJECT=your-project-id" && exit 1)
	docker build --target production -f infra/docker/Dockerfile -t gcr.io/$(GCP_PROJECT)/home-finance:latest .
	docker push gcr.io/$(GCP_PROJECT)/home-finance:latest
	gcloud run deploy home-finance \
		--image gcr.io/$(GCP_PROJECT)/home-finance:latest \
		--region europe-west1 \
		--port 8501 \
		--allow-unauthenticated \
		--cpu 1 --memory 512Mi \
		--min-instances 0 --max-instances 3

tf-init:
	cd infra/terraform && terraform init

tf-plan:
	cd infra/terraform && terraform plan

tf-apply:
	cd infra/terraform && terraform apply

# ============================================================
# Help
# ============================================================

.PHONY: help
help:
	@echo ""
	@echo "Home Finance SaaS"
	@echo "=================="
	@echo ""
	@echo "Development:"
	@echo "  make build        Build Docker images"
	@echo "  make up           Start app + database (foreground)"
	@echo "  make up-d         Start app + database (background)"
	@echo "  make down         Stop all services"
	@echo "  make restart      Restart all services"
	@echo "  make logs         Follow container logs"
	@echo "  make shell        Open shell in app container"
	@echo ""
	@echo "Testing:"
	@echo "  make test         Run tests"
	@echo "  make test-cov     Run tests with coverage"
	@echo "  make lint         Check code style"
	@echo "  make format       Auto-format code"
	@echo "  make check        Run lint + tests"
	@echo ""
	@echo "Database:"
	@echo "  make db-up        Start Postgres only"
	@echo "  make db-reset     Destroy and recreate database"
	@echo "  make db-shell     Open psql shell"
	@echo ""
	@echo "Deploy:"
	@echo "  make build-prod   Build production image"
	@echo "  make deploy-manual GCP_PROJECT=xxx  Deploy to Cloud Run"
	@echo "  make tf-init      Initialize Terraform"
	@echo "  make tf-plan      Preview infrastructure changes"
	@echo "  make tf-apply     Apply infrastructure changes"
	@echo ""

.DEFAULT_GOAL := help
