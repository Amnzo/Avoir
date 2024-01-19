# myapp/forms.py

from django import forms
from .models import Avoir, Client
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
class CustomLoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)



class AvoirForm(forms.ModelForm):
    class Meta:
        model = Avoir
        fields = ['montant','facture']
        




class AvoirConsumeForm(forms.ModelForm):
    class Meta:
        model = Avoir
        fields = ['montant', 'ean_13','famille']

    facture = forms.FileField(
        label='Facture',
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        widget=forms.HiddenInput()  # Use HiddenInput to make it invisible
    )

    def clean_ean_13(self):
        ean_13 = self.cleaned_data['ean_13']

        if not ean_13.isdigit() or len(ean_13) != 13:
            #raise ValidationError('EAN-13 Barcode must be a 13-digit numeric value.')
            raise ValidationError('Le code-barres EAN-13 doit être une valeur numérique de 13 chiffres.')

        return ean_13
    def __init__(self, *args, **kwargs):
        super(AvoirConsumeForm, self).__init__(*args, **kwargs)
        self.fields['ean_13'].required = True





class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'datenaissance']
    datenaissance = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True  # Set to True to make it required
    )