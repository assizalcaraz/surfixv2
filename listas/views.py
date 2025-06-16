import os
import csv
import datetime
import locale
import pandas as pd
from decimal import Decimal
from bs4 import BeautifulSoup
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.staticfiles import finders
from django.urls import reverse
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from weasyprint import HTML, CSS
from .models import Producto
import requests

from django.contrib.auth.decorators import login_required

@login_required
def ventas(request):
    ...



# Configurar formato local para precios
try:
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

def obtener_cotizacion_dolar():
    url = "https://www.bna.com.ar/Personas"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    cotizacion_venta = soup.find("td", class_="tit", string="Dolar U.S.A").find_next("td").find_next("td").text.strip()
    return float(cotizacion_venta.replace(',', '.'))

def cotizacion_dolar_api(request):
    try:
        cotizacion = obtener_cotizacion_dolar()
        return JsonResponse({'cotizacion': cotizacion})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Encabezados esperados (en minúsculas)
expected_headers = {
    'codigo': ['codigo'],
    'grano': ['grano'],
    'precio_unidad': ['precio unidad (u$s)', 'precio x unidad', 'precio'],
    'formato': ['formato'],
    'descuento': ['descuento', 'dto.'],
    'ad': ['ad', 'ad.'],
    'largo': ['largo'],
    'ancho': ['ancho'],
    'litros': ['litros'],
    'producto': ['producto'],
    'medidas': ['medidas'],
    'unidades_x_caja': ['unidades x caja', 'rollos'],
    'cantidad': ['cantidad'],
    'numero': ['nº', 'numero']
}

omit_values = [
    "Precios en Dólares más iva",
    "FAIP SAIC",
    "Gral. Villegas 4344",
    "B1678BXD - Caseros. Pcia. de Buenos Aires",
    "Tel./Fax 4750-1132/0287/3460",
    "mail: pedidosventas@faipsa.com"
]

@login_required
def upload_file(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_file = request.FILES["excel_file"]
            categoria = request.POST.get("categoria")  # Captura la categoría seleccionada
            
            if not categoria:
                messages.error(request, "Debe seleccionar una categoría antes de subir el archivo.")
                return redirect('upload_file')
            
            # Leer el archivo Excel
            df = pd.read_excel(excel_file)
            request.session['df'] = df.to_dict()
            request.session['categoria'] = categoria  # Guardar la categoría en la sesión
            
            return redirect('validate_headers')  # Redirige a la validación de encabezados

    return render(request, 'listas/upload.html')

@login_required
def validate_headers(request):
    if request.method == 'POST':
        df = pd.DataFrame(request.session['df'])
        total_headers = int(request.POST['total_headers'])
        omit_text = request.POST.get('omit_text', '').strip()
        
        # Almacenar el texto a omitir en la sesión
        request.session['omit_text'] = omit_text

        for i in range(1, total_headers + 1):
            header = request.POST[f'attribute_{i}']
            if header != 'ninguno':
                original_header = df.columns[i - 1]
                df.rename(columns={original_header: header}, inplace=True)

        request.session['df'] = df.to_dict()
        return load_to_database(request, df)
    else:
        df = pd.DataFrame(request.session['df'])
        possible_headers = [header for sublist in expected_headers.values() for header in sublist]

        # Convertir todos los encabezados a minúsculas
        df.columns = [col.lower() for col in df.columns]
        df_filtered = df.dropna(how='all').reset_index(drop=True)  # Eliminar filas completamente vacías y resetear índice

        # Mensaje de depuración: Mostrar DataFrame después de filtrar filas vacías
        print("DataFrame después de eliminar filas vacías:")
        print(df_filtered)

        # Identificar la fila que contiene los encabezados correctos
        header_row_index = None
        for i, row in df_filtered.iterrows():
            print(f"Evaluando fila {i} con contenido: {row.dropna().tolist()}")  # Mensaje de depuración
            if set(row.dropna().str.lower().tolist()) & set(possible_headers):
                header_row_index = i
                break

        print(f"Índice de la fila de encabezados identificado: {header_row_index}")  # Mensaje de depuración

        if header_row_index is not None:
            header_row_index = int(header_row_index)  # Asegurarse de que header_row_index sea un entero

            # Verificar si el índice está presente en el DataFrame
            if header_row_index in df_filtered.index:
                print(f"El índice {header_row_index} está presente en el DataFrame.")  # Mensaje de depuración
                df_filtered.columns = df_filtered.iloc[header_row_index].str.lower()
                print("Nuevos encabezados del DataFrame:", df_filtered.columns.tolist())  # Mensaje de depuración
                df_filtered = df_filtered.drop(index=header_row_index).reset_index(drop=True)
                print("DataFrame después de eliminar la fila de encabezados:")  # Mensaje de depuración
                print(df_filtered.head())  # Mensaje de depuración

                # Si no falta ningún encabezado esperado, cargar datos directamente a la base de datos
                found_headers = df_filtered.columns.tolist()
                missing_headers = [header for header in expected_headers.keys() if header not in found_headers]

                # Si no falta ningún encabezado esperado, cargar datos directamente a la base de datos
                if not missing_headers:
                    return load_to_database(request, df_filtered)

                # Si faltan encabezados, mostrar la vista de validación manual
                request.session['filtered_df'] = df_filtered.to_dict()
                return render(request, 'listas/validate_headers.html', {
                    'headers': found_headers,
                    'possible_headers': list(expected_headers.keys()) + ['ninguno'],
                    'missing_headers': missing_headers,
                    'omit_text': request.session.get('omit_text', '')  # Enviar texto a omitir a la vista
                })
            else:
                print(f"El índice {header_row_index} no se encuentra en el DataFrame.")  # Mensaje de depuración
                return JsonResponse({'error': 'El índice de la fila de encabezados no se encuentra en el DataFrame.'})
        else:
            # Mostrar un mensaje de error más detallado
            return JsonResponse({'error': 'No se encontraron encabezados válidos. Asegúrese de que el archivo contenga los encabezados correctos.'})

@login_required
def validate_header(request):
    if request.method == 'POST':
        header = request.POST['header']
        attribute = request.POST['attribute']

        df_filtered = pd.DataFrame(request.session['filtered_df'])
        if attribute != 'ninguno':
            df_filtered.rename(columns={header: attribute}, inplace=True)
        request.session['filtered_df'] = df_filtered.to_dict()

        return JsonResponse({'status': 'Header validated'})



# Diccionario de referencia para tipos de productos
CODIGO_PRODUCTO_REFERENCIA = {
    # Rodillos y pinceles
    'RODLA': 'Rodillo Lana Natural',
    'RODTE': 'Rodillo Termofus. Epoxi',
    'RODMI': 'Mini Rodillo Epoxi',
    'PINGR': 'Pinceleta Gris Nº40',
    'PAÑLA': 'Paño de Lustrar Lana Natural',
    'VENSI': 'Venda Sintética',
    
    # Lijas
    'ROJA': 'Lija Roja Óxido de Aluminio',
    'ESMER': 'Lija Tela Esmeril Óxido de Aluminio',
    'AGUA': 'Lija al Agua Carburo de Silicio',
    'WF': 'Lija Antiempaste White Fill Óxido de Aluminio',
    
    # Discos abrasivos
    'K720': 'Disco Abrasivo Oxido de Aluminio',

    # Cintas RAPIFIX
    '00P80': 'Rapifix Nº 793 Peligro (sin adhesivo)',
    '2200': 'Rapifix Nº 2200 Antideslizante',
    '450': 'Rapifix Nº 450 Aisladora PVC',
    '790': 'Rapifix Nº 790 Espuma Negra Polietileno Doble Faz',
    '150': 'Rapifix Nº 150 Filamentosa',
    '270': 'Rapifix Nº 270 Aluminio 30µ',
    '650': 'Rapifix Nº 650 Help Tape',
    '365': 'Rapifix Nº 365 OPP 45µ Hogar y Oficina',
    '130': 'Rapifix Nº 130 OPP Invisible',
    '380': 'Rapifix Nº 380 OPP Doble Faz',
    '580': 'Rapifix Nº 580 Papel Doble Faz',
    '370': 'Rapifix Nº 370 OPP 45µ Impresa Transparente',
    '373': 'Rapifix Nº 373 OPP 45µ Impresa Blanco',
    '310': 'Rapifix Nº 310 OPP 50µ Transparente',
    '320': 'Rapifix Nº 320 OPP 45µ Colores',
    '340': 'Rapifix Nº 340 OPP 45µ Marrón',
    '350': 'Rapifix Nº 350 OPP 45µ Transparente',
    '510': 'Rapifix Nº 510 Arte y Diseño',
    '570': 'Rapifix Nº 570 Automotor Blanca',
    '560': 'Rapifix Nº 560 Automotor Verde Premium',
    '590': 'Rapifix Nº 590 Automotor Amarillo',
    '795': 'Rapifix Nº 795 Film Para Enmascarar Automotor/Obra',
    '540': 'Rapifix Nº 540 Papel Blanco Uso General',
    '520': 'Rapifix Nº 520 Papel Negro Uso General',
    '500': 'Rapifix Nº 500 Papel Enmascarar Blanco Obra',
    '550': 'Rapifix Nº 550 Papel Enmascarar Azul Obra Premium',

    # Cintas Fijapel
    '330': 'Cinta OPP Marrón Fijapel',
    '335': 'Cinta OPP Transparente Fijapel',

    # Pinturas
    '30120': 'Latex Int./Ext. Mate',
    '40270': 'Fijador',
}

# Define la función obtener_producto_desde_codigo de manera global
def obtener_producto_desde_codigo(codigo):
    """Busca claves en el código y devuelve el nombre del producto."""
    if not isinstance(codigo, str):
        return "Producto Desconocido"
    codigo_limpio = codigo.replace(" ", "").replace("-", "").upper()
    for clave, producto in CODIGO_PRODUCTO_REFERENCIA.items():
        if clave in codigo_limpio:
            return producto
    return "Producto Desconocido"

def sanear_productos(df):
    """
    Rellena las celdas vacías de 'producto' en el DataFrame usando un patrón en el código.
    Autocompleta las medidas combinando los valores de 'ancho' y 'largo'.
    Limpia datos inconsistentes.
    """
    # Hacer una copia explícita del DataFrame
    df = df.copy()

    # Filtrar registros con valores no numéricos en 'precio_unidad'
    print("Limpiando valores no numéricos en 'precio_unidad'...")
    df['precio_unidad'] = pd.to_numeric(df['precio_unidad'], errors='coerce')
    df = df.dropna(subset=['precio_unidad'])

    # Eliminar registros con precio_unidad == 0
    print("Eliminando registros con precio_unidad == 0...")
    df = df.loc[df['precio_unidad'] > 0].copy()

    # Rellenar 'producto' con la lógica de identificación
    print("Rellenando 'producto' usando el código...")
    df['producto'] = df['codigo'].apply(obtener_producto_desde_codigo)

    # Actualizar 'medidas' con 'ancho x largo' si está vacío
    if {'ancho', 'largo'}.issubset(df.columns):
        print("Actualizando 'medidas' con 'ancho x largo'...")
        df['medidas'] = df.apply(
            lambda row: f"{int(float(row['ancho']))} mm x {int(float(row['largo']))} mts"
            if pd.notna(row['ancho']) and pd.notna(row['largo']) else row.get('medidas', "-"),
            axis=1
        )

    # Convertir columnas 'ancho' y 'largo' a enteros
    for col in ['ancho', 'largo']:
        if col in df.columns:
            print(f"Redondeando columna '{col}' a enteros...")
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    print("Valores finales del DataFrame después de limpieza:")
    print(df.head())
    return df


def load_to_database(request, df=None):
    if df is None:
        df = pd.DataFrame(request.session['filtered_df'])

    categoria_asignada = request.session.get('categoria', None)
    omit_text = request.session.get('omit_text', '')

    if omit_text:
        df = df[~df.apply(lambda row: row.astype(str).str.contains(omit_text, case=False).any(), axis=1)]
    df = df[~df.apply(lambda row: row.astype(str).str.contains('|'.join(omit_values), case=False).any(), axis=1)]

    df = sanear_productos(df)

    for index, row in df.iterrows():
        codigo = row.get('codigo')
        if pd.notna(codigo):
            Producto.objects.update_or_create(
                codigo=codigo,
                defaults={
                    'producto': row.get('producto', ''),
                    'medidas': row.get('medidas', ''),
                    'grano': row.get('grano', ''),
                    'litros': row.get('litros', 0),
                    'unidades_x_caja': row.get('unidades_x_caja', 0),
                    'precio_unidad': row.get('precio_unidad', 0),
                    'categoria': categoria_asignada,
                }
            )

    # ✅ Mensaje para mostrar en la plantilla
    messages.success(request, "Los datos se cargaron correctamente.")
    return redirect('upload_file')  # Usa el name del `path()` de tu view upload_file

def configurar_listas(request):
    productos = Producto.objects.all()
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    productos_nombres = Producto.objects.values_list('producto', flat=True).distinct()
    return render(request, 'listas/configurar_listas.html', {'productos': productos, 'categorias': categorias, 'productos_nombres': productos_nombres})

@login_required
@csrf_protect
def asignar_categoria(request):
    if request.method == "POST":
        ids = request.POST.getlist('ids[]')
        nueva_categoria = request.POST['categoria']
        productos = Producto.objects.filter(id__in=ids)
        for producto in productos:
            producto.categoria = nueva_categoria  # Asignar nueva categoría al atributo 'producto'
            producto.save()
        return redirect('configurar_listas')
    return redirect('configurar_listas')

def asignar_producto(request):
    if request.method == "POST":
        ids = request.POST.getlist('ids[]')
        nuevo_producto = request.POST['producto']
        productos = Producto.objects.filter(id__in=ids)
        for producto in productos:
            producto.producto = nuevo_producto
            producto.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})

@login_required
def ventas(request):
    productos = Producto.objects.all()
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    return render(request, 'listas/ventas.html', {
        'productos': productos,
        'categorias': categorias,
    })


def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        raise Exception(f"URI de medios debe comenzar con {settings.MEDIA_URL} o {settings.STATIC_URL}")
    if not os.path.isfile(path):
        raise Exception(f"El archivo en el path {path} no existe")
    return path

class ExportarPDFView(View):
    def post(self, request, *args, **kwargs):
        cotizacion_dolar = Decimal(request.POST.get('cotizacion_dolar_hidden', '1.0').replace(',', '.'))
        ids = request.POST.getlist('ids[]')
        productos = Producto.objects.filter(id__in=ids)

        productos_data = []
        for producto in productos:
            categoria = producto.categoria
            descuento = Decimal(request.POST.get(f'descuento_{categoria}', '0'))
            descuento_adicional = Decimal(request.POST.get(f'descuento_adicional_{categoria}', '0'))
            margen_ganancia = Decimal(request.POST.get(f'margen_ganancia_{categoria}', '0'))

            precio_base = producto.precio_unidad
            precio_con_descuento = precio_base * (1 - descuento / 100)
            precio_con_descuento_adicional = precio_con_descuento * (1 - descuento_adicional / 100)
            precio_final = precio_con_descuento_adicional * (1 + margen_ganancia / 100) * cotizacion_dolar

            productos_data.append({
                'producto': producto.producto,
                'medidas': producto.medidas,
                'grano': producto.grano,
                'litros': producto.litros or "",
                'unidades_x_caja': producto.unidades_x_caja or "",
                'precio_pesos': locale.format_string("%.2f", precio_final, grouping=True),
            })

        context = {
            'productos': productos_data,
            'fecha': datetime.date.today().strftime("%d/%m/%Y"),
            'cotizacion_dolar': cotizacion_dolar,
            'user': request.user,  # <--- esto es lo clave

        }

        html_string = render_to_string('listas/plantilla_pdf.html', context)
        css_path = os.path.join(settings.BASE_DIR, 'static', 'listas', 'plantilla_pdf.css')
        if not os.path.exists(css_path):
            raise FileNotFoundError(f"No se encontró el archivo CSS en: {css_path}")

        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf(stylesheets=[CSS(css_path)])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="lista_precios.pdf"'
        return response
        
    
class PrevisualizarPDFView(View):
    def post(self, request):
        productos = Producto.objects.filter(id__in=request.POST.getlist('ids[]'))
        context = {'productos': productos}
        return render(request, 'listas/plantilla_pdf.html', context)

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

def buscar_producto(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(producto__icontains=query)[:10]
        data = [
            {
                'id': p.id,
                'nombre': p.producto,
                'precio_unidad': p.precio_unidad,
                'grano': getattr(p, 'grano', ''),
                'litros': getattr(p, 'litros', ''),
                'medidas': getattr(p, 'medidas', '')
            }
            for p in productos
        ]
    else:
        data = []
    return JsonResponse(data, safe=False)
