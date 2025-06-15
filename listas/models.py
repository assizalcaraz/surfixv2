from django.db import models

class Producto(models.Model):
    codigo = models.CharField(max_length=100, blank=True, null=True)
    grano = models.CharField(max_length=100, blank=True, null=True)
    precio_unidad = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    formato = models.CharField(max_length=100, blank=True, null=True)
    descuento = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    ad = models.CharField(max_length=100, blank=True, null=True)
    largo = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    ancho = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    
    litros = models.DecimalField(max_digits=2, decimal_places=0, blank=True, null=True)
    producto = models.CharField(max_length=100, blank=True, null=True)
    medidas = models.CharField(max_length=100, blank=True, null=True)
    unidades_x_caja = models.IntegerField(blank=True, null=True)
    categoria = models.CharField(max_length=100, null=True, blank=True) 

    def __str__(self):
        return self.codigo
