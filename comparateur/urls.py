# comparateur/urls.py
from django.urls import path

from comparateur.views import *


urlpatterns = [
    path('', read_pdf, name='comparateur_home'),
    path('data/', data, name='data'),
    path('delete/', delete, name='delete'),
    path('export_to_excel/', export_to_excel, name='export_to_excel'),
     path('ophtal/', ophtal, name='ophtal'),
    
    
    path('generate_random_values/', generate_random_values, name='generate_random_values'),
    
    
    # Add more paths for other views as needed
]
