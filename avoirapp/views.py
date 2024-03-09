from django.shortcuts import get_object_or_404, redirect, render,HttpResponse
from django.db.models import Sum
from django.http import HttpResponseBadRequest, JsonResponse
from avoirapp.forms import AvoirForm,ConsommationForm,FamilleForm
from django.http import JsonResponse
from .models import Avoir, Client, Famille,Consommation, Invoice, Repertoire, Retour
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
import json
from django.contrib import messages
from django.utils import formats
# myapp/views.py

from django.contrib.auth import authenticate, login,logout
from .forms import ClientForm, CustomLoginForm, RepertoireSearchForm
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
    items_per_page = 8
    paginator = Paginator(clients, items_per_page)
         # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the Page object for the requested page
        clients = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        clients = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, show the last page
        clients = paginator.page(paginator.num_pages)

    return render(request, 'clients/client.html', {'clients': clients})
    #return render(request, 'client.html')


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

from datetime import datetime, timedelta
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


    return HttpResponse("kkkkkkkk")


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
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')

        # Convert dates to ISO format
        start_date_iso = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_iso = datetime.strptime(end_date, '%Y-%m-%d').date()

        if type == 'consommation':
            # Query consommations and select related client
            consommations = Consommation.objects.filter(
                date_ajout__range=[start_date_iso, end_date_iso]
            ).select_related('client')
            if selected_families:
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
                date_ajout__range=[start_date_iso, end_date_iso]
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
    # Rendre le modèle HTML avec les données de consommation
    html_string = render_to_string('pdf/template_consoomation_par_famille.html', {'consommations': consommations,'title':title})
    
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
        title=f"{famille}_{mois}_{annee}"

        pdf_data = generate_pdf_consommation(consommations,title)

        filename = f"CONSOMMATIONS_{famille}_{mois}_{annee}.pdf"

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
            avoir.save()
            messages.success(request, f'UNE CREDIT DE {avoir.montant} A BIEN ÉTÉ CRÉÉE')
            return redirect('client_details', client_id=client.id)
    else:
        form = AvoirForm()

    return render(request, 'avoirs/ajouter_avoir.html', {'client': client, 'form': form})




def consommer_avoir(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    print(client)

    if request.method == 'POST':
        form = ConsommationForm(request.POST, request.FILES)
        if form.is_valid():
            prix_achat = form.cleaned_data['prix_achat']
            prix_vente = form.cleaned_data['prix_vente']
            designation=form.cleaned_data['designation']
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
                    code_barre=form.cleaned_data['code_barre'],
                    famille=famille_instance
                )
                if facture:
                    consommation.facture = facture
                    consommation.save()
                messages.success(request, f'UNE CONSOMATION DE {prix_vente} A BIEN ÉTÉ CRÉÉE')

                return redirect('client_details', client_id=client.id)
            else:

                form.add_error('', f"VOUS NE POUVEZ PAS CONSOMMER PLUS QUE LE SOLDE CLIENT, QUI EST DE {total_avoir:.2f} DH.")
        else:
             return render(request, 'avoirs/consommer_avoir.html', {'form': form, 'client': client})

    else:
        #form = AvoirConsumeForm()
        form = ConsommationForm(initial={'code_barre': ''})
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
        messages.success(request, 'FAMILLE A BIEN ÉTÉ CRÉÉE')
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


            messages.success(request, 'FAMILLE A BIEN ÉTÉ MODIFIÉE')

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
            form.save()
            messages.success(request, f"VOUS AVEZ CREER LE CLIENT {form.cleaned_data['nom'].upper()} {form.cleaned_data['prenom'].upper()} AVEC SUCCÈS")

            return redirect('client')  # Replace 'client_list' with the URL name of the client list view
    else:
        #form = ClientForm()
        form = ClientForm(initial={'nom': '','prenom': '','datenaissance':''})

    return render(request, 'clients/add_client.html', {'form': form})

def edit_client(request,id):
    client = Client.objects.get(pk=id)
    if request.method == 'POST':
        form = ClientForm(request.POST,instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'VOUS AVEZ MODIFIÉ LE FICHIER DE {client.nom.upper()} {client.prenom.upper()} AVEC SUCCÈS')
            return redirect('client')  # Replace 'client_list' with the URL name of the client list view
    else:

        form = ClientForm(instance=client)

    return render(request, 'clients/edit_client.html', {'form': form})


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
    repertoires = Repertoire.objects.filter(is_active=True)
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

    
    repertoires = Repertoire.objects.filter(is_active=False)
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
        messages.success(request, f'Le répertoire "{nom}" a été modiféé avec succès.')
        
        return redirect('repertoire_list')  # Rediriger vers la liste des répertoires après la mise à jour
    return render(request, 'rep/add.html')


#--------------------Gestion Retour----------------------------

from django.utils import timezone

def retour_list(request):
    retours = Retour.objects.filter(facture='')
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
    retours = Retour.objects.exclude(facture='')
    search_query=""
    # Filtrer les enregistrements en fonction de la recherche de nom
    if request.method == 'GET' and request.GET.get('search'):
        search_query = request.GET.get('search')
        print(search_query)
        retours = retours.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
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
        code = request.POST.get('code')
        facture = request.FILES.get('facture')  # Utilisez FILES pour récupérer le fichier de la facture
        
        # Créer un nouvel objet Retour
        retour = Retour.objects.create(
            nom=nom,
            prenom=prenom,
            fournisseur=fournisseur,
            designation=designation,
            code=code,
            facture=facture  # Assignez le fichier de la facture
        )
        
        # Enregistrer les modifications dans la base de données
        retour.save()
        messages.success(request, 'Le retour a été ajouté avec succès.')
        
        return redirect('retour_list')  # Rediriger vers la liste des retours après l'ajout
    return render(request, 'retours/add.html')




def edit_retour(request, id):
    retour = Retour.objects.get(pk=id)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire depuis la requête POST
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        fournisseur = request.POST.get('fournisseur')
        designation = request.POST.get('designation')
        code = request.POST.get('code')
        facture = request.FILES.get('facture')  # Utilisez FILES pour récupérer le fichier de la facture
        
        # Mettre à jour les champs du retour avec les nouvelles valeurs
        retour.nom = nom
        retour.prenom = prenom
        retour.fournisseur = fournisseur
        retour.designation = designation
        retour.code = code
        if facture:  # Vérifiez si un nouveau fichier de facture a été fourni
            retour.facture = facture
        
        # Enregistrer les modifications dans la base de données
        retour.save()
        messages.success(request, f'Le retour "{nom}" a été modifié avec succès.')
        return redirect('retour_list')  # Rediriger vers la liste des retours après la mise à jour
    
    return render(request, 'retours/edit.html', {'retour': retour})


def valider_retour(request,id):
    retour=Retour.objects.get(pk=id)
    return render(request, 'retours/valider.html', {'retour': retour})

def confirme_validation(request, id):
    retour = Retour.objects.get(pk=id)   
    if request.method == 'POST':
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