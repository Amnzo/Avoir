from django.contrib import admin
from django import forms
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Seiko, StarVision

class RemiseForm(forms.Form):
    remise = forms.DecimalField(max_digits=10, decimal_places=2)
    date_debut_remise = forms.DateField(widget=forms.SelectDateWidget)
    date_fin_remise = forms.DateField(widget=forms.SelectDateWidget)

@admin.register(Seiko)
class SeikoAdmin(admin.ModelAdmin):
    list_display = ('reference', 'actif', 'remise', 'date_debut_remise', 'date_fin_remise')
    search_fields = ('reference',)
    actions = ['appliquer_remise']

    def appliquer_remise(self, request, queryset):
        if 'apply' in request.POST:
            form = RemiseForm(request.POST)
            if form.is_valid():
                remise = form.cleaned_data['remise']
                date_debut_remise = form.cleaned_data['date_debut_remise']
                date_fin_remise = form.cleaned_data['date_fin_remise']
                queryset.update(remise=remise, date_debut_remise=date_debut_remise, date_fin_remise=date_fin_remise)
                self.message_user(request, "La remise a été appliquée avec succès.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = RemiseForm()

        return render(request, 'excel/discount.html', {'form': form, 'products': queryset})
    
    appliquer_remise.short_description = "Appliquer une remise et une période sélectionnée"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('apply_discount/', self.admin_site.admin_view(self.appliquer_remise), name='apply_discount'),
        ]
        return custom_urls + urls

class StarvisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'reference', 'remise', 'prix', 'actif']
    search_fields = ['reference']  # Liste des champs à rechercher

admin.site.register(StarVision, StarvisionAdmin)
