# 🛠️ SurfixV2.MANUAL.md

> Manual técnico y operativo para desarrollo, despliegue y mantenimiento del proyecto **SurfixV2**.

## ✏ï¸ Descripción general

SurfixV2 es una aplicación web desarrollada en Django, dockerizada para facilitar el despliegue y mantenimiento. Incluye una interfaz web protegida por autenticación y una versión estática visible en `surfix.ar`, con el backend funcionando bajo `ofi.surfix.ar`.

---

## 📂 Estructura de carpetas clave

```
SurfixV2/
├── docker/
│   └── nginx/
│       └── nginx.conf
│   └── prod.Dockerfile
├── app/
│   └── ... (código fuente Django)
├── static/
├── Makefile
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.prod
```

---

## ⚙️ Makefile: comandos y atajos definidos

### Desarrollo (opcional)

* `up-dev`: levanta el entorno de desarrollo con override:

  ```bash
  docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build -d
  ```

### Producción

* `up-prod`: levanta el entorno en modo producción:

  ```bash
  docker compose -f docker-compose.yml up --build -d
  ```

* `down`: detiene y elimina contenedores:

  ```bash
  docker-compose down
  ```

* `migrate`: ejecuta migraciones de base de datos:

  ```bash
  docker-compose exec web python manage.py migrate
  ```

* `createsuperuser`: crea un usuario administrador:

  ```bash
  docker-compose exec web python manage.py createsuperuser
  ```

* `collectstatic`: recolecta archivos estáticos para producción:

  ```bash
  docker-compose exec web python manage.py collectstatic --noinput
  ```

* `logs`: muestra logs en tiempo real:

  ```bash
  docker-compose logs -f
  ```

* `shell`: abre una shell interactiva de Django:

  ```bash
  docker-compose exec web python manage.py shell
  ```

* `restart`: reinicia los servicios:

  ```bash
  docker-compose restart
  ```

* `prune`: limpia recursos inactivos de Docker (incluye volúmenes):

  ```bash
  docker system prune -af --volumes
  ```

---

## 🌐 Dominios y acceso

* `https://surfix.ar`: landing institucional.
* `https://ofi.surfix.ar`: interfaz de la aplicación Django.
* `/admin`: acceso limitado por IP mediante Nginx.

---

## 🚨 Seguridad

* CSRF y CORS configurados correctamente en `settings.py`.
* Acceso a `/admin` bloqueado salvo IPs permitidas.
* Certificados SSL automáticos mediante Let's Encrypt.

---

## 🌟 Estilo visual y responsive

* Redefinido `--bs-primary` con color institucional naranja: `#ff4200`.
* `base.css` adaptado para dispositivos móviles (media queries).
* Inputs, botones y enlaces personalizados con el color naranja como foco visual.

---

## 🚜 Continuar desarrollando...

* Ver bitácora en `Bitacora Ensamble` para seguimiento diario.
* Considerar ocultar rutas sensibles (admin, API) y optimizar tiempo de carga.

---

© 2025 Surfix | Desarrollado por Assiz Alcaraz Baxter
