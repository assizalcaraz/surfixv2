from django.urls import path
from . import views

urlpatterns = [
    path('api/cotizacion_dolar/', views.cotizacion_dolar_api, name='cotizacion_dolar_api'),
    path('upload/', views.upload_file, name='upload_file'),
    path('validate_headers/', views.validate_headers, name='validate_headers'),
    path('validate_header/', views.validate_header, name='validate_header'),
    path('load_to_database/', views.load_to_database, name='load_to_database'),
    path('configurar_listas/', views.configurar_listas, name='configurar_listas'),
    path('asignar_categoria/', views.asignar_categoria, name='asignar_categoria'),
    path('asignar_producto/', views.asignar_producto, name='asignar_producto'),
    path('ventas/', views.ventas, name='ventas'),
    path('exportar_pdf/', views.ExportarPDFView.as_view(), name='exportar_pdf'),
    path('previsualizar_pdf/', views.PrevisualizarPDFView.as_view(), name='previsualizar_pdf'),
    path('exportar_csv/', views.exportar_csv, name='exportar_csv'),

    
]
