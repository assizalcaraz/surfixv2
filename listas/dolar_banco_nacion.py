#/Surfix_v2/listas/dolar_banco_nacion.py

import requests
from bs4 import BeautifulSoup
import time

# URL de la página web
url = "https://www.bna.com.ar/Personas"  # Cambia esto con la URL específica de la página

# Valor de referencia para la cotización de venta del dólar
valor_referencia_venta = "1200"  # Cambia este valor de referencia según tus necesidades

def obtener_cotizacion_venta():
    # Realizar solicitud HTTP
    response = requests.get(url)
    response.raise_for_status()  # Verificar si la solicitud fue exitosa

    # Parsear el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscar el valor de la cotización de venta del dólar
    # Encontrar la fila que contiene "Dolar U.S.A" y luego el segundo <td> siguiente
    cotizacion_venta = soup.find("td", class_="tit", string="Dolar U.S.A").find_next("td").find_next("td").text.strip()

    return cotizacion_venta

def monitorear_cotizacion_venta():
    while True:
        try:
            # Obtener la cotización actual de venta
            cotizacion_venta_actual = obtener_cotizacion_venta()

            # Comparar con el valor de referencia
            if cotizacion_venta_actual != valor_referencia_venta:
                print(f"Cambio detectado: Cotización de venta actual = {cotizacion_venta_actual}")
                break
            else:
                print("Sin cambios en la cotización de venta.")
                
        except Exception as e:
            print(f"Error al obtener la cotización de venta: {e}")

        # Esperar antes de la próxima verificación
        time.sleep(60)  # Verificar cada 60 segundos

# Ejecutar el monitoreo
monitorear_cotizacion_venta()
