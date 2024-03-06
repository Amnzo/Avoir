# myapp/forms.py

from django import forms
from .models import Avoir, Client,Consommation,Famille
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
class CustomLoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)





class AvoirForm(forms.ModelForm):
    class Meta:
        model = Avoir
        fields = ['montant','facture']

    facture = forms.FileField(
        label='Facture',
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
         # Use HiddenInput to make it invisible
    )

class ConsommationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['famille'].queryset = Famille.objects.filter(is_active=True)
    class Meta:
        model = Consommation
        fields = ['prix_achat','prix_vente','designation','code_barre','famille','facture']

    facture = forms.FileField(
        label='Facture',
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
         # Use HiddenInput to make it invisible
    )
    code_barre = forms.FileField(
        label='code_barre',
        required=False,
       
         # Use HiddenInput to make it invisible
    )

class DateInput(forms.DateInput):
    input_type = 'date'
    format='%d/%m/%Y'

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'datenaissance']

    datenaissance = forms.DateField(
        widget=DateInput(),
        required=True
    )


class FamilleForm(forms.ModelForm):
    class Meta:
        model = Famille
        fields = ['famille', 'is_facture']
