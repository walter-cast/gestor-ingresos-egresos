from datetime import date

from django.db import models


# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


class Movimiento(models.Model):
    TIPOS = [
        (
            "ingreso",
            "Ingreso",
        ),
        ("gasto", "Gasto"),
    ]
    tipo = models.CharField(max_length=10, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField(default=date.today)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.tipo}: {self.monto} {self.categoria}"
