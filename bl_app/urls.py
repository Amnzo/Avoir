# myapp/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    #path('', client, name='client'),
    path('', index, name='index'),
    path('bl_list/', bl_list, name='bl_list'),
    path('generate_pdf/<int:bon_commande_id>/', generate_pdf, name='generate_pdf'),
    path('bl_login/', bl_custom_login, name='bl_login'),
    path('bl_logout/', bl_custom_logout, name='bl_logout'),

]
