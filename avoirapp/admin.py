# myapp/admin.py

from django.contrib import admin
from django.db.models import Sum
from .models import Client, Avoir, Famille,Consommation
from django.utils.html import format_html

from django.db.models import Sum

class AvoirAdmin(admin.ModelAdmin):
    list_display = ('client', 'montant', 'date_ajout','display_facture_link')
    search_fields = ('client__nom', 'montant', 'date_ajout')
    list_filter = ('client', 'date_ajout')

    def display_facture_link(self, obj):
        # Display a PDF icon with a link to download the file in the admin list view
        if obj.facture:
            return format_html(f'<a href="{obj.facture.url}" target="_blank"><img src="/path/to/pdf_icon.png" alt="PDF" width="20" height="20"></a>')
        else:
            return '-'

    display_facture_link.allow_tags = True
    display_facture_link.short_description = 'Facture Link'



class ConsommationAdmin(admin.ModelAdmin):
    list_display = ('client', 'prix_achat','prix_vente', 'date_ajout','famille')
    search_fields = ('client__nom', 'prix_achat', 'date_ajout')
    list_filter = ('client', 'date_ajout')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'display_total_avoir_moins_consommation')
    search_fields = ('nom', 'prenom')

    def display_total_avoir_moins_consommation(self, obj):
        # Calculate total avoir
        total_avoir = Avoir.objects.filter(client=obj).aggregate(Sum('montant'))['montant__sum'] or 0

        # Calculate total consommation
        total_consommation = Consommation.objects.filter(client=obj).aggregate(Sum('prix_achat'))['prix_achat__sum'] or 0

        # Calculate total avoir moins total consommation
        total_avoir_moins_consommation = total_avoir - total_consommation
        return total_avoir_moins_consommation

    display_total_avoir_moins_consommation.short_description = 'Total Avoir - Total Consommation'


admin.site.register(Client, ClientAdmin)
admin.site.register(Avoir,AvoirAdmin)
admin.site.register(Consommation,ConsommationAdmin)

class FamilleAdmin(admin.ModelAdmin):
    list_display = ('id', 'famille')
admin.site.register(Famille,FamilleAdmin)
