# 📓 Bitácora SurfixV2

> Registro cronológico de avances, decisiones y desvíos.

## 2025-06-16

### ✅ Despliegue completo en el VPS

* Configuración de **nginx** como proxy inverso con certificados SSL válidos mediante **Let's Encrypt** para:

  * `surfix.store`
  * `ofi.surfix.store`

* Configuración de:

  * `docker-compose.yml`
  * Archivos de entorno `.env.prod`
  * `Dockerfile` específico para producción (`prod.Dockerfile`)

### ⚠️ Errores detectados tras deploy inicial

* Recursos estáticos (`.css`, `.js`, `.png`) devolvían error **404**.
* **Hipótesis:** faltaba carpeta `static/` en el repositorio + errores de `collectstatic` y configuración de `nginx`.
* **Solución:**

  * `git push` de carpeta `static` desde entorno local.
  * `git pull` en el VPS.
  * Ejecutar `collectstatic` nuevamente.
* **Resultado:** recursos estáticos disponibles en frontend.

### 🌏 Delegación DNS

* Se delegó gestión DNS en **Cloudflare**.
* Se configuraron los registros para los subdominios mencionados.

### 🚀 Restricción de acceso a `/admin`

* Panel `/admin` protegido en `nginx` mediante:

  * `allow` por IP
  * `deny all` para otras IPs
* Verificado: accesos no autorizados reciben error **403 Forbidden**.

### ✅ Ajustes visuales

* Se mejoró experiencia en **dispositivos móviles**:

  * Tipografía adaptativa.
  * Estructura flexible.
* Se redefine el color `--bs-primary` de **Bootstrap** a naranja institucional `#ff4200`.

### 🔓 Usuario admin creado manualmente

* Comando utilizado:

  ```python
  from login.models import CustomUser
  user = CustomUser.objects.create_user(username='juan', password='claveSegura123')
  user.save()
  ```
