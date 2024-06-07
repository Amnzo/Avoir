# comparateur/urls.py
from django.urls import path

from comparateur.views import *


urlpatterns = [
    path('', read_pdf, name='comparateur_home'),
    #path('data/', data, name='data'),
    #path('delete/', delete, name='delete'),
    path('export_to_excel/', export_to_excel, name='export_to_excel'),
    path('ophtal/', ophtal, name='ophtal'),
    path('appliquer_remise/', appliquer_remise, name='appliquer_remise'),
    path('novadata/', novadata, name='novadata'),
    path('nova/', nova, name='nova'),
    #path('execute_sql_file/', execute_sql_file, name='execute_sql_file'),
    
    
    
    
    
    
    #path('generate_random_values/', generate_random_values, name='generate_random_values'),
    
    
    # Add more paths for other views as needed
]
