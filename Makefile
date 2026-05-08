.PHONY: up down build logs restart ps clean dev dev-down dev-logs shell-backend shell-mongo

# --- Production ---

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

rebuild:
	docker compose build --no-cache

start: build up

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

restart:
	docker compose restart

restart-backend:
	docker compose restart backend

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans

shell-backend:
	docker compose exec backend bash

shell-mongo:
	docker compose exec mongo mongosh livesongbook

# --- Development ---
# Frontend: Vite dev server with HMR at http://localhost:5173
# Backend:  uvicorn --reload at http://localhost:8000
# Proxy:    vite.config.js forwards /api → backend:8000

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

dev-logs:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
