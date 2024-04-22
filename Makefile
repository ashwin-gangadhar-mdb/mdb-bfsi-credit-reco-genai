.PHONY: build up down logs backend frontend

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

backend:
	docker compose up -d backend

frontend:
	docker compose up -d frontend
