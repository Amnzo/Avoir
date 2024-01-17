# myapp/urls.py

from django.urls import path
from .views import avoir,client,client_details,ajouter_avoir,consommer_avoir

urlpatterns = [
    # Your existing URL patterns go here
    path('', client, name='client'),
    path('avoir', avoir, name='avoir'),
    path('client/<int:client_id>/', client_details, name='client_details'),
    path('client/<int:client_id>/ajouter-avoir/', ajouter_avoir, name='ajouter_avoir'),
     path('client/<int:client_id>/consommer-avoir/', consommer_avoir, name='consommer_avoir'),

    
]
