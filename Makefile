up-dev:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build -d

up-prod:
	docker compose -f docker-compose.yml up --build -d

update-prod:
	@echo "📦 Backup de la base de datos..."
	docker exec surfixv2-db-1 pg_dump -U surfix_user surfix > backup_surfix_$$(date +%F_%H-%M).sql
	@echo "🧹 Bajando y eliminando volúmenes..."
	docker compose down -v
	@echo "🚀 Reconstruyendo contenedores..."
	docker compose up --build -d
	@echo "🕒 Esperando 10 segundos a que la base de datos arranque..."
	sleep 10
	@echo "🗃️ Restaurando backup..."
	cat backup_surfix_$$(ls -t backup_surfix_*.sql | head -n 1) | docker exec -i surfixv2-db-1 psql -U surfix_user surfix
	@echo "🎨 Ejecutando collectstatic..."
	docker compose exec web python manage.py collectstatic --noinput


down:
	docker-compose down

migrate:
	docker-compose exec web python manage.py makemigrations && docker-compose exec web python manage.py migrate

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

restart:
	docker-compose restart

prune:
	docker system prune -af --volumes
