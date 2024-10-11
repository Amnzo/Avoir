# myapp/forms.py

from django import forms
from .models import Avoir, Client,Consommation,Famille,Teletransmition, Stock, Sav, Anomalie, RemiseBanque, Livraison, Litige
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
class CustomLoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)




class RepertoireSearchForm(forms.Form):
    search = forms.CharField(label='Rechercher', required=False)
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
    

class DateInput(forms.DateInput):
    input_type = 'date'
    format='%d/%m/%Y'

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'datenaissance']

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')

        # Vérifie si un client avec le même nom et prénom existe
        if Client.objects.filter(nom=nom, prenom=prenom).exists():
            raise ValidationError("Un client avec ce nom et prénom existe déjà.")

        return cleaned_data


class FamilleForm(forms.ModelForm):
    class Meta:
        model = Famille
        fields = ['famille', 'is_facture']




class CustomUserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)



    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')

        return password2
    



class GenericModelForm(forms.ModelForm):
    class Meta:
        model = None  # On spécifie pas de modèle ici

    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)
        super(GenericModelForm, self).__init__(*args, **kwargs)
        
        if model:
            self.Meta.model = model



