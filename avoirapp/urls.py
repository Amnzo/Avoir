from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(statistique), name='statistique'),
    path('dashboard/', login_required(dashboard), name='dashboard'),
    path('client/', login_required(client), name='client'),
    path('client_expired/', login_required(client_expired), name='client_expired'),

    
    path('avoir/', login_required(avoir), name='avoir'),
    path('consommation_periode/', login_required(consommation_periode), name='consommation_periode'),
    path('display_facture/', login_required(display_facture), name='display_facture'),
    path('display_facture2/', login_required(display_facture2), name='display_facture2'),
    path('consommation_par_famille_par_mois/', login_required(consommation_par_famille_par_mois), name='consommation_par_famille_par_mois'),
    path('credit_par_periode/', login_required(credit_par_periode), name='credit_par_periode'),
    path('repertoires/', login_required(repertoire_list), name='repertoire_list'),
    path('valide_repertoire/', login_required(valide_repertoire), name='valide_repertoire'),
    path('edit_rep/<int:id>/', login_required(edit_rep), name='edit_rep'),
    path('add_rep/', login_required(add_rep), name='add_rep'),
    path('retours/', login_required(retour_list), name='retour_list'),
    path('consultation_list_retour/', login_required(consultation_list_retour), name='consultation_list_retour'),
    path('add_retour/', login_required(add_retour), name='add_retour'),
    path('edit_retour/<int:id>/', login_required(edit_retour), name='edit_retour'),
    path('valider_retour/<int:id>/', login_required(valider_retour), name='valider_retour'),
    path('confirme-validation/<int:id>/', login_required(confirme_validation), name='confirme_validation'),
    path('add_user/', login_required(add_user), name='add_user'),
    path('list_user/', login_required(list_user), name='list_user'),
    path('profile/', login_required(profile), name='profile'),
    path('profile_user/<int:id>/', login_required(profile_user), name='profile_user'),
    path('search_filter/', login_required(search_filter), name='search_filter'),
    path('compte_rendu/', login_required(CompteRenduView.as_view()), name='compte_rendu'),
    path('compte_rendu_pdf/', login_required(generate_pdf), name='compte_rendu_pdf'),
    path('client/<int:client_id>/', login_required(client_details), name='client_details'),
    path('client/<int:client_id>/ajouter-avoir/', login_required(ajouter_avoir), name='ajouter_avoir'),
    path('client/<int:client_id>/consommer-avoir/', login_required(consommer_avoir), name='consommer_avoir'),
    path('editer_avoir/<int:id>/', login_required(editer_avoir), name='editer_avoir'),
    path('editer_consommation/<int:id>/', login_required(editer_consommation), name='editer_consommation'),
    path('add_client/', login_required(add_client), name='add_client'),
    path('edit_client/<int:id>/', login_required(edit_client), name='edit_client'),
    path('test/', login_required(test), name='test'),
    path('familles/', login_required(familles), name='familles'),
    path('add_famille/', login_required(add_famille), name='add_famille'),
    path('fetch_is_facture/', login_required(fetch_is_facture), name='fetch_is_facture'),
    path('edit_famille/<int:id>/', login_required(edit_famille), name='edit_famille'),
    path('saisie-vente/', saisie_vente, name='saisie_vente'),
    path('ventes-journee/', ventes_journee, name='ventes_journee'),
    path('ventes-cloturer_ventes/', cloturer_journee, name='cloturer_ventes'),
    path('valider_cloture', login_required(valider_cloture), name='valider_cloture'),
    path('edit_rendu/<int:id>/', login_required(edit_rendu), name='edit_rendu'),
    path('open_day/', login_required(open_day), name='open_day'),
    path('add/<str:model_name>/', add_item, name='add_item'),
    path('edit/<str:model_name>/<int:item_id>/', edit_item, name='edit_item'),
    path('vente_statistique/', vente_statistique, name='vente_statistique'),
    path('get_statistics/', get_statistics, name='get_statistics'),
   
    #path('global_statistique/', global_statistique, name='global_statistique'),
    
    path('data/', fill_dummy_data, name='data'),

    
    
    
    

    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
]
