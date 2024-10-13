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
    facture = forms.FileField(
        label='Facture',
        required=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'gif'])
        ],
    )

    class Meta:
        model = Avoir  # Remplacez Avoir par le nom de votre modèle
        fields = ['montant', 'facture']  # Assurez-vous que tous les champs nécessaires sont inclus

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
        validators=[FileExtensionValidator(allowed_extensions=['pdf','jpg','jpeg','png','gif'])],
         # Use HiddenInput to make it invisible
    )
    

class DateInput(forms.DateInput):
    input_type = 'date'
    format='%d/%m/%Y'

from django import forms
from django.core.exceptions import ValidationError
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'datenaissance']

    def __init__(self, *args, **kwargs):
        # Capture the instance if provided (for update)
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        datenaissance = cleaned_data.get('datenaissance')

        # Vérifie si un client avec le même nom, prénom et date de naissance existe
        # Exclure l'instance actuelle lors de la mise à jour
        if self.instance:
            if Client.objects.filter(nom=nom, prenom=prenom, datenaissance=datenaissance).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Un client avec ce nom, prénom et date de naissance existe déjà.")
        else:
            if Client.objects.filter(nom=nom, prenom=prenom, datenaissance=datenaissance).exists():
                raise ValidationError("Un client avec ce nom, prénom et date de naissance existe déjà.")

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



