#!/bin/bash

echo "⏳ Aplicando migraciones..."
if ! python manage.py migrate --noinput; then
    echo "❌ Error al aplicar migraciones"
    exit 1
fi

echo "📦 Recolectando archivos estáticos..."
if ! python manage.py collectstatic --noinput; then
    echo "❌ Error al recolectar archivos estáticos"
    exit 1
fi

echo "✅ Inicialización completa. Ejecutando servidor..."
exec "$@"
