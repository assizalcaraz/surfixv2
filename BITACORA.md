# 📓 Bitácora SurfixV2.0.2

> Registro cronológico de avances, decisiones y desvíos.

## 2025-06-24 → 2025-06-25

### ✅ Versión Surfix V2.0.2 — Lista de precios y presupuestador integrado

* Integración de un **presupuestador interactivo** con capacidad para:
  * Buscar productos desde la base de datos.
  * Agregarlos dinámicamente al presupuesto.
  * Ingresar cantidades y calcular automáticamente precios finales.
  * Exportar el resultado a **PDF**.

* Integración de módulo **"Composición de Precio"**:
  * Sección desplegable (`<details>`) con:
    * Cotización del dólar.
    * Descuentos por categoría (Dto1 y Dto2).
    * Margen de ganancia.
    * Descuento global extra.
  * Los valores modificables impactan dinámicamente en el precio final.

* Mejoras visuales y de usabilidad:
  * El buscador quedó **sticky** para mantenerse visible al hacer scroll.
  * Reorganización del módulo de composición para diferenciarlo del listado.
  * Agregado de columnas en la tabla para mostrar **grano** y **litros**.
  * Corrección de diseño mobile: estructura más ordenada en pantallas pequeñas.

### 🔎 Búsqueda de productos

* Ampliación del límite de resultados de búsqueda de **10 a 25 productos**.
* Inclusión de coincidencias por:
  * `producto`
  * `código`
  * `categoría` (con uso de `Q(...)` de Django).
* Verificado que productos como *"Lija Tela Esmeril Óxido de Aluminio"* ya aparecen al buscar por "esmeril", "tela", etc.

### 🐛 Correcciones y ajustes técnicos

* Solucionado problema donde el precio final no aplicaba descuentos ni márgenes (solo cotización).
* Se aplican correctamente los ajustes por categoría al seleccionar productos.
* Se incluyó fallback `"Sin categoría"` para productos sin categoría definida.
* Corregida la recuperación de campos `grano` y `litros` desde el backend hacia el JS.


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
