# Makefile

up-dev:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up --build -d

up-prod:
	docker compose -f docker-compose.yml up --build -d

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

createsuperuser:
	docker compose exec web python manage.py createsuperuser

collectstatic:
	docker compose exec web python manage.py collectstatic --noinput

logs:
	docker compose logs -f

shell:
	docker compose exec web python manage.py shell

restart:
	docker compose restart

prune:
	docker system prune -af --volumes
