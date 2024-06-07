from django.db import models

# Create your models here.

from django.db import models


class Classeur(models.Model):
    nom=models.CharField(max_length=100)
    def __str__(self):
        return f"id: {self.id}-{self.nom}"



class Seiko(models.Model):
    #classeur = models.ForeignKey(Classeur, on_delete=models.CASCADE, default='')
    reference = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)  # Nouveau champ

    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_debut_remise = models.DateField(null=True, blank=True)  # Date de début de la remise
    date_fin_remise = models.DateField(null=True, blank=True)  # Date de fin de la remise
    UC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    HC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ISC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SCC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRB = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRCUV = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SRBUV = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    RCC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SUNUC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SUNHC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SUNISC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    POLA_UC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    POLA_ISC = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self) -> str:
        return f"{self.reference}"


class StarVision(models.Model):
    #classeur = models.ForeignKey(Classeur, on_delete=models.CASCADE, default='')
    reference = models.CharField(max_length=100)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_debut_remise = models.DateField(null=True, blank=True)  # Date de début de la remise
    date_fin_remise = models.DateField(null=True, blank=True)  # Date de fin de la remise
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    actif = models.BooleanField(default=True)  # Nouveau champ

    def __str__(self) -> str:
        return f"{self.reference}- {self.prix}"



class NovaCell(models.Model):

    reference = models.CharField(max_length=100)
    SANSTR=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    DIAPLUS=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    MAJOR=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    SELISXT=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    GRAPHEN=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    AIRLISShock=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    BLUE_Shock=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    #TEINTE=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    def __str__(self) -> str:
        return f"{self.reference}"

class POL(models.Model):

    reference = models.CharField(max_length=100)
    DIAPLUS=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ARINTERNE=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    MAJOR=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    AIRLIS=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self) -> str:
        return f"{self.reference}"
    
class AKSESS(models.Model):

    reference = models.CharField(max_length=100)
    PRIX=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
   
    
    def __str__(self) -> str:
        return f" {self.reference}"
    
    

    


  







class Ophtal(models.Model):
    designation = models.CharField(max_length=255)
    prix_brut = models.DecimalField(max_digits=10, decimal_places=2)
    remise = models.DecimalField(max_digits=5, decimal_places=2)
    prix_net = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.designation



	

    def __str__(self):
        return f"id: {self.id} reference : {self.reference} remise : {self.remise}"

