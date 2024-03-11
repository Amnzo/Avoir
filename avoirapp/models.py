# myapp/models.py

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
class Client(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    datenaissance = models.DateField(blank=True, null=True)
    #email = models.EmailField(blank=True, null=True)
    #telephone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f' {self.nom} {self.prenom} '

    def total_consommation_client(self):
        return self.consommation_set.aggregate(models.Sum('prix_vente'))['prix_vente__sum'] or 0


    def total_avoir_client(self):
        #return self.avoir_set.aggregate(models.Sum('montant'))['montant__sum'] or 0
        avoir_total = self.avoir_set.aggregate(models.Sum('montant'))['montant__sum'] or 0
        consommation_total = self.total_consommation_client()
        solde=avoir_total-consommation_total
        return solde

def upload_invoice_path(instance, filename):
    # This function defines the upload path for the PDF invoices.
    return f'avoir_invoices/{instance.client.nom}_{instance.date_ajout}_{filename}'




def upload_invoice_path_retour(instance, filename):
    # Nom de fichier unique
    return f'retours_invoice/{filename}'


class Famille(models.Model):
    famille = models.CharField(max_length=255)
    is_facture=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_barre=models.BooleanField(default=False)
    # Other fields for the Family model can be added here

    def __str__(self):
        return self.famille

class Avoir(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajout = models.DateTimeField(default=timezone.now)
    #date_de_cmd = models.
    #description = models.TextField(blank=True, null=True)
    #ean_13 = models.CharField(max_length=13, verbose_name='EAN-13 Barcode', blank=False ,null=True)
    facture = models.FileField(
        upload_to=upload_invoice_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
         blank=True ,  # La facture est obligatoire
         null=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,default=1)
    #is_avoir = models.BooleanField(default=True)
    #famille = models.ForeignKey(Famille, on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return f"{self.client.nom} - {self.montant} Dh"


class Consommation(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajout = models.DateTimeField(default=timezone.now)
    designation = models.TextField(blank=False, null=False)
    code_barre = models.CharField(max_length=25, blank=True ,null=True)
    facture = models.FileField(
        upload_to=upload_invoice_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
         blank=True ,  # La facture est obligatoire
         null=True
    )
    famille = models.ForeignKey(Famille, on_delete=models.SET_NULL, null=True, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,default=1)

    def __str__(self):
        return f"{self.client.nom} - {self.prix_achat} Dh"



class Invoice(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True, editable=False,default='DEFAULT_VALUE')
    mois_concerne = models.CharField(max_length=7, unique=True)  # Assuming format 'MM-YYYY'

    def __str__(self):
        return f"Invoice: {self.invoice_number}, Month: {self.mois_concerne}"
    
class Repertoire(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20)
    fax = models.CharField(max_length=20,blank=True ,null=True)
    site_internet = models.URLField(max_length=200,blank=True ,null=True)
    identifiant = models.CharField(max_length=100,blank=True ,null=True)
    mot_de_passe = models.CharField(max_length=100,blank=True ,null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.nom


class Retour(models.Model):
    date= models.DateTimeField(default=timezone.now)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    fournisseur = models.CharField(max_length=100)
    marque=models.CharField(max_length=100,blank=True ,null=True,default="-")
    designation = models.CharField(max_length=100,blank=True ,null=True,)
    code = models.CharField(max_length=50,blank=True ,null=True)
    facture = models.FileField(
        upload_to=upload_invoice_path_retour,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
         blank=True ,  # La facture est obligatoire
         null=True
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

    def jours_ecoules(self):
        # Calculer la différence de jours entre la date de retour et la date actuelle
        difference = timezone.now() - self.date
        return difference.days