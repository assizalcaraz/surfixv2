#!/bin/sh

echo "Esperando a que PostgreSQL esté listo..."

python << END
import time
import socket

while True:
    try:
        with socket.create_connection(("db", 5432), timeout=1):
            break
    except OSError:
        time.sleep(1)
END

echo "PostgreSQL iniciado. Arrancando Gunicorn..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000
