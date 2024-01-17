# myapp/admin.py

from django.contrib import admin
from django.db.models import Sum
from .models import Client, Avoir
from django.utils.html import format_html
class AvoirAdmin(admin.ModelAdmin):
    list_display = ('client', 'montant', 'date_ajout', 'description', 'display_facture_link',"is_avoir")
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

class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'display_total_avoir')
    search_fields = ('nom', 'prenom')
    #inlines = [AvoirInline]

    def display_total_avoir(self, obj):
        # Calculate the total avoir or avoir_solde for the client
        total_avoir = Avoir.objects.filter(client=obj).aggregate(Sum('montant'))['montant__sum']
        return total_avoir if total_avoir is not None else 0
    
    display_total_avoir.short_description = 'Total Avoir'

admin.site.register(Client, ClientAdmin)
admin.site.register(Avoir,AvoirAdmin)
