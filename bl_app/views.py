
from django.shortcuts import render,HttpResponse

from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib import messages
from avoirapp.models import Client, Famille
from .forms import CustomLoginForm
from .models import Bon_Commande, Produit
from django.views.decorators.csrf import csrf_exempt
# myapp/views.py
from django.contrib.auth import authenticate, login,logout
# Create your views here.

def bl_custom_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page or home page
                return redirect('index')  # Change 'home' to your actual home page URL
            else:
                # Handle invalid login
                form.add_error(None, 'Invalid login credentials')
    else:
        form = CustomLoginForm()

    return render(request, 'login_bl.html', {'form': form,'hide_menu': True})

def bl_custom_logout(request):
    logout(request)
    # Add any additional logic or redirect as needed
    return redirect('bl_login')

@login_required(login_url='bl_login')
def index(request):
    if request.method == 'POST':
        form_data = request.POST.dict()
        #form_data = request.POST.dict()
        #client_name = form_data.get('client')
        
        #client = Client.objects.get(nom=client_name)
        client = Client.objects.get(pk=form_data.get('client'))
        categorie_d= Famille.objects.get(pk=form_data.get('categorie_d'))
        produit_d = Produit.objects.get(pk=form_data.get('produit_d'))
        categorie_g= Famille.objects.get(pk=form_data.get('categorie_g'))
        produit_g = Produit.objects.get(pk=form_data.get('produit_g'))
        bon_commande = Bon_Commande(client=client,
                        categorie_d=categorie_d,categorie_g=categorie_g,
                        produit_d=produit_d,produit_g =produit_g,
                        sphere_d=form_data.get('sphere_d'),sphere_g=form_data.get('sphere_g'),
                        cylindre_d=form_data.get('cylindre_d'),cylindre_g=form_data.get('cylindre_g'),
                        axe_d=form_data.get('axe_d'),axe_g=form_data.get('axe_g'),
                        quatite_d=form_data.get('quatite_d'),quatite_g=form_data.get('quatite_g'),
                        user=request.user,

                          
                          
                           )
        bon_commande.save()
        messages.success(request, 'Bon de Commande créé avec succes')
        return redirect('bl_list')
    else:
    
        #sphere_range = [round(x, 2) for x in range(-600/100, 601/100, 5/100)]
        step = 0.5
        sphere_range  = [round(x, 2) for x in [-6 + i * 0.5 for i in range(25)]]
        # Generate the range of values from -3 to +3 with a step of 0.5
        cylindre_range = [round(x, 2) for x in [-3 + i * 0.5 for i in range(13)]]

        # Generate the range of values from 0 to 180 with a step of 5
        axe_range = [round(x, 2) for x in range(0, 181, 5)]
        quantite_range = [round(x, 2) for x in range(1, 21, 1)]
        categories = Famille.objects.all()
        products = Produit.objects.all()
        clients=Client.objects.all()
        context = {

            'sphere_range': sphere_range,
            'cylindre_range':cylindre_range,
            'axe_range': axe_range,
            'quantite_range':quantite_range,
            'categories':categories,
            'products':products,
            "clients":clients,


            # ... other context data
        }
        return render(request,'index.html', context)
    
@login_required(login_url='bl_login')
def bl_list(request):
    if request.user.is_superuser:
        bl_data = Bon_Commande.objects.all().order_by('-date_de_bl')
    else:
        bl_data = Bon_Commande.objects.filter(user=request.user).order_by('-date_de_bl')
    return render(request, 'bl_liste.html', {'bl_data': bl_data})
    #return render(request,'bl_liste.html')

from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from xhtml2pdf import pisa
def generate_pdf(request, bon_commande_id):
    # Fetch the Bon_Commande object using the provided bon_commande_id
    bon_commande = Bon_Commande.objects.get(id=bon_commande_id)

    # Your PDF generation logic here (replace this with your actual logic)
    template_path = 'pdf.html'
    context = {'bon_commande': bon_commande}
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename={bon_commande.id}_bon_commande.pdf'

    # Create the PDF file
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))
    
    return response