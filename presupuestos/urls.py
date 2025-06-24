# Numero de revisión: 3

from django.urls import path
from .views import ExportarPresupuestoPDFView, PrevisualizarPDFView, presupuesto_home, generar_presupuesto, buscar_producto, exportar_csv

urlpatterns = [
    path('', presupuesto_home, name='presupuesto_home'),
    path('generar/', generar_presupuesto, name='generar_presupuesto'),
    path('buscar_producto/', buscar_producto, name='buscar_producto'),  # Verifica esta línea
    path('exportar_pdf/', ExportarPresupuestoPDFView.as_view(), name='exportar_presupuesto'),
    path('exportar_csv/', exportar_csv, name='exportar_csv'),
    path('previsualizar/', PrevisualizarPDFView.as_view(), name='previsualizar_pdf'),
]
