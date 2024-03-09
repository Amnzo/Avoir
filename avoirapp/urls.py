# myapp/urls.py

from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required, user_passes_test
def is_superuser(user):
    return user.is_superuser
urlpatterns = [
    #path('', client, name='client'),
    path('',statistique,name='statistique'),
     path('dashboard/',dashboard,name='dashboard'),
    path('client/', client, name='client'),
    path('avoir/', avoir, name='avoir'),
    path('consommation_periode/', consommation_periode, name='consommation_periode'),
    path('display_facture/', display_facture, name='display_facture'),
    path('display_facture2/', display_facture2, name='display_facture2'),
    path('consommation_par_famille_par_mois/', consommation_par_famille_par_mois, name='consommation_par_famille_par_mois'),
    path('repertoires/', repertoire_list, name='repertoire_list'),
    path('valide_repertoire/', valide_repertoire, name='valide_repertoire'),
    path('edit_rep/<int:id>/', edit_rep, name='edit_rep'),
    path('add_rep/', add_rep, name='add_rep'),
    path('retours/', retour_list, name='retour_list'),
    path('consultation_list_retour/', consultation_list_retour, name='consultation_list_retour'),
    
    path('add_retour/', add_retour, name='add_retour'),
    path('edit_retour/<int:id>/', edit_retour, name='edit_retour'),
    path('valider_retour/<int:id>/', valider_retour, name='valider_retour'),
    path('confirme-validation/<int:id>/', confirme_validation, name='confirme_validation'),
    
    
    
 
     
    

    path('search_filter/', search_filter, name='search_filter'),
    #path('compte_rendu/', compte_rendu, name='compte_rendu'),
    path('compte_rendu/', CompteRenduView.as_view(), name='compte_rendu'),
    path('compte_rendu_pdf/', generate_pdf, name='compte_rendu_pdf'),
    path('client/<int:client_id>/', client_details, name='client_details'),
    path('client/<int:client_id>/ajouter-avoir/', ajouter_avoir, name='ajouter_avoir'),
    path('client/<int:client_id>/consommer-avoir/', consommer_avoir, name='consommer_avoir'),
    path('add_client/', add_client, name='add_client'),
    path('edit_client/<int:id>/', edit_client, name='edit_client'),
    path('test/', test, name='test'),
    path('familles/', login_required(familles, login_url='bl_login'), name='familles'),
    path('add_famille/', user_passes_test(is_superuser, login_url='bl_login')(add_famille), name='add_famille'),
    path('fetch_is_facture/', fetch_is_facture, name='fetch_is_facture'),
    path('edit_famille/<int:id>/', user_passes_test(is_superuser, login_url='bl_login')(edit_famille), name='edit_famille'),

    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    # Place other specific URLs above the generic one
    # ...

    # The generic URL pattern should be at the end
    #path('^(?P<path>.*)$', your_generic_view),
]
