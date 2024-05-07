from django.db import models

# Create your models here.

from django.db import models


class Classeur(models.Model):
    nom=models.CharField(max_length=100)
    def __str__(self):
        return f"id: {self.id}-{self.nom}"

class ExcelData(models.Model):
    classeur = models.ForeignKey(Classeur, on_delete=models.CASCADE,default='')
    reference = models.CharField(max_length=100)
    UC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    HC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ISC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SCC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SRC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SRB = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SRCUV = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SRBUV = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    RCC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    HSC = models.CharField(max_length=100, null=True, blank=True)
    SUNUC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SUNHC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SUNSCC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SUNUC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    SUNUC = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    POLA_UC=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    POLA_ISC=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)	
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

	

    def __str__(self):
        return f"id: {self.id} reference : {self.reference}"

