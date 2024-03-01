# myapp/urls.py

from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required, user_passes_test
def is_superuser(user):
    return user.is_superuser
urlpatterns = [
    #path('', client, name='client'),
    path('', client, name='client'),
    path('avoir/', avoir, name='avoir'),
    #path('compte_rendu/', compte_rendu, name='compte_rendu'),
    path('compte_rendu/', CompteRenduView.as_view(), name='compte_rendu'),
    path('compte_rendu_pdf/', generate_pdf, name='compte_rendu_pdf'),
    path('client/<int:client_id>/', client_details, name='client_details'),
    path('client/<int:client_id>/ajouter-avoir/', ajouter_avoir, name='ajouter_avoir'),
    path('client/<int:client_id>/consommer-avoir/', consommer_avoir, name='consommer_avoir'),
    path('add_client/', add_client, name='add_client'),
    path('test/', test, name='test'),
    path('familles/', login_required(familles, login_url='bl_login'), name='familles'),
    path('add_famille/', user_passes_test(is_superuser, login_url='bl_login')(add_famille), name='add_famille'),
    #path('edit_famille/<int:id>/', user_passes_test(is_superuser, login_url='bl_login')(edit_categorie), name='edit_categorie'),

    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    # Place other specific URLs above the generic one
    # ...

    # The generic URL pattern should be at the end
    #path('^(?P<path>.*)$', your_generic_view),
]
