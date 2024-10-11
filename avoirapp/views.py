from decimal import Decimal
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render,HttpResponse
from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
import openpyxl
from avoirapp.forms import AvoirForm,ConsommationForm,FamilleForm
from django.http import JsonResponse
from .models import Anomalie, Avoir, Client, Famille,Consommation, JourneeVente, Litige, Livraison, RemiseBanque, Repertoire, Retour, Sav, Stock, Teletransmition, Vente
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
import json
from django.contrib import messages
from django.utils import formats
from django.contrib.auth.models import User
# myapp/views.py

from django.contrib.auth import authenticate, login,logout
from .forms import ClientForm, CustomLoginForm, CustomUserRegistrationForm, GenericModelForm, RepertoireSearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page or home page
                return redirect('statistique')  # Change 'home' to your actual home page URL
            else:
                # Handle invalid login
                form.add_error(None, 'Invalid login credentials')
    else:
        form = CustomLoginForm()

    return render(request, 'login/login.html', {'form': form,'hide_menu': True})

# Create your views here.
@login_required(login_url='login')
def client(request):
    clients = Client.objects.annotate(total_avoir=Sum('avoir__montant')).order_by('-id').all()
    search = request.GET.get('search', '')

    if search:
        clients = clients.filter(Q(nom__icontains=search) | Q(prenom__icontains=search))
    print(clients)

    print(search)
    items_per_page = 8
    paginator = Paginator(clients, items_per_page)
    page = request.GET.get('page')
    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        clients = paginator.page(1)
    except EmptyPage:
        clients = paginator.page(paginator.num_pages)
    return render(request, 'clients/client.html', {'clients': clients,'search':search})


@login_required(login_url='login')
def client_expired(request):
    #clients_queryset = Client.objects.annotate(total_avoir=Sum('avoir__montant')).order_by('-id')
    clients_queryset = Client.objects.annotate(total_avoir=Sum('avoir__montant')).order_by('-id')
    clients = [client for client in clients_queryset if client.dernier_avoir_plus_de_24_mois()]
    search = request.GET.get('search', '')

    if search:
        clients = [client for client in clients if search.lower() in client.nom.lower() or search.lower() in client.prenom.lower()]
    print(clients)
    items_per_page = 8
    paginator = Paginator(clients, items_per_page)
    page = request.GET.get('page')
    try:
        clients = paginator.page(page)
    except PageNotAnInteger:
        clients = paginator.page(1)
    except EmptyPage:
        clients = paginator.page(paginator.num_pages)
    return render(request, 'clients/client_expire.html', {'clients': clients,'search':search})
@login_required(login_url='login')
def statistique(request):
  # Fetching data from the database
    families = Famille.objects.filter(is_active=True)
    consumption_data = []
    for family in families:
        consumption = Consommation.objects.filter(famille=family).count()
        consumption_data.append(consumption)

    # Converting data to JSON format
    data = {
        'labels': [family.famille for family in families],
        'data': consumption_data
    }
    data_json = json.dumps(data)

    total_clients = Client.objects.count()
    total_consomation =  Consommation.objects.aggregate(Sum('prix_vente'))['prix_vente__sum'] or 0
    total_avoirs = Avoir.objects.aggregate(Sum('montant'))['montant__sum'] or 0

    context = {
        'chart_data': data_json,
        'total_clients': total_clients,
        'total_consomation': total_consomation,
        'total_avoirs': total_avoirs
    }
    return render(request, 'dashbord/statistique.html', context)

from datetime import date, datetime, timedelta
import calendar
from collections import defaultdict
from django.db.models import Sum,functions,Count
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from .models import Avoir, Consommation

def dashboard(request):
    # Filtrer les objets Consommation
    consommations = Consommation.objects.order_by('date_ajout')

    # Grouper les consommations par année et mois
    consommations_groupes = defaultdict(list)
    for consommation in consommations:
        year_month = consommation.date_ajout.strftime('%Y-%m')
        consommations_groupes[year_month].append(consommation)

    # Préparer les données pour le rendu dans le modèle
    data = []
    for year_month, consommations in consommations_groupes.items():
        year, month = map(int, year_month.split('-'))
        data.append({
            'annee': year,
            'mois': month,
            'consommations': consommations
        })
    print(data)
    return render(request, 'dashbord/dashboard.html', {'data': data})


def lire_excel_avoir(request):
    # Construire le chemin complet vers le fichier Excel dans 'data'
    excel_file_path = os.path.join(settings.BASE_DIR, 'avoirapp', 'data', 'RETOURS.xlsx')
    # Liste pour stocker les données du fichier Excel
    data = []
    
    # Charger le fichier Excel avec openpyxl
    workbook = openpyxl.load_workbook(excel_file_path)
    worksheet = workbook.active  # Sélectionner la première feuille
    #Retour.objects.all().delete()

    for row in worksheet.iter_rows(values_only=True):
        print(row)
        date_excel = row[0]  # Suppose que la première colonne est 'Date'
        nom_prenom = row[1]  # Suppose que la deuxième colonne est 'Nom Prénom'
        fournisseur = row[2]  # Suppose que la troisième colonne est 'Fournisseur'
        marque = row[3]       # Suppose que la quatrième colonne est 'Marque'
        designation = row[4]  # Suppose que la cinquième colonne est 'Designation'
        date_renvoi = row[5]  # Suppose que la cinquième colonne est 'Designation'
        motif = row[7]        # Suppose que la sixième colonne est 'Motif'
       # Convertir la date depuis Excel
        if date_excel:
            # Convertir la date depuis Excel
            if isinstance(date_excel, datetime):  # Si la date est déjà au format datetime
                date_value = date_excel
            else:
                try:
                    date_value = datetime.strptime(date_excel, '%Y-%m-%d %H:%M:%S')  # Convertir depuis string si nécessaire
                except ValueError:
                    continue  # Si la conversion échoue, passer à la ligne suivante
        else:
            continue  # Si date_excel est None, ignorer cette ligne

        if date_renvoi:
            # Convertir la date depuis Excel
            if isinstance(date_renvoi, datetime):  # Si la date est déjà au format datetime
                date_value2 = date_renvoi
            else:
                try:
                    date_value2 = datetime.strptime(date_renvoi, '%Y-%m-%d %H:%M:%S')  # Convertir depuis string si nécessaire
                except ValueError:
                    continue  # Si la conversion échoue, passer à la ligne suivante
        else:
            continue  # Si date_excel est None, ignorer cette ligne
        if nom_prenom:
            try:
                nom, prenom = nom_prenom.split(' ', 1)  # Sépare en deux parties : nom et prénom
            except ValueError:
                nom = nom_prenom
                prenom = ''  # Si pas de prénom

            # Créer et sauvegarder l'objet Retour dans la base de données
        retour = Retour(
                date=date_value,
                date_renvoi=date_value2,
                nom=nom,
                prenom=prenom,
                fournisseur=fournisseur,
                marque=marque,
                designation=designation,
                motif=motif,
                is_active=False,
              
        )
        print(f" motif : {motif}")
        #print("ADD")
        #retour.save()
    return HttpResponse("Données importées avec succès avec les dates")
@login_required(login_url='login')
def avoir(request):
    items_per_page = 8
    
    # Query for Avoirs and paginate the results
    avoirs = Avoir.objects.all().order_by('-date_ajout')
    paginator = Paginator(avoirs, items_per_page)
    page = request.GET.get('page')
    try:
        avoirs = paginator.page(page)
    except PageNotAnInteger:
        avoirs = paginator.page(1)
    except EmptyPage:
        avoirs = paginator.page(paginator.num_pages)

    # Group Consommations by year, month, and famille
    consommations = Consommation.objects.order_by('-date_ajout')
    consommations_groupes = defaultdict(lambda: defaultdict(int))

    for consommation in consommations:
        year_month = consommation.date_ajout.strftime('%Y-%m')
        famille = consommation.famille
        consommations_groupes[year_month][famille] += 1  # Comptage des consommations par famille

    # Obtenir toutes les familles
    familles = set()
    for consommation in consommations:
        familles.add(consommation.famille)

    # Préparation des données pour le modèle de rendu
    data = []
    for year_month, consommations_familles in consommations_groupes.items():
        year, month = map(int, year_month.split('-'))
        consommations_data = [{'famille': famille, 'nombre_consommations': consommations_familles.get(famille, 0)}
                            for famille in familles]
        data.append({'annee': year, 'mois': month, 'consommations_familles': consommations_data})


    credits = Avoir.objects.order_by('-date_ajout')
    # Group Avoirs by year and month
    avoirs_groupes = defaultdict(list)
    for credit in credits:
        year_month = credit.date_ajout.strftime('%Y-%m')
        avoirs_groupes[year_month].append(avoir)

    # Prepare data for rendering in the template
    data2 = []
    for year_month, credits in avoirs_groupes.items():
        year, month = map(int, year_month.split('-'))
        data2.append({
            'annee': year,
            'mois': month,
            'credits': credits
        })
    familles =Famille.objects.filter(is_active=True)

    # Return the rendered template with the data
    return render(request, 'avoirs/avoir_list.html', {'avoirs': avoirs, 'data': data, 'data2': data2,'familles':familles})


def consommation_periode(request):
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        consommations = Consommation.objects.filter(date_ajout__range=[start_date, end_date])
        return render(request, 'avoirs/avoir_list.html', {'consommations': consommations})
    else:
        return render(request, 'votre_template.html', {})
    

from django.core import serializers

from django.http import JsonResponse
from django.core import serializers

from datetime import datetime
from django.http import JsonResponse
from django.core import serializers



from django.http import JsonResponse
from django.core import serializers
from .models import Consommation, Avoir
from datetime import datetime

def search_filter(request):
    if request.method == 'POST':
        type = request.POST.get('type')
        selected_families = request.POST.getlist('families[]')
        print(f"selected famille is {len(selected_families)}")
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        # Convert dates to ISO format
        start_date_iso = datetime.strptime(start_date, '%d-%m-%Y').date()
        end_date_iso = datetime.strptime(end_date, '%d-%m-%Y').date()
        if type == 'consommation':
            # Query consommations and select related client
            consommations = Consommation.objects.filter(
            date_ajout__gte=start_date_iso,
            date_ajout__lte=end_date_iso
             ).select_related('client')

            if len(selected_families) > 0 :
                consommations = consommations.filter(famille__in=selected_families)
            # Construct JSON response for consommations
            data = []
            for consommation in consommations:
                client_nom = consommation.client.nom
                client_prenom = consommation.client.prenom
                facture =""
                if consommation.facture:
                    facture ="yes"


                
                consommation_data = {
                    'client_nom': client_nom,
                    'client_prenom': client_prenom,
                    'famille': consommation.famille.famille,
                    'designation': consommation.designation,
                    'prix_achat': consommation.prix_achat,
                    'prix_vente': consommation.prix_vente,
                    'date_ajout': consommation.date_ajout,
                    'designation': consommation.designation,
                    'code_barre': consommation.code_barre,
                    'facture':facture,
                    
                    'id': consommation.id,
                    # Add other fields from Consommation model as needed
                }
                data.append(consommation_data)

        elif type == 'credit':
            # Query avoirs and select related client
            avoirs = Avoir.objects.filter(
                date_ajout__gte=start_date_iso,
                date_ajout__lte=end_date_iso
            ).select_related('client')


            # Construct JSON response for avoirs
            data = []
            for avoir in avoirs:
                client_nom = avoir.client.nom
                client_prenom = avoir.client.prenom
                print(avoir.facture)
                avoir_data = {
                    'client_nom': client_nom,
                    'client_prenom': client_prenom,
                    'montant': avoir.montant,
                    'date_ajout': avoir.date_ajout,
                    'id': avoir.id,
                   
                    
                  
                    # Add other fields from Avoir model as needed
                }
                data.append(avoir_data)

        else:
            # Invalid search type
            data = {'error': 'Type de recherche non valide'}

        return JsonResponse(data, safe=False)

    else:
        # Method not allowed
        data = {'error': 'Méthode de requête non autorisée'}
        return JsonResponse(data, status=400)



from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
import os


from django.shortcuts import get_object_or_404
from django.conf import settings
import os

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Avoir
import os

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

import os
from django.utils.text import slugify

def display_facture(request):
    if request.method == 'GET':
        facture_id = request.GET.get('facture_id')
        avoir = get_object_or_404(Avoir, id=facture_id)
        
        facture_path = avoir.facture.path
        avoir_date = avoir.date_ajout.strftime('%d-%m-%Y')
        filename = f'Credit_{slugify(avoir_date)}.pdf'
        
        if os.path.exists(facture_path):
            with open(facture_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/pdf')
                #response['Content-Disposition'] = 'attachment'  # Afficher dans le navigateur au lieu de télécharger
                #response['Content-Disposition'] = f'attachment; filename="Credit_{facture_id}"'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            return HttpResponse("Le fichier de la facture n'existe pas", status=404)
    else:
        return HttpResponse("Méthode non autorisée", status=405)
    

def display_facture2(request):
    if request.method == 'GET':
        facture_id = request.GET.get('facture_id2')
        avoir = get_object_or_404(Consommation, id=facture_id)
        
        facture_path = avoir.facture.path
        avoir_date = avoir.date_ajout.strftime('%d-%m-%Y')
        filename = f'Consommation_{slugify(avoir_date)}.pdf'
        
        if os.path.exists(facture_path):
            with open(facture_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/pdf')
                #response['Content-Disposition'] = 'attachment'  # Afficher dans le navigateur au lieu de télécharger
                #response['Content-Disposition'] = f'attachment; filename="Credit_{facture_id}"'
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            return HttpResponse("Le fichier de la facture n'existe pas", status=404)
    else:
        return HttpResponse("Méthode non autorisée", status=405)
    
import os
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from .models import Consommation, Famille

from django.template.loader import render_to_string
from weasyprint import HTML

def generate_pdf_consommation(consommations,title):
    html_string = render_to_string('pdf/consommation_par_famille.html', {'consommations': consommations,'title':title})
    pdf = HTML(string=html_string).write_pdf()
    return pdf

def generate_pdf_credit(avoirs,title):
    # Rendre le modèle HTML avec les données de consommation
    html_string = render_to_string('pdf/template_credit.html', {'avoirs': avoirs,'title':title})
    
    # Convertir le HTML en objet PDF
    pdf = HTML(string=html_string).write_pdf()
    return pdf

def consommation_par_famille_par_mois(request):
    if request.method == 'GET':
        famille_id = request.GET.get('famille_id')
        famille = Famille.objects.get(pk=famille_id)
        periode = request.GET.get('periode')
        mois, annee = map(int, periode.split('-'))
        consommations = Consommation.objects.filter(famille=famille,
                                                    date_ajout__month=mois,
                                                    date_ajout__year=annee)
        title=f"{famille} DU {mois}-{annee}"

        pdf_data = generate_pdf_consommation(consommations,title)

        filename = f"CONSOMMATIONS_{famille}_{mois}_{annee}.pdf"

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse("Méthode non autorisée", status=405)
    


def credit_par_periode(request):
    if request.method == 'GET':
        #famille_id = request.GET.get('famille_id')
        #famille = Famille.objects.get(pk=famille_id)
        periode = request.GET.get('periode')
        mois, annee = map(int, periode.split('-'))
        avoirs = Avoir.objects.filter( date_ajout__month=mois,date_ajout__year=annee)
        title=f"DES CREDITS DU {mois}-{annee}"

        pdf_data = generate_pdf_credit(avoirs,title)

        filename = f"CREDIT_{mois}_{annee}.pdf"

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse("Méthode non autorisée", status=405)






def client_details(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    avoirs = Avoir.objects.filter(client=client).order_by('-date_ajout')
    consomations = Consommation.objects.filter(client=client).order_by('-date_ajout')
    context = {
        'client': client,
        'avoirs': avoirs,
        'consommations': consomations }
    # You can add additional logic or context data here if needed
    return render(request, 'clients/client_details.html', context)

def ajouter_avoir(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = AvoirForm(request.POST, request.FILES)  # Ensure FILES is included
        if form.is_valid():
            avoir = form.save(commit=False)
            avoir.client = client
            print(f"l'utilisateur qui est ajouter est {request.user}")
            avoir.user = request.user
            avoir.save()
            messages.success(request, f'UNE CREDIT DE {avoir.montant} A BIEN ÉTÉ CRÉÉE', extra_tags='temp')
            return redirect('client_details', client_id=client.id)
    else:
        form = AvoirForm()

    return render(request, 'avoirs/ajouter_avoir.html', {'client': client, 'form': form})



def editer_avoir(request, id):
    avoir = Avoir.objects.get(pk=id)
   
    if request.method == 'POST':
        # Récupérer les données du formulaire depuis la requête POST
        montant = request.POST.get('montant')
        facture = request.FILES.get('facture')
        
        if facture:
            avoir.facture=facture
        date = request.POST.get('date')
        date_= datetime.strptime(date, '%d-%m-%Y').date()
        avoir.montant=montant
        avoir.date_ajout= date_
       
        
        # Enregistrer les modifications dans la base de données
        avoir.save()
        messages.success(request, f'LE CREDIT DE  A BIEN ÉTÉ CRÉÉE', extra_tags='temp')
        return redirect('client_details', client_id=avoir.client.id)
        
    return render(request, 'avoirs/editer_avoir.html', {'avoir': avoir})

def editer_consommation(request, id):
    conso = Consommation.objects.get(pk=id)
    familles=Famille.objects.all()
    print(familles)
   
    if request.method == 'POST':
        # Récupérer les données du formulaire depuis la requête POST
        prix_achat = request.POST.get('prix_achat')
        prix_vente = request.POST.get('prix_vente')
        designation = request.POST.get('designation')
        facture = request.FILES.get('facture')
        famille = request.POST.get('familles')
        print(famille)
        code=request.POST.get('code')
        print(code)
        conso.prix_achat=prix_achat
        conso.prix_vente=prix_vente
        conso.designation=designation
        date = request.POST.get('date')
        date_= datetime.strptime(date, '%d-%m-%Y').date()
        conso.date_ajout=date_
        if facture:
            conso.facture=facture
        if code :
            conso.code_barre=code
        if famille:
            f=Famille.objects.get(pk=famille)
            conso.famille=f
        
        # Enregistrer les modifications dans la base de données
        conso.save()
        messages.success(request, f'LA CONSOMMATION DE  A BIEN ÉTÉ MODIFIEE', extra_tags='temp')
        return redirect('client_details', client_id=conso.client.id)
        
    return render(request, 'avoirs/editer_consommation.html', {'conso': conso,'familles':familles})
    


def consommer_avoir(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    print(client)

    if request.method == 'POST':
        print(request)
        form = ConsommationForm(request.POST, request.FILES)
        if form.is_valid():
            prix_achat = form.cleaned_data['prix_achat']
            prix_vente = form.cleaned_data['prix_vente']
            designation=form.cleaned_data['designation']
            code_barre=form.cleaned_data['code_barre']
            
            print(form.cleaned_data)
            print(f"famille={form.cleaned_data['famille']}")
            facture = request.FILES.get('facture')
            # Vérifier si le montant à consommer est valide
            total_avoir = client.total_avoir_client()
            print(client.total_avoir_client())

            if prix_vente <= total_avoir:
                # Créer une instance de modèle Avoir pour représenter la consommation
                famille_name = form.cleaned_data['famille']
                famille_instance = get_object_or_404(Famille, famille=famille_name)
                consommation = Consommation.objects.create(
                    client=client,
                    prix_achat=prix_achat,
                    prix_vente=prix_vente,
                    designation=designation,
                    famille=famille_instance,
                    code_barre=code_barre,
                    user=request.user,

                    
                )
                if facture:
                    consommation.facture = facture
                    consommation.save()
              
                messages.success(request, f'UNE CONSOMATION DE {prix_vente} A BIEN ÉTÉ CRÉÉE', extra_tags='temp')

                return redirect('client_details', client_id=client.id)
            else:

                form.add_error('', f"VOUS NE POUVEZ PAS CONSOMMER PLUS QUE LE SOLDE CLIENT, QUI EST DE {total_avoir:.2f} DH.")
        else:
             return render(request, 'avoirs/consommer_avoir.html', {'form': form, 'client': client})

    else:
        #form = AvoirConsumeForm()
        form = ConsommationForm()
        print("Avoir form to display in you page")

    return render(request, 'avoirs/consommer_avoir.html', {'client': client, 'form': form})

def familles(request):
    familles=Famille.objects.all()
    return render(request, 'familles/familles.html', {'familles': familles})

def add_famille(request):
    #form = FamilleForm()
    if request.method == 'POST':
        is_facture=False
        is_active=False
        is_barre=False
        famille_name = request.POST.get('famille')
        facture=request.POST.get('is_facture')
        active=request.POST.get('is_active')
        barre=request.POST.get('is_barre')
        if facture=="on":
                is_facture=True
        if active=="on":
                is_active=True
        if barre=="on":
                is_barre=True

        Famille.objects.create(famille=famille_name,is_facture=is_facture,is_active=is_active,is_barre=is_barre)
        messages.success(request, 'FAMILLE A BIEN ÉTÉ CRÉÉE', extra_tags='temp')
        return redirect('familles')
    else:
        return render(request, 'familles/add_famille.html')

def edit_famille(request,id):
        famille=Famille.objects.get(pk=id)
        if request.method == 'POST':
            print(request.POST.get('is_active'))
            famille.famille=request.POST.get('famille')
            active=request.POST.get('is_active')
            facture=request.POST.get('is_facture')
            barre=request.POST.get('is_barre')
            if barre=="on":
                famille.is_barre=True
            else :
                famille.is_barre=False
            if active=="on":
                famille.is_active=True
            else :
                famille.is_active=False

            if facture=="on":
                famille.is_facture=True
            else :
                famille.is_facture=False

            famille.save()


            messages.success(request, 'FAMILLE A BIEN ÉTÉ MODIFIÉE', extra_tags='temp')

            return redirect('familles')  # Redirect to the category list page

        return render(request, 'familles/edit_famille.html',{'famille':famille})


""" def fetch_is_facture(request):
    famille_id = request.GET.get('famille_id')
    try:
        famille = Famille.objects.get(pk=famille_id)
        is_facture = famille.is_facture
        return JsonResponse({'is_facture': is_facture})
    except Famille.DoesNotExist:
        return JsonResponse({'error': 'Famille not found'}, status=404) """
    
def fetch_is_facture(request):
    famille_id = request.GET.get('famille_id')
    try:
        famille = Famille.objects.get(pk=famille_id)
        is_facture = famille.is_facture
        is_barre = famille.is_barre  # Ajout de la vérification is_barre
        return JsonResponse({'is_facture': is_facture, 'is_barre': is_barre})  # Retourne les deux valeurs
    except Famille.DoesNotExist:
        return JsonResponse({'error': 'Famille not found'}, status=404)





def custom_logout(request):
    logout(request)
    # Add any additional logic or redirect as needed
    return redirect('login')


def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f"VOUS AVEZ CRÉÉ LE CLIENT {form.cleaned_data['nom'].upper()} {form.cleaned_data['prenom'].upper()} AVEC SUCCÈS", extra_tags='temp')
                return redirect('client')  # Rediriger vers la liste des clients ou une autre page
            except IntegrityError:
                form.add_error(None, 'Un client avec ce nom et prénom existe déjà.')

                # Ajoute un message d'erreur dans le système de messages
                messages.error(request, "Erreur : Ce client existe déjà.")

    else:
        form = ClientForm(initial={'nom': '', 'prenom': '', 'datenaissance': ''})

    return render(request, 'clients/add_client.html', {'form': form})

def edit_client(request,id):
    client = Client.objects.get(pk=id)
    linked_ = []
    membres=[]
    if client.enfants_ids:
       # membres=
        membres=list(map(int, client.enfants_ids.split(',')))  
        linked_=Client.objects.filter(id__in=membres)
        print(linked_)
     
        

    # Print the list of child IDs to the console
    print(membres)  # This will display the list of IDs
    
    enfants = Client.objects.all()  # Récupérer tous les enfants
    if request.method == 'POST':
        form = ClientForm(request.POST,instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'VOUS AVEZ MODIFIÉ LE FICHIER DE {client.nom.upper()} {client.prenom.upper()} AVEC SUCCÈS', extra_tags='temp')
            return redirect('client')  # Replace 'client_list' with the URL name of the client list view
    else:

        form = ClientForm(instance=client)

    client = Client.objects.get(pk=id)
    return render(request, 'clients/edit_client.html', {'form': form,'enfants':enfants,'client':client,'membres': linked_})

@csrf_exempt  # Assurez-vous d'ajouter le décorateur CSRF si vous n'utilisez pas la protection CSRF
def ajouter_enfant(request):
    if request.method == 'POST':
        client_id = request.POST.get('id')
        enfant_id = request.POST.get('enfant_id')
        
        client = Client.objects.get(pk=client_id)
        client.ajouter_enfant(enfant_id)  # Utiliser la méthode pour ajouter un enfant
        
        return JsonResponse({'success': True})  # Retourner une réponse JSON
    return JsonResponse({'success': False}, status=400)  # Erreur si ce n'est pas une requête POST
from django.views.decorators.http import require_http_methods
@require_http_methods(["DELETE"])
def delete_member(request, id, enfant_id):
    try:
        # Get the client instance based on the provided ID
        client = Client.objects.get(id=id)
        
        # Split the enfants_ids into a list of integers
        enfants_list = list(map(int, client.enfants_ids.split(',')))

        # Remove all instances of the enfant_id from the list
        enfants_list = [e for e in enfants_list if e != enfant_id]

        # Join the list back into a comma-separated string
        client.enfants_ids = ','.join(map(str, enfants_list))

        # Save the updated client object
        client.save()

        return JsonResponse({'success': True})
    except Client.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Client not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
from django.db.models import Count
def compte_rendu(request):
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')

        results = Avoir.objects.filter(date_ajout__range=[start_date, end_date], is_avoir=False).values('famille__famille').annotate(nombre=Count('famille'))
        results_list = list(results)

        return render(request, 'compte_rendu.html', {'results': results_list})

    return render(request, 'compte_rendu.html')
#------------------------------Repertoire----------------------------
# Dans votre fichier views.py



from django.db.models import Q

def repertoire_list(request):
    # Récupérer tous les enregistrements du modèle Repertoire
    repertoires = Repertoire.objects.filter(is_active=True).order_by('-id')
    # Si une requête de recherche est soumise
    if request.method == 'GET' and request.GET.get('search'):
        print(f"recherche somit = {request.GET.get('search')}")
        search_query = request.GET.get('search')
        
        repertoires = Repertoire.objects.filter(
            Q(nom__icontains=search_query) |
            Q(adresse__icontains=search_query) |
            Q(telephone__icontains=search_query) |
            Q(fax__icontains=search_query) |
            Q(site_internet__icontains=search_query) |
            Q(identifiant__icontains=search_query),
            is_active=True
        )

    search_form = RepertoireSearchForm()
    return render(request, 'rep/rep.html', {'repertoires': repertoires, 'search_form': search_form})






def valide_repertoire(request):
    if request.method == 'POST':
        print(request.POST.get('id_rep'))
        rep=Repertoire.objects.get(pk=request.POST.get('id_rep'))
        rep.is_active=True
        rep.save()
        print("Post")

    
    repertoires = Repertoire.objects.filter(is_active=False).order_by('-id')
    return render(request, 'rep/valider.html', {'repertoires': repertoires})



def edit_rep(request,id):
    repertoire = Repertoire.objects.get(pk=id)
    print(repertoire)
    if request.method == 'POST':
        # Récupérer les données du formulaire depuis la requête POST
        nom = request.POST.get('nom')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        fax = request.POST.get('fax')
        site_internet = request.POST.get('site_internet')
        identifiant = request.POST.get('identifiant')
        mot_de_passe = request.POST.get('mot_de_passe')
        
        # Mettre à jour les champs du répertoire avec les nouvelles valeurs
        repertoire.nom = nom
        repertoire.adresse = adresse
        repertoire.telephone = telephone
        repertoire.fax = fax
        repertoire.site_internet = site_internet
        repertoire.identifiant = identifiant
        repertoire.mot_de_passe = mot_de_passe
        
        # Enregistrer les modifications dans la base de données
        repertoire.save()
        #messages.success(request, f'UNE CONSOMATION DE {prix_vente} A BIEN ÉTÉ CRÉÉE')
        messages.success(request, f'Le répertoire "{nom}" a été créé avec succès.')
        return redirect('repertoire_list')  # Rediriger vers la liste des répertoires après la mise à jour
    return render(request, 'rep/edit.html', {'repertoire': repertoire})





def add_rep(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire depuis la requête POST
        nom = request.POST.get('nom')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        fax = request.POST.get('fax')
        site_internet = request.POST.get('site_internet')
        identifiant = request.POST.get('identifiant')
        mot_de_passe = request.POST.get('mot_de_passe')
        
        # Create a new Repertoire object
        repertoire = Repertoire.objects.create(
            nom=nom,
            adresse=adresse,
            telephone=telephone,
            fax=fax,
            site_internet=site_internet,
            identifiant=identifiant,
            mot_de_passe=mot_de_passe
        )
        
        # Enregistrer les modifications dans la base de données
        repertoire.save()
        messages.success(request, f'Le répertoire "{nom}" a été modiféé avec succès.', extra_tags='temp')
        
        return redirect('repertoire_list')  # Rediriger vers la liste des répertoires après la mise à jour
    return render(request, 'rep/add.html')


#--------------------Gestion Retour----------------------------

from django.utils import timezone

def retour_list(request):
    retours = Retour.objects.filter(facture='').order_by('-date')
    maintenant = timezone.now()
    maintenant_moins_25_jours = maintenant - timedelta(days=25)
    search_query=""
    couleurs= []

    # Filtrer les enregistrements en fonction de la recherche de nom
    if request.method == 'GET' and request.GET.get('search'):
        search_query = request.GET.get('search')
        print(search_query)
        retours = retours.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(marque=search_query) |
            Q(fournisseur__icontains=search_query)
        )

    # Filtrer les enregistrements en fonction de la couleur et de la présence de facture
    if request.method == 'GET' and request.GET.getlist('couleur[]'):
        couleurs = request.GET.getlist('couleur[]')
        print(couleurs)
        filtered_retours = []
        for retour in retours:
            jours_ecoules = retour.jours_ecoules()  # Assurez-vous que la méthode est appelée correctement
            if 'orange' in couleurs and 0 <= jours_ecoules <= 25 and not retour.facture:
                filtered_retours.append(retour)

            if 'rouge' in couleurs and jours_ecoules > 25 and not retour.facture :
                filtered_retours.append(retour)
        retours = filtered_retours

    context = {
        'retours': retours,
        'maintenant_moins_25_jours': maintenant_moins_25_jours,
        'search_query': search_query,
        'couleurs': request.GET.getlist('couleur[]')
    }

    return render(request, 'retours/retour.html', context)

def consultation_list_retour(request):
    #retours = Retour.objects.filter(facture='')
    retours = Retour.objects.exclude(facture='').order_by('-date')
    search_query=""
    # Filtrer les enregistrements en fonction de la recherche de nom
    if request.method == 'GET' and request.GET.get('search'):
        search_query = request.GET.get('search')
        print(search_query)
        retours = retours.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(designation__icontains=search_query) |
            Q(marque=search_query) |
            Q(fournisseur__icontains=search_query)
        )
    context = {
        'retours': retours,
        'search_query': search_query,

    }

    return render(request, 'retours/consulter.html', context)



def add_retour(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire depuis la requête POST
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        fournisseur = request.POST.get('fournisseur')
        designation = request.POST.get('designation')
        marque = request.POST.get('marque')
        code = request.POST.get('code')
        motif = request.POST.get('motif')
        facture = request.FILES.get('facture')  # Utilisez FILES pour récupérer le fichier de la facture
        
        # Créer un nouvel objet Retour
        retour = Retour.objects.create(
            marque=marque,
            nom=nom,
            prenom=prenom,
            fournisseur=fournisseur,
            designation=designation,
            code=code,
            motif=motif,
            facture=facture  # Assignez le fichier de la facture
        )
        
        # Enregistrer les modifications dans la base de données
        retour.save()
        messages.success(request, 'Le retour a été ajouté avec succès.', extra_tags='temp')
        
        return redirect('retour_list')  # Rediriger vers la liste des retours après l'ajout
    return render(request, 'retours/add.html')




def edit_retour(request, id):
    retour = Retour.objects.get(pk=id)
    previous_url = request.GET.get('previous_url', '')
    print(f"referer_url={previous_url}")   
    if request.method == 'POST':
        # Récupérer les données du formulaire depuis la requête POST
        nom = request.POST.get('nom')
        marque = request.POST.get('marque')
        prenom = request.POST.get('prenom')
        fournisseur = request.POST.get('fournisseur')
        designation = request.POST.get('designation')
        code = request.POST.get('code')
        motif = request.POST.get('motif')
        facture = request.FILES.get('facture')  # Utilisez FILES pour récupérer le fichier de la facture
        date = request.POST.get('date')
        date_retour= datetime.strptime(date, '%d-%m-%Y').date()
        # Mettre à jour les champs du retour avec les nouvelles valeurs
        retour.nom = nom
        retour.date=date_retour
        retour.marque = marque
        retour.prenom = prenom
        retour.fournisseur = fournisseur
        retour.designation = designation
        retour.code = code
        retour.motif = motif
        
        if facture:  # Vérifiez si un nouveau fichier de facture a été fourni
            retour.facture = facture
        
        # Enregistrer les modifications dans la base de données
        retour.save()
        messages.success(request, f'Le retour "{nom}" a été modifié avec succès.', extra_tags='temp')
        return HttpResponseRedirect(previous_url)
        #return redirect('retour_list')  # Rediriger vers la liste des retours après la mise à jour
    
    return render(request, 'retours/edit.html', {'retour': retour})


def valider_retour(request,id):
    retour=Retour.objects.get(pk=id)
    return render(request, 'retours/valider.html', {'retour': retour})

def confirme_validation(request, id):
    retour = Retour.objects.get(pk=id)   
    if request.method == 'POST':
        #return HttpResponse(request'retour_list')
        if 'confirmation' in request.POST:
            # Mettre à jour la facture du retour avec le fichier uploadé
            facture = request.FILES.get('facture')
            if facture:
                retour.facture = facture
                retour.save()
                # Rediriger vers une page de confirmation ou une autre vue
                return redirect('retour_list')
            else:
                # Si aucun fichier n'a été téléchargé, gérer l'erreur
                # ou afficher un message à l'utilisateur
                pass
        else:
            # Si la case de confirmation n'est pas cochée, gérer l'erreur
            # ou afficher un message à l'utilisateur
            pass
    
    return redirect('retour_list')
#--------------------PDF---------------------
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.template.loader import get_template
from django.views.generic import TemplateView
from reportlab.pdfgen import canvas
from django.http import FileResponse
from .models import Avoir
class CompteRenduView(TemplateView):
    template_name = 'compte_rendu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = Avoir.objects.all()  # You might need to adjust this queryset
        context['results'] = results
        return context

def generate_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    results = Avoir.objects.filter(date_ajout__range=[start_date, end_date], is_avoir=False).values('famille__famille').annotate(nombre=Count('famille'))

    # Create a response object with appropriate PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="compte_rendu.pdf"'

    # Create a PDF object using reportlab
    pdf = canvas.Canvas(response)

    # Add content to the PDF
    pdf.drawString(100, 800, "Compte Rendu")

    y_position = 780  # Starting Y position for the table
    for result in results:
        pdf.drawString(100, y_position, f"Famille: {result['famille__famille']}, Nombre: {result['nombre']}")
        y_position -= 20  # Adjust as needed for spacing

    # Close the PDF object and return the response
    pdf.showPage()
    pdf.save()
    return response



from django.template.loader import get_template
from xhtml2pdf import pisa

def test(request):
    # Assuming you have a context with data for your invoice
    context = {
        'invoice_number': 'INV-123',
        'invoice_date': '2024-01-18',
        'customer_name': 'John Doe',
        'quantity_tv': 3,
        'price_tv': 500,  # Assuming the price per TV is $500
        # Add other context data here
    }

    template_path = 'bill_template.html'
    template = get_template(template_path)
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    # Generate PDF using ReportLab
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response



#------------Utilisateur-----------------------

#---------------------------------UTILISATEUR-------------------------------------------------------
def list_user(request):
        users = User.objects.filter(is_superuser=False).order_by('-id')
        return render(request, 'utilisateurs/liste_user.html', {'users': users})



def add_user(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = User.objects.create_user(username=username,password=password)
            messages.success(request, 'UTILISATEUR créé avec succes')

            # Redirect to a success page or login the user, etc.
            return redirect('list_user')

    else:
        form = CustomUserRegistrationForm()

    return render(request, 'utilisateurs/ajouter.html', {'form': form})



def profile(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            request.user.username = username
            request.user.set_password(password)  # Use set_password to securely update the password
            request.user.save()
            messages.success(request, "PROFILE ADMINISTRATEUR CHANGÉ AVEC SUCCÈS")
            return redirect('list_user')
    else:
        form = CustomUserRegistrationForm()  # Moved form instantiation inside the else block

    return render(request, 'utilisateurs/profile.html', {'form': form})


from django.contrib.auth import get_user_model
def profile_user(request, id):
    profile = User.objects.get(id=id)

    if request.method == 'POST':
        is_active=False
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            print("inside form validation")
            active=request.POST.get('is_active')
            print(active)
            if active=="on":
                is_active=True
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            profile.username = username
            profile.set_password(password)
            profile.is_active=is_active
            profile.save()
            messages.success(request, f"LE PROFILE DE {profile.username} CHANGÉ AVEC SUCCÈS")
            return redirect('list_user')
    else:
        form = CustomUserRegistrationForm()  # Pass profile as instance

    return render(request, 'utilisateurs/profile_user.html', {'form': form, 'profile': profile})




#------------COMPTE RENDU --------------------
@login_required
def saisie_vente(request):
    if request.method == 'POST':
        # Traiter les données de la première ligne de vente
        nom_client = request.POST.get('nom')
        prenom_client = request.POST.get('prenom')
        designation_produit = request.POST.get('designation_1')
        code_barre = request.POST.get('code_barre_1')
        prix_vente = Decimal(request.POST.get('prix_vente_1'))
        prix_achat = Decimal(request.POST.get('prix_achat_1'))
        vendeur = request.user
        Vente.objects.create(nom_client=nom_client, prenom_client=prenom_client, designation_produit=designation_produit,
                             code_barre=code_barre, prix_vente=prix_vente, prix_achat=prix_achat, vendeur=vendeur)

        # Traiter les données des lignes de vente supplémentaires
        ligne_count = 2  # Commencer à partir de la deuxième ligne
        while True:
            if request.POST.get(f'designation_{ligne_count}') and request.POST.get(f'code_barre_{ligne_count}') \
                    and request.POST.get(f'prix_vente_{ligne_count}') and request.POST.get(f'prix_achat_{ligne_count}'):
                # S'il y a des données pour la ligne suivante, les traiter
                designation_produit = request.POST.get(f'designation_{ligne_count}')
                code_barre = request.POST.get(f'code_barre_{ligne_count}')
                prix_vente = Decimal(request.POST.get(f'prix_vente_{ligne_count}'))
                prix_achat = Decimal(request.POST.get(f'prix_achat_{ligne_count}'))
                Vente.objects.create(nom_client=nom_client, prenom_client=prenom_client, designation_produit=designation_produit,
                                     code_barre=code_barre, prix_vente=prix_vente, prix_achat=prix_achat, vendeur=vendeur)
                ligne_count += 1  # Passer à la ligne suivante
            else:
                break  # Sortir de la boucle si aucune donnée n'est trouvée pour la ligne suivante

        return redirect('ventes_journee')

    return render(request, 'rendu/saisie_vente.html')

from django.db.models import Max
def ventes_journee(request):
   
    current_date = timezone.now().strftime('%d-%m-%Y')
    vendeur = request.user
    today = date.today()
    #dernier_jour_vente = JourneeVente.objects.filter(vendeur=vendeur, date__lt=today).aggregate(dernier_jour=Max('date'))['dernier_jour']
    dernier_jour_vente = JourneeVente.objects.filter(vendeur=vendeur, date__lt=today).order_by('-date').first()
    
    #dernier_jour_vente = JourneeVente.objects.filter(vendeur=vendeur, date__lt=today).aggregate(dernier_jour=Max('date'))['dernier_jour']
    print(f"dernier_jour_vente ={dernier_jour_vente}")
    if   dernier_jour_vente:
        if dernier_jour_vente.cloturee==False:
            print(f"journee_precedente_cloturee******** {dernier_jour_vente.date}")        # Rediriger l'utilisateur vers une page d'erreur ou afficher un message d'avertissement
            return render(request, 'rendu/erreur_journee_precedente_non_cloturee.html',{'dernier_jour_vente': dernier_jour_vente.date})  
    date_aujourdhui = timezone.now().date()
    vente_journee, created = JourneeVente.objects.get_or_create(
            date=date_aujourdhui,
            vendeur=request.user,
        )
    ventes = Vente.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    teletransitions = Teletransmition.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    stocks = Stock.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    savs = Sav.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    anomalies = Anomalie.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    remises_banque = RemiseBanque.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    livraisons = Livraison.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    litiges = Litige.objects.filter(vendeur=vendeur, date__date=timezone.now().date())
    total_ventes = Decimal(0)
    today_vente = JourneeVente.objects.filter(vendeur=vendeur, date=today).order_by('-date').first()

    for vente in ventes:
        total_ventes += vente.prix_vente
    context = {
    'current_date': current_date,
    'ventes': ventes,
    'total_ventes': total_ventes,
    'today_vente': today_vente,
    'teletransitions': teletransitions,
    'stocks': stocks,
    'savs': savs,
    'anomalies': anomalies,
    'remises_banque': remises_banque,
    'livraisons': livraisons,
    'litiges': litiges
}

    #print (f"les ventes : {ventes}")
    return render(request, 'rendu/ventes_journee.html', context)


@login_required
def cloturer_journee(request):
    print(f"cloture journé pour ce vendeur  {request.user} ")
    if request.method == 'POST':
        day_str = request.POST.get('day')
        day_date = datetime.strptime(day_str, '%d-%m-%Y').date()
        vendeur = request.user
        journee = JourneeVente.objects.get(vendeur=vendeur, cloturee=False,date=day_date)
        journee.cloturee = True
        journee.ca_jour=request.POST.get('ca_jour')
        journee.ca_jour_1=request.POST.get('ca_jour_1')
        journee.ca_mois=request.POST.get('ca_mois')
        journee.ca_mois_1=request.POST.get('ca_mois_1')
        journee.save()
        return redirect('ventes_journee')
    return render(request, 'rendu/cloturer_journee.html')


def valider_cloture(request):
    day = request.GET.get('day')
    print(day)
    date_filter = datetime.strptime(day, "%d-%m-%Y")
    ventes = Vente.objects.filter(vendeur=request.user, date__date=date_filter)
    print(ventes)
    total_ventes = Decimal(0)
    #today_vente = JourneeVente.objects.filter(vendeur=request.user, date=day).order_by('-date').first()

    for vente in ventes:
        total_ventes += vente.prix_vente
    print(total_ventes)
    return render(request, 'rendu/valider_cloture.html',{'day':day,'ca_jour':total_ventes})

def open_day(request):
    day = request.GET.get('day')
    date_filter = datetime.strptime(day, "%d-%m-%Y")
    try:
        journee = JourneeVente.objects.get(vendeur=request.user, date__date=date_filter)
        journee.cloturee = False
        journee.save()
        print(f"++++++++++++++++{journee}")
    except JourneeVente.DoesNotExist:
        # Gérer le cas où aucune journée n'est trouvée
        pass

    return redirect('ventes_journee')



@login_required
def edit_rendu(request,id):
    vente=Vente.objects.get(pk=id)
    print(vente)

    if request.method == 'POST':

        vente.nom_client = request.POST.get('nom')
        vente.prenom_client = request.POST.get('prenom')
        vente.designation_produit = request.POST.get('designation')
        vente.code_barre = request.POST.get('code_barre')
        vente.prix_vente = Decimal(request.POST.get('prix_vente'))
        vente.prix_achat = Decimal(request.POST.get('prix_achat'))
        vente.save()


            
        return redirect('ventes_journee')

    return render(request, 'rendu/edit_vente.html',{"vente":vente})

from django.contrib import messages

def add_item(request, model_name):
    if request.method == 'POST':
        if model_name == 'teletransmition':
            # Créer une instance de Teletransmition
            Teletransmition.objects.create(
                vendeur=request.user,
                amo=request.POST['amo'],
                amc=request.POST['amc']
            )
            # Ajouter un message de succès
            messages.success(request, "NOUVELLE TÉLÉTRANSMISSION AJOUTÉE AVEC SUCCÈS!")
        elif model_name == 'stock':
            # Créer une instance de Stock
            Stock.objects.create(
                vendeur=request.user,
                marque=request.POST['marque'],
                qtt=request.POST['qtt']
            )
            # Ajouter un message de succès
            messages.success(request, "NOUVEAU STOCK AJOUTÉ AVEC SUCCÈS!")
        elif model_name == 'sav':
            # Créer une instance de Sav
            Sav.objects.create(
                vendeur=request.user,
                nom=request.POST['nom'],
                prenom=request.POST['prenom'],
                fournisseur=request.POST['fournisseur'],
                reference=request.POST['reference']
            )
            # Ajouter un message de succès
            messages.success(request, "NOUVEAU SAV AJOUTÉ AVEC SUCCÈS!")
        elif model_name == 'anomalie':
            # Créer une instance de Anomalie
            Anomalie.objects.create(
                vendeur=request.user,
                subject=request.POST['subject']
            )
            # Ajouter un message de succès
            messages.success(request, "NOUVELLE ANOMALIE AJOUTÉE AVEC SUCCÈS!")
        elif model_name == 'remisebanque':
            # Créer une instance de RemiseBanque
            RemiseBanque.objects.create(
                vendeur=request.user,
                montant=request.POST['montant'],
                piece=request.FILES['piece']
            )
            # Ajouter un message de succès
            messages.success(request, "NOUVELLE REMISE BANCAIRE AJOUTÉE AVEC SUCCÈS!")
        elif model_name == 'livraison':
            # Créer une instance de Livraison
            Livraison.objects.create(
                vendeur=request.user,
                nom=request.POST['nom'],
                prenom=request.POST['prenom']
            )
            # Ajouter un message de succès
            messages.success(request, "NOUVELLE LIVRAISON AJOUTÉE AVEC SUCCÈS!")
        elif model_name == 'litige':
            # Créer une instance de Litige
            Litige.objects.create(
                vendeur=request.user,
                subject=request.POST['subject']
            )
            # Ajouter un message de succès
            messages.success(request, "NOUVEAU LITIGE AJOUTÉ AVEC SUCCÈS!")

        # Rediriger l'utilisateur vers une page de confirmation ou une autre vue
        return redirect('ventes_journee')  # Remplacez 'nom_de_la_vue_de_confirmation' par le nom de votre vue de confirmation
    else:
        return render(request, 'rendu/add_item.html', {'model_name': model_name})



    

def edit_item(request, model_name, item_id):
    # Récupérer l'objet correspondant à l'identifiant
    if model_name == 'teletransmition':
        item = get_object_or_404(Teletransmition, pk=item_id)
    elif model_name == 'stock':
        item = get_object_or_404(Stock, pk=item_id)
    elif model_name == 'sav':
        item = get_object_or_404(Sav, pk=item_id)
    elif model_name == 'anomalie':
        item = get_object_or_404(Anomalie, pk=item_id)
    elif model_name == 'remisebanque':
        item = get_object_or_404(RemiseBanque, pk=item_id)
    elif model_name == 'livraison':
        item = get_object_or_404(Livraison, pk=item_id)
    elif model_name == 'litige':
        item = get_object_or_404(Litige, pk=item_id)
    else:
        # Gérer le cas où le modèle n'est pas trouvé
        return HttpResponseNotFound("Model not found")

    if request.method == 'POST':
        if model_name == 'teletransmition':
            # Mettre à jour l'instance de Teletransmition
            item.amo = request.POST['amo']
            item.amc = request.POST['amc']
            item.save()
            messages.success(request, "TÉLÉTRANSMISSION MODIFIÉE AVEC SUCCÈS!")
        elif model_name == 'stock':
            # Mettre à jour l'instance de Stock
            item.marque = request.POST['marque']
            item.qtt = request.POST['qtt']
            item.save()
            messages.success(request, "STOCK MODIFIÉ AVEC SUCCÈS!")
        elif model_name == 'sav':
            # Mettre à jour l'instance de Sav
            item.nom = request.POST['nom']
            item.prenom = request.POST['prenom']
            item.fournisseur = request.POST['fournisseur']
            item.reference = request.POST['reference']
            item.save()
            messages.success(request, "SAV MODIFIÉ AVEC SUCCÈS!")
        elif model_name == 'anomalie':
            # Mettre à jour l'instance de Anomalie
            item.subject = request.POST['subject']
            item.save()
            messages.success(request, "ANOMALIE MODIFIÉE AVEC SUCCÈS!")
        elif model_name == 'remisebanque':
            # Mettre à jour l'instance de RemiseBanque
            item.montant = request.POST['montant']
            if 'piece' in request.FILES:
                item.piece = request.FILES['piece']
            item.save()
            messages.success(request, "REMISE BANCAIRE MODIFIÉE AVEC SUCCÈS!")
        elif model_name == 'livraison':
            # Mettre à jour l'instance de Livraison
            item.nom = request.POST['nom']
            item.prenom = request.POST['prenom']
            item.save()
            messages.success(request, "LIVRAISON MODIFIÉE AVEC SUCCÈS!")
        elif model_name == 'litige':
            # Mettre à jour l'instance de Litige
            item.subject = request.POST['subject']
            item.save()
            messages.success(request, "LITIGE MODIFIÉ AVEC SUCCÈS!")

        return redirect('ventes_journee')

    else:
        # Afficher le formulaire d'édition avec les données existantes
        context = {
            'item': item,
            'model_name': model_name,
        }
        return render(request, 'rendu/edit_item.html', context)
    

from django.db.models import Sum
from django.db.models.functions import TruncDate



def calculate_statistics(model, seller, start_date, end_date):
    if seller:
        searching_seller = User.objects.get(pk=seller)
        data = model.objects.filter(vendeur=searching_seller, date__date__range=(start_date, end_date))
    else:
        data = model.objects.filter(date__date__range=(start_date, end_date))
    
    statistics = data.annotate(date=TruncDate('date')).values('date').annotate(total_sales=Sum('prix_vente'))
    return statistics

def vente_statistique(request):
    ventes = Vente.objects.all()
    sellers=User.objects.all()
    searching_seller=""

    if request.method == 'POST':
        # Récupérer les paramètres du formulaire
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        seller = request.POST.get('seller')
        stat_type = request.POST.get('stat_type')
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
        ventes_par_jour = []
        if stat_type in ["Vente", "Teletransmition","Stock","Sav","Anomalie","RemiseBanque","Livraison","Litige"]:
            current_date = start_date
            while current_date <= end_date:
                if seller:
                    searching_seller=User.objects.get(pk=seller)
                    ventes_pour_ce_jour = stat_type.objects.filter(vendeur=seller,date__date=current_date)
                else :
                    ventes_pour_ce_jour = stat_type.objects.filter(date__date=current_date)
                print(ventes_pour_ce_jour)

                ventes_de_ce_jour = []
                total=0
                for vente in ventes_pour_ce_jour:
                    total=total+vente.prix_vente
                    vente_dict = {
                        'id': vente.id,
                        'nom':vente.nom_client,
                        'prenom':vente.prenom_client,
                        'achat':vente.prix_achat,
                        'vente':vente.prix_vente,
                        'vendeur': vente.vendeur,
                        # Ajoutez d'autres attributs de vente selon vos besoins
                    }
                    ventes_de_ce_jour.append(vente_dict)
                ventes_par_jour.append({'date': current_date,'total':total, 'ventes': ventes_de_ce_jour})
                current_date += timedelta(days=1)
        #print(ventes_par_jour)
        return render(request, 'rendu/statistique.html', {'sellers': sellers,
                        'searching_seller':searching_seller,
                        'ventes_par_jour': ventes_par_jour,
                        'start_date':request.POST.get('start_date'),
                        'end_date':request.POST.get('end_date')})
    return render(request, 'rendu/statistique.html')

#----------STATI-------------------------------
@login_required
def get_statistics(request):
    model_dict = {
                "Vente": Vente,
                "Teletransmition": Teletransmition,
                "Stock": Stock,
                "Sav": Sav,
                "Anomalie": Anomalie,
                "RemiseBanque": RemiseBanque,
                "Livraison": Livraison,
                "Litige": Litige,
            }
  
    journees_vente = JourneeVente.objects.all().order_by('-date')
    #journees_vente = JourneeVente.objects.all()
    ventes_par_mois_facture= defaultdict(list)
    for journee in journees_vente:
        year = journee.date.year
        month = journee.date.month
        ventes_par_mois_facture[(year, month)].append(journee)
    sellers=User.objects.all()

    searching_seller=""
    onglet=0
    if request.method == "POST" and request.POST.get('jour') :
        selected_date = request.POST.get('selected_date')
        sellers = User.objects.all()
        statistics_by_seller = {}
        total_all_sellers = 0  # Initialize total sales for all sellers
        total_all_ventes=0
        total_all_teletransmitions_amo=0
        total_all_teletransmitions_amc=0
        total_all_stock=0
        total_all_sav=0
        total_all_banque=0
        total_all_anomalie=0
        total_all_livraison=0
        total_all_litige=0
        division_result = 0
        for seller in sellers:
            seller_id = seller.id
            total_sales = get_total_sales(selected_date, seller_id)
            total_all_sellers += total_sales  # Add seller's sales to total for all sellers
            #total_ventes=get_total_ventes(selected_date, seller.id)
            total_all_ventes +=get_total_ventes(selected_date, seller.id)
            total_teletransmitions_amo, total_teletransmitions_amc = get_total_teletransmitions(selected_date, seller.id)
            total_all_teletransmitions_amo += total_teletransmitions_amo
            total_all_teletransmitions_amc += total_teletransmitions_amc
            total_all_stock +=get_total_insertions_stock(selected_date, seller.id)
            total_all_sav +=get_total_sav(selected_date, seller.id)
            total_all_banque +=get_total_remises_banque(selected_date, seller.id)
            total_all_anomalie +=get_total_anomalies(selected_date, seller.id)
            total_all_livraison +=get_total_livraisons(selected_date, seller.id)
            total_all_litige +=get_total_litiges(selected_date, seller.id)
            statistics_by_seller[seller.id] = {
                'vendeur': seller,
                'total_sales': get_total_sales(selected_date, seller.id),
                'total_ventes': get_total_ventes(selected_date, seller.id),
                'total_teletransmitions': get_total_teletransmitions(selected_date, seller.id),
                'total_insertions_stock': get_total_insertions_stock(selected_date, seller.id),
                'total_sav': get_total_sav(selected_date, seller.id),
                'total_anomalies': get_total_anomalies(selected_date, seller.id),
                'total_remises_banque': get_total_remises_banque(selected_date, seller.id),
                'total_livraisons': get_total_livraisons(selected_date, seller.id),
                'total_litiges': get_total_litiges(selected_date, seller.id),
                'average_cart': get_average_cart(selected_date, seller.id),
               
            }
        if total_all_ventes != 0:
            division_result = total_all_sellers / total_all_ventes
        print(f"day {selected_date}")
        onglet=1
        return render(request, 'rendu/statistique.html',
                       {'statistics_by_seller': statistics_by_seller,
                         'selected_date':selected_date ,
                         "onglet":onglet,'sellers':sellers,
                         'total_all_sellers': total_all_sellers,
                         'total_all_ventes':total_all_ventes,
                         'total_all_teletransmitions_amo':total_all_teletransmitions_amo,
                         'total_all_teletransmitions_amc':total_all_teletransmitions_amc,
                         'total_all_stock' : total_all_stock,
                         'total_all_sav':total_all_sav,
                         'total_all_anomalie':total_all_anomalie,
                         'total_all_livraison':total_all_livraison,
                         'total_all_litige':total_all_litige,
                         'total_all_banque':total_all_banque,
                         'model_dict':model_dict,


                         'division_result':division_result
                         ,'ventes_par_mois_facture':ventes_par_mois_facture})
    
    if request.method == "POST" and request.POST.get('periode') :
        # Récupérer les paramètres du formulaire
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        seller = request.POST.get('seller')
        stat_type = request.POST.get('stat_type')
        start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
        ventes_par_jour = []

        if stat_type in model_dict:
            current_date = start_date
            model = model_dict[stat_type]
            total_periode=0
            amo_periode=0
            amc_periode=0
            montant_periode=0
            qtt_periode=0
            nombre_periode=0
            
            while current_date <= end_date:
                if seller:
                    searching_seller=User.objects.get(pk=seller)
                    ventes_pour_ce_jour = model.objects.filter(vendeur=seller,date__date=current_date)
                else :
                    ventes_pour_ce_jour = model.objects.filter(date__date=current_date)
                print(ventes_pour_ce_jour)

                ventes_de_ce_jour = []     
                total=0
                amo=0
                amc=0
                montant=0
                qtt=0
                vente_dict={}
                for vente in ventes_pour_ce_jour:
                    if stat_type=="Vente":
                        total=total+vente.prix_vente
                        total_periode=total_periode+vente.prix_vente
                    if stat_type=="Teletransmition":
                        amo=amo+vente.amo
                        amc=amc+vente.amc
                        amo_periode=amo_periode+vente.amo
                        amc_periode=amc_periode+vente.amc
                    if stat_type=="RemiseBanque":
                        montant=montant+vente.montant
                        montant_periode=montant_periode+vente.montant
                    if stat_type=="Stock":
                        qtt=qtt+vente.qtt
                        qtt_periode=qtt_periode+vente.qtt
                    if stat_type=="Litige":
                        nombre_periode += 1
                    if stat_type=="Livraison":
                       nombre_periode += 1
                    if stat_type=="Anomalie":
                        nombre_periode += 1
                    if stat_type=="Sav":
                        nombre_periode += 1
                    vente_dict = vars(vente)
                    vente_dict['vendeur_username'] = vente.vendeur  # Convert vente object to dictionary      
                    ventes_de_ce_jour.append(vente_dict)
                #vente_dict['total']=total
                ventes_par_jour.append({'date': current_date,'total':total,
                                        'amo':amo,
                                        'amc':amc,
                                        'montant':montant,
                                        'qtt':qtt,
                                         'ventes': ventes_de_ce_jour})
                current_date += timedelta(days=1)
        
        onglet=2
        print(f"total periode :  {total_periode}")
        return render(request, 'rendu/statistique.html', {'sellers': sellers,
                        'searching_seller':searching_seller,
                        'ventes_par_jour': ventes_par_jour,
                        'start_date':request.POST.get('start_date'),
                        'end_date':request.POST.get('end_date'),
                        'onglet':onglet,
                        'stat_type':stat_type,
                        'total_periode':total_periode,
                         'amo_periode':amo_periode,
                          'amc_periode':amc_periode,
                          'montant_periode':montant_periode,
                          'qtt_periode':qtt_periode,
                          'nombre_periode':nombre_periode,
                          'model_dict':model_dict,
                          'ventes_par_mois_facture':ventes_par_mois_facture
                        })  
    else :   
        onglet = request.GET.get('onglet')
        if onglet=="100" and request.GET.get('date_facture') :   
            month, year = map(int, request.GET.get('date_facture').split('-'))
            vente_objects = Vente.objects.filter(date__month=month, date__year=year)
            chiffre_mois_result = vente_objects.aggregate(total_prix_vente=Sum('prix_vente'))
            chiffre_mois = chiffre_mois_result.get('total_prix_vente', 0)
            teletransmition_objects = Teletransmition.objects.filter(date__month=month, date__year=year)
            amo_mois_result = teletransmition_objects.aggregate(total_amo=Sum('amo'))
            amc_mois_result = teletransmition_objects.aggregate(total_amc=Sum('amc'))
            amo_mois = amo_mois_result.get('total_amo', 0)
            amc_mois = amc_mois_result.get('total_amc', 0)
            stock_objects = Stock.objects.filter(date__month=month, date__year=year)
            total_qtt_result = stock_objects.aggregate(total_qtt=Sum('qtt'))
            qtt_mois = total_qtt_result.get('total_qtt', 0)
            sav_objects = Sav.objects.filter(date__month=month, date__year=year)
            anomalie_objects = Anomalie.objects.filter(date__month=month, date__year=year)
            livraison_objects = Livraison.objects.filter(date__month=month, date__year=year)
            litige_objects = Litige.objects.filter(date__month=month, date__year=year)
            # Count the number of objects for each queryset
            sav_count = sav_objects.count()
            anomalie_count = anomalie_objects.count()
            livraison_count = livraison_objects.count()
            litige_count = litige_objects.count()
            remise_banque_objects = RemiseBanque.objects.filter(date__month=month, date__year=year)
            # Calculate the sum of montant
            total_montant_result = remise_banque_objects.aggregate(total_montant=Sum('montant'))
            # Retrieve the aggregated value
            remise_mois= total_montant_result.get('total_montant', 0)
            context = {
            'vente_objects': vente_objects,
            'chiffre_mois':chiffre_mois,
            'teletransmition_objects': teletransmition_objects,
            'amo_mois':amo_mois,
            'amc_mois':amc_mois,
            'stock_objects': stock_objects,
            'qtt_mois':qtt_mois,
            'sav_objects': sav_objects,
            'anomalie_objects': anomalie_objects,
            'remise_banque_objects': remise_banque_objects,
            'livraison_objects': livraison_objects,
            'litige_objects': litige_objects,
            'sav_count':sav_count,
            'livraison_count':livraison_count,
            'litige_count':litige_count,
            'remise_mois':remise_mois,
            'anomalie_count':anomalie_count,
            'model_dict':model_dict,
            'year':year,
            'month':month}                                
            if request.GET.get('model'):
                model = model_dict[request.GET.get('model')]
                data = model.objects.filter(date__month=month, date__year=year)
                context.update({
                    'data': data,
                    'model': request.GET.get('model')
                })
                html_string = render_to_string('rendu/pdf_model.html', context)       
                filename = f"RAPPORT_{request.GET.get('model')}_{month}_{year}.pdf"

            else:
                html_string = render_to_string('rendu/pdf.html', context)
                filename = f"RAPPORT_{month}_{year}.pdf"
            pdf = HTML(string=html_string).write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        

            
        
    return render(request, 'rendu/statistique.html',{'sellers':sellers,'ventes_par_mois_facture':ventes_par_mois_facture,'onglet':3,'model_dict':model_dict})
    











        

# Fonctions pour récupérer les statistiques
# Fonctions pour récupérer les statistiques pour chaque modèle par vendeur
def get_total_sales(selected_date, seller_id=None):
    sales_data = Vente.objects.filter(vendeur_id=seller_id, date__date=selected_date)
    total_sales = sales_data.aggregate(total_sales=Sum('prix_vente')).get('total_sales') or 0
    return total_sales

def total_sales_all_sellers(selected_date):
    total_sales = Vente.objects.filter(date__date=selected_date).aggregate(total_sales=Sum('prix_vente')).get('total_sales') or 0
    return total_sales

def get_total_remises_banque(selected_date, seller_id=None):
    remises_banque_data = RemiseBanque.objects.filter(vendeur_id=seller_id, date__date=selected_date)
    return remises_banque_data.aggregate(total_remises=Sum('montant')).get('total_remises') or 0



def get_total_ventes(selected_date, seller_id=None):
    ventes_data = Vente.objects.filter(vendeur_id=seller_id,date__date=selected_date)
    return ventes_data.count()

def get_total_teletransmitions(selected_date, seller_id=None):
    teletransmitions_data = Teletransmition.objects.filter(vendeur_id=seller_id, date__date=selected_date)
    total_amo = teletransmitions_data.aggregate(total_amo=Sum('amo'))['total_amo'] or 0
    total_amc = teletransmitions_data.aggregate(total_amc=Sum('amc'))['total_amc'] or 0
    return total_amo, total_amc

def get_total_insertions_stock(selected_date, seller_id=None):
    total_quantity = Stock.objects.filter(vendeur_id=seller_id, date__date=selected_date).aggregate(total_quantity=Sum('qtt'))
    total_quantity_value = total_quantity['total_quantity']
    if total_quantity_value is not None:
        total_quantity_value = int(total_quantity_value)
    else:
        total_quantity_value = 0
    print(f'total_quantity_value {total_quantity_value}')
    return total_quantity_value


def get_total_sav(selected_date, seller_id=None):
    sav_data = Sav.objects.filter(vendeur_id=seller_id,date__date=selected_date)
    return sav_data.count()

def get_total_anomalies(selected_date, seller_id=None):
    anomalies_data = Anomalie.objects.filter(vendeur_id=seller_id,date__date=selected_date)
    return anomalies_data.count()


def get_total_livraisons(selected_date, seller_id=None):
    livraisons_data = Livraison.objects.filter(vendeur_id=seller_id,date__date=selected_date)
    return livraisons_data.count()

def get_total_litiges(selected_date, seller_id=None):
    litiges_data = Litige.objects.filter(vendeur_id=seller_id,date__date=selected_date)
    return litiges_data.count()


def get_average_cart(selected_date, seller_id=None):
    total_sales = get_total_sales(selected_date, seller_id)
    total_ventes = get_total_ventes(selected_date, seller_id)
    if total_ventes != 0:
        average_cart = total_sales / total_ventes
    else:
        average_cart = 0
    return average_cart

#----------DUMMY DATA--------------------
from faker import Faker
import random

def fill_dummy_data(request):
    fake = Faker()

    vendeur = request.user  # Récupérer le vendeur à partir de la requête

    # Remplir 10 ventes
    for _ in range(10):
        nom_client = fake.first_name()
        prenom_client = fake.last_name()
        designation_produit = fake.word()
        code_barre = fake.ean13()
        prix_vente = random.uniform(10, 1000)
        prix_achat = prix_vente * random.uniform(0.5, 0.8)
        vente = Vente.objects.create(vendeur=vendeur, nom_client=nom_client, prenom_client=prenom_client,
                                     designation_produit=designation_produit, code_barre=code_barre,
                                     prix_vente=prix_vente, prix_achat=prix_achat)

    # Remplir 5 exemples de données factices pour les autres modèles
    for _ in range(5):
        # Remplir Teletransmition
        amo = random.uniform(100, 1000)
        amc = amo * random.uniform(0.5, 0.8)
        Teletransmition.objects.create(vendeur=vendeur, amo=amo, amc=amc)

        # Remplir Stock
        Stock.objects.create(vendeur=vendeur, marque=fake.company(), qtt=random.randint(1, 100))

        # Remplir Sav
        Sav.objects.create(vendeur=vendeur, nom=fake.first_name(), prenom=fake.last_name(),
                           fournisseur=fake.company(), reference=fake.ean13())

        # Remplir Anomalie
        Anomalie.objects.create(vendeur=vendeur, subject=fake.sentence())

       

        # Remplir Livraison
        Livraison.objects.create(vendeur=vendeur, nom=fake.first_name(), prenom=fake.last_name())

        # Remplir Litige
        Litige.objects.create(vendeur=vendeur, subject=fake.sentence())
    return redirect('ventes_journee')
    #return render(request, 'dummy_data_filled.html')  # Remplacer 'dummy_data_filled.html' par le nom de votre template de confirmation