from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Seiko,StarVision

class SeikoaAdmin(admin.ModelAdmin):
    list_display = ['reference','remise']
    search_fields = ['reference'] 

    


class StarvisionaAdmin(admin.ModelAdmin):
    list_display = ['reference','remise']
    search_fields = ['reference']  # Liste des champs à rechercher

# Enregistrez le modèle ExcelData avec la classe d'administration personnalisée
admin.site.register(Seiko, SeikoaAdmin)
admin.site.register(StarVision,StarvisionaAdmin)

