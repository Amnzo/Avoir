from django.shortcuts import get_object_or_404, redirect, render,HttpResponse
from django.db.models import Sum
from django.http import HttpResponseBadRequest, JsonResponse
from avoirapp.forms import AvoirForm,ConsommationForm,FamilleForm
from django.http import JsonResponse
from .models import Avoir, Client, Famille,Consommation
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
import json
from django.contrib import messages
# myapp/views.py

from django.contrib.auth import authenticate, login,logout
from .forms import ClientForm, CustomLoginForm

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
                return redirect('client')  # Change 'home' to your actual home page URL
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
    return render(request, 'clients/client.html', {'clients': clients})
    #return render(request, 'client.html')


@login_required(login_url='login')


def statistique(request):
  # Fetching data from the database
    families = Famille.objects.all()
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
@login_required(login_url='login')
def avoir(request):
    #return render(request, 'avoir.html')
 # Query all Avoir instances where is_avoir is True
    #avoirs = Avoir.objects.all()
    avoirs = Avoir.objects.all().order_by('-date_ajout')


    # Pass the queryset to the template
    return render(request, 'avoirs/avoir_list.html', {'avoirs': avoirs})

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
        famille_name = request.POST.get('famille')
        facture=request.POST.get('is_facture')
        active=request.POST.get('is_active')
        if facture=="on":
                is_facture=True
        if active=="on":
                is_active=True
        
        Famille.objects.create(famille=famille_name,is_facture=is_facture,is_active=is_active)
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
    

def fetch_is_facture(request):
    famille_id = request.GET.get('famille_id')
    try:
        famille = Famille.objects.get(pk=famille_id)
        is_facture = famille.is_facture
        return JsonResponse({'is_facture': is_facture})
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
            return redirect('client')  # Replace 'client_list' with the URL name of the client list view
    else:
        #form = ClientForm()
        form = ClientForm(initial={'nom': '','prenom': '','datenaissance':''})

    return render(request, 'clients/add_client.html', {'form': form})


from django.db.models import Count
def compte_rendu(request):
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')

        results = Avoir.objects.filter(date_ajout__range=[start_date, end_date], is_avoir=False).values('famille__famille').annotate(nombre=Count('famille'))
        results_list = list(results)

        return render(request, 'compte_rendu.html', {'results': results_list})

    return render(request, 'compte_rendu.html')



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