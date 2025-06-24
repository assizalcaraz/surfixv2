# Numero de revisión: 1
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from decimal import Decimal, InvalidOperation
from django.conf import settings
import os
import datetime
from listas.models import Producto
import json

def presupuesto_home(request):
    return render(request, 'presupuestos/presupuesto.html')

class PrevisualizarPDFView(View):
    def post(self, request):
        ids = request.POST.getlist('ids[]')
        productos = Producto.objects.filter(id__in=ids)

        productos_data = []
        for producto in productos:
            productos_data.append({
                'producto': producto.producto,
                'medidas': producto.medidas,
                'grano': producto.grano,
                'litros': producto.litros or "",
                'unidades_x_caja': producto.unidades_x_caja or "",
                'precio_unidad': producto.precio_unidad,
            })

        context = {
            'productos': productos_data,
            'fecha': datetime.date.today().strftime("%d/%m/%Y"),
        }

        return render(request, 'presupuestos/plantilla_presupuesto_pdf.html', context)

def generar_presupuesto(request):
    productos = Producto.objects.all()
    return render(request, 'presupuestos/presupuestos.html', {'productos': productos})

def buscar_producto(request):
    query = request.GET.get('q', '').strip()
    if query:
        productos = Producto.objects.filter(producto__icontains=query)[:10]
        data = [
            {
                'id': p.id,
                'codigo': p.codigo,
                'nombre': p.producto,
                'precio_unidad': p.precio_unidad,
                'grano': p.grano or '',
                'litros': p.litros or '',
                'medidas': p.medidas or ''
            }
            for p in productos
        ]
    else:
        data = []
    return JsonResponse(data, safe=False)

def calcular_precio_final(precio_base_usd, cotizacion_dolar, margen_ganancia, descuento):
    # Aplica el descuento al precio base
    precio_descuento = precio_base_usd * (1 - (descuento / 100))
    # Calcula el precio con el margen de ganancia
    precio_ganancia = precio_descuento * (1 + (margen_ganancia / 100))
    # Convierte el precio a pesos
    precio_final = precio_ganancia * cotizacion_dolar
    return round(precio_final, 2)


def exportar_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lista_precios.csv"'

    writer = csv.writer(response)
    writer.writerow(['Código', 'Producto', 'Precio Base (USD)', 'Categoría'])

    productos = Producto.objects.all()
    for producto in productos:
        writer.writerow([
            producto.codigo,
            producto.producto,
            producto.precio_unidad,
            producto.categoria
        ])

    return response


class ExportarPresupuestoPDFView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Recuperar cotización del dólar
            cotizacion_dolar = Decimal(request.POST.get('cotizacion_dolar_hidden', '1.0').replace(',', '.'))
        except (InvalidOperation, AttributeError):
            cotizacion_dolar = Decimal('1.0')

        try:
            # Recuperar margen de ganancia global
            margen_ganancia_global = Decimal(request.POST.get('margen_ganancia_hidden', '0').replace(',', '.'))
        except (InvalidOperation, AttributeError):
            margen_ganancia_global = Decimal('0')

        productos_json = request.POST.get('productos', '[]')
        print(f"Datos enviados en POST: {request.POST}")  # Depuración de datos enviados
        productos = json.loads(productos_json)  # Deserializar JSON
        print(f"Productos recibidos: {productos}")  # Depuración de productos deserializados

        productos_data = []
        total = Decimal('0.0')

        for producto in productos:
            try:
                # Consultar en la base de datos para obtener los atributos faltantes
                producto_db = Producto.objects.get(id=producto.get('id'))
                cantidad = int(producto.get('cantidad', 1))
                precio_unitario = Decimal(producto.get('precioUnitario').replace(',', '.'))  # Precio desde la vista
                subtotal = precio_unitario * cantidad

                # Incrementar el total acumulado
                total += subtotal

                # Preparar datos combinados de la base de datos y la vista
                productos_data.append({
                    'producto': producto_db.producto,
                    'medidas': producto_db.medidas or (
                        f"{int(producto_db.ancho or 0)} mm x {int(producto_db.largo or 0)} mts"
                        if producto_db.ancho and producto_db.largo else "-"
                    ),
                    'grano': producto_db.grano or "-",
                    'litros': producto_db.litros or "-",
                    'unidades_x_caja': producto_db.unidades_x_caja or "-",
                    'cantidad': cantidad,
                    'precio_pesos': "{:,.2f}".format(precio_unitario).replace('.', 'X').replace(',', '.').replace('X', ','),
                    'subtotal': "{:,.2f}".format(subtotal).replace('.', 'X').replace(',', '.').replace('X', ','),
                })
            except (Producto.DoesNotExist, KeyError, InvalidOperation, ValueError) as e:
                print(f"Error procesando producto: {producto}. Error: {e}")  # Depuración
                continue

        print(f"Productos procesados para PDF: {productos_data}")  # Depuración

        # Contexto para la plantilla
        context = {
            'productos': productos_data,
            'fecha': datetime.date.today().strftime("%d/%m/%Y"),
            'fecha_vencimiento': (datetime.date.today() + datetime.timedelta(days=10)).strftime("%d/%m/%Y"),
            'total': "{:,.2f}".format(total).replace('.', 'X').replace(',', '.').replace('X', ','),
        }

        # Renderizar HTML y generar PDF
        html_string = render_to_string('presupuestos/plantilla_presupuesto_pdf.html', context)
        css_path = os.path.join(settings.BASE_DIR, 'static/presupuestos/plantilla_presupuesto_pdf.css')
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf(stylesheets=[CSS(css_path)])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="presupuesto.pdf"'
        return response
