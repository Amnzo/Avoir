# myapp/forms.py

from django import forms
from .models import Avoir
from django.core.validators import FileExtensionValidator

class AvoirForm(forms.ModelForm):
    class Meta:
        model = Avoir
        fields = ['montant', 'description','facture']
        




class AvoirConsumeForm(forms.Form):
    model = Avoir
    fields = ['description', 'montant_a_consommer']
    montant_a_consommer = forms.DecimalField(
        label='Montant à consommer',
        min_value=0.01,  # Assurez-vous que le montant est positif
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )
    facture = forms.FileField(
        label='Facture',
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        widget=forms.HiddenInput()  # Use HiddenInput to make it invisible
    )