from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.template.loader import render_to_string, get_template
from weasyprint import HTML, CSS
from xhtml2pdf import pisa
from decimal import Decimal, InvalidOperation
from django.conf import settings
import os
import datetime
import json
from django.contrib.auth.decorators import login_required
from listas.models import Producto


def calcular_precio_final_completo(precio_base_usd, cotizacion_dolar, margen, dto1, dto2):
    precio = precio_base_usd * (1 - dto1 / 100)
    precio *= (1 - dto2 / 100)
    precio *= (1 + margen / 100)
    return round(precio * cotizacion_dolar, 2)


@login_required
def presupuesto_home(request):
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    return render(request, 'presupuestos/presupuesto.html', {'categorias': categorias})


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
                'medidas': p.medidas or '',
                'categoria': p.categoria or '',
                'ancho': p.ancho or 0,
            }
            for p in productos
        ]
    else:
        data = []
    return JsonResponse(data, safe=False)


class CrearPresupuestoView(View):
    def get(self, request):
        productos = Producto.objects.all()
        return render(request, 'crear_presupuesto.html', {'productos': productos})

    def post(self, request):
        form = PresupuestoForm(request.POST)
        if form.is_valid():
            presupuesto = form.save(commit=False)
            producto = Producto.objects.get(id=request.POST['producto'])

            cotizacion = float(request.POST['cotizacion'])
            margen = float(request.POST['margen'])
            descuento = float(request.POST['descuento'])
            descuento_adicional = float(request.POST['descuento_adicional'])

            presupuesto.producto = producto
            presupuesto.precio_final = calcular_precio_final_completo(
                producto.precio_unidad, cotizacion, margen, descuento, descuento_adicional
            )
            presupuesto.save()
            return redirect('lista_presupuestos')
        return render(request, 'crear_presupuesto.html', {'form': form})


class ListaPresupuestosView(View):
    def get(self, request):
        presupuestos = Presupuesto.objects.all()
        return render(request, 'lista_presupuestos.html', {'presupuestos': presupuestos})


class ExportarPresupuestoPDFView(View):
    def post(self, request, *args, **kwargs):
        try:
            cotizacion_dolar = Decimal(request.POST.get('cotizacion_dolar_hidden', '1.0').replace(',', '.'))
        except (InvalidOperation, AttributeError):
            cotizacion_dolar = Decimal('1.0')

        try:
            margen_ganancia_global = Decimal(request.POST.get('margen_ganancia_hidden', '0').replace(',', '.'))
        except (InvalidOperation, AttributeError):
            margen_ganancia_global = Decimal('0')

        productos_json = request.POST.get('productos', '[]')
        productos = json.loads(productos_json)

        productos_data = []
        total = Decimal('0.0')

        for producto in productos:
            try:
                producto_db = Producto.objects.get(id=producto.get('id'))
                cantidad = int(producto.get('cantidad', 1))
                precio_unitario = Decimal(producto.get('precioUnitario').replace(',', '.'))
                subtotal = precio_unitario * cantidad
                total += subtotal

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
                print(f"Error procesando producto: {producto}. Error: {e}")
                continue

        user = request.user
        user_nombre = user.get_full_name() or user.username
        user_celular = getattr(user, 'celular', 'No especificado')

        context = {
            'productos': productos_data,
            'fecha': datetime.date.today().strftime("%d/%m/%Y"),
            'fecha_vencimiento': (datetime.date.today() + datetime.timedelta(days=10)).strftime("%d/%m/%Y"),
            'total': "{:,.2f}".format(total).replace('.', 'X').replace(',', '.').replace('X', ','),
            'user_nombre': user_nombre,
            'user_celular': user_celular,
        }

        html_string = render_to_string('presupuestos/plantilla_presupuesto_pdf.html', context)
        css_path = os.path.join(settings.BASE_DIR, 'static/presupuestos/plantilla_presupuesto_pdf.css')
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf(stylesheets=[CSS(css_path)])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="presupuesto.pdf"'
        return response
