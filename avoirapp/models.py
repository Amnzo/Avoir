# myapp/models.py

from django.db import models
from django.core.validators import FileExtensionValidator

class Client(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    datenaissance = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.nom
    
    def total_avoir_client(self):
        return self.avoir_set.aggregate(models.Sum('montant'))['montant__sum'] or 0

def upload_invoice_path(instance, filename):
    # This function defines the upload path for the PDF invoices.
    return f'avoir_invoices/{instance.client.nom}_{instance.date_ajout}_{filename}'

class Avoir(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajout = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    facture = models.FileField(
        upload_to=upload_invoice_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
         blank=False ,  # La facture est obligatoire
         null=True
    )
    is_avoir = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client.nom} - {self.montant} Dh"
