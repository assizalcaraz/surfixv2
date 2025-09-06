# Configuración de Gunicorn para producción
import multiprocessing
import os

# Número de workers (2x CPUs + 1, pero mínimo 2)
workers = max(2, multiprocessing.cpu_count() * 2 + 1)

# Configuración de workers
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts (en segundos)
timeout = 120
keepalive = 5
graceful_timeout = 30

# Configuración de logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload de la aplicación
preload_app = True

# Configuración de memoria
worker_tmp_dir = '/dev/shm'

# Configuración de procesos
bind = '0.0.0.0:8000'
