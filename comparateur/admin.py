from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import ExcelData,Classeur
class ExcelDataAdmin(admin.ModelAdmin):
    list_display = ['reference']
    search_fields = ['reference']  # Liste des champs à rechercher

# Enregistrez le modèle ExcelData avec la classe d'administration personnalisée
admin.site.register(ExcelData, ExcelDataAdmin)
admin.site.register(Classeur)

