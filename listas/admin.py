from django.contrib import admin
from .models import Producto

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'grano', 'precio_unidad', 'formato', 'descuento', 'ad', 'ancho', 'largo', 'litros', 'producto', 'medidas', 'unidades_x_caja', 'categoria')
    search_fields = ('codigo', 'grano', 'producto', 'precio_unidad', 'categoria')

admin.site.register(Producto, ProductoAdmin)
