# Runbook

## Local Development

### Prerequisites
- Docker and Docker Compose

### Start the app

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

App will be available at http://localhost:8501

### Run tests

```bash
docker compose -f infra/docker/docker-compose.yml run --rm app uv run pytest
```

### Run linting

```bash
docker compose -f infra/docker/docker-compose.yml run --rm app uv run ruff check .
```

### Stop everything

```bash
docker compose -f infra/docker/docker-compose.yml down
```

### Reset database

```bash
docker compose -f infra/docker/docker-compose.yml down -v
docker compose -f infra/docker/docker-compose.yml up --build
```

## Deployment (Cloud Run)

TBD - Will be configured with Terraform in `infra/terraform/`.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | For production |
| `SUPABASE_KEY` | Supabase anon/service key | For production |
| `DEBUG` | Enable debug mode | No (default: false) |
