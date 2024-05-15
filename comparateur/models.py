from django.db import models

# Create your models here.

from django.db import models


class Classeur(models.Model):
    nom=models.CharField(max_length=100)
    def __str__(self):
        return f"id: {self.id}-{self.nom}"



class ExcelData(models.Model):
    classeur = models.ForeignKey(Classeur, on_delete=models.CASCADE, default='')
    reference = models.CharField(max_length=100)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    UC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    HC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ISC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SCC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRB = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRCUV = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRBUV = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    RCC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    HSC = models.CharField(max_length=100, default='')
    SUNUC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SUNHC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SUNSCC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SUNUC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SUNUC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    POLA_UC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    POLA_ISC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


	

    def __str__(self):
        return f"id: {self.id} reference : {self.reference} remise : {self.remise}"

