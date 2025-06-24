# SurfixV2

Sistema de listas y presupuestos online para Plenor / Surfix. Desarrollado en Django + Docker + Nginx, con despliegue seguro en VPS.

## 💡 Características principales

* Generación de presupuestos a partir de catálogo
* Cálculo en tiempo real según cotización del dólar, descuentos y margen de ganancia
* Exportación de presupuestos en PDF
* Vista protegida por login
* Interfaz responsiva y adaptada a branding institucional
* Backend oculto bajo ruta `/admin`, protegido por IP en `nginx`

## 🚀 Despliegue en Producción

### ⚡ Requisitos

* VPS con Docker y Docker Compose
* Certificados SSL válidos (autogenerados por Let's Encrypt)
* DNS gestionado desde Cloudflare u otro proveedor

### ⚙ Instalación

1. Clonar repositorio

2. Crear archivo `.env.prod` con variables necesarias

3. Ejecutar:

   ```bash
   docker compose -f docker-compose.yml up --build -d
   ```

4. Ejecutar migraciones:

   ```bash
   docker compose exec web python manage.py migrate
   ```

5. Crear superusuario:

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. Recolectar archivos estáticos:

   ```bash
   docker compose exec web python manage.py collectstatic --noinput
   ```

### 🌐 Dominios

* [https://surfix.store](https://surfix.store) → landing institucional (HTML estático)
* [https://ofi.surfix.store](https://ofi.surfix.store) → aplicación Django con login y funcionalidades

## 🔧 Makefile

Comandos abreviados para desarrollo y mantenimiento:

```Makefile
up-prod:        docker compose -f docker-compose.yml up --build -d
down:           docker compose down
migrate:        docker compose exec web python manage.py migrate
createsuperuser:docker compose exec web python manage.py createsuperuser
collectstatic:  docker compose exec web python manage.py collectstatic --noinput
logs:           docker compose logs -f
shell:          docker compose exec web python manage.py shell
restart:        docker compose restart
prune:          docker system prune -af --volumes
```

## 🔒 Seguridad

* Protección CSRF habilitada
* Rutas críticas restringidas por IP desde `nginx`
* Uso de `.env` para variables sensibles

## 📅 Historial de cambios

Ver archivo [`Bitacora Ensamble`](./Bitacora%20Ensamble) para detalles técnicos y cronológicos.

---

© 2025 Assiz Alcaraz para Plenor / Surfix.
