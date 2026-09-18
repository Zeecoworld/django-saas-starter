.PHONY: up down build migrate makemigrations shell superuser test lint fmt logs seed

up:
	docker compose up

build:
	docker compose build

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

shell:
	docker compose exec web python manage.py shell

superuser:
	docker compose exec web python manage.py createsuperuser

seed:
	docker compose exec web python manage.py seed_plans

test:
	docker compose exec web pytest

lint:
	docker compose exec web ruff check .

fmt:
	docker compose exec web ruff format .

logs:
	docker compose logs -f web
