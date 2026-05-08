.PHONY: up down build logs restart ps clean seed

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
