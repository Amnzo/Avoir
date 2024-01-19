from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from avoirapp.models import Client, Famille

# Create your models here.
class Produit(models.Model):
    nom = models.CharField(max_length=50)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.nom} - {self.prix}'
class Bon_Commande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    categorie_d = models.ForeignKey(Famille, on_delete=models.CASCADE, related_name='commandes_d')
    produit_d = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='commandes_d')
    sphere_d = models.FloatField()
    cylindre_d = models.FloatField()
    axe_d = models.FloatField()
    quatite_d = models.IntegerField()
    
    categorie_g = models.ForeignKey(Famille, on_delete=models.CASCADE, related_name='commandes_g')
    produit_g = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='commandes_g')
    sphere_g = models.FloatField()
    cylindre_g = models.FloatField()
    axe_g = models.FloatField()
    quatite_g = models.IntegerField()
    date_de_bl = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return f'Bon_Commande for {self.client}'
