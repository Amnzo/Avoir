
from django.shortcuts import render,HttpResponse

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from avoirapp.models import Client, Famille
from .forms import CustomLoginForm
from .models import Bon_Commande, Produit
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
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

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Spacer,Image
def generate_pdf(request, bon_commande_id):
   # Fetch the Bon_Commande object using the provided bon_commande_id
    bon_commande = Bon_Commande.objects.get(id=bon_commande_id)

    # Create an HttpResponse object with the content type 'application/pdf'
    response = HttpResponse(content_type='application/pdf')
    # Set the content disposition header to specify the filename
    response['Content-Disposition'] = f'filename={bon_commande.id}_bon_commande.pdf'

    # Set the width of the PDF document
    pdf_doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=18, width=500)

    elements = []

    

    # Add store logo
    elements.append(Spacer(1, 5))

    # Add store and client information in the same row using nested tables
    store_info_data = [
        ["Livré  a "],
        ["SCORTIS OPTIC"],
        ["38 rue Saint Denis ,927000 COLOMBIS ,France"],
        [""],
        [""],

    ]
    store_info_table = Table(store_info_data, style=[
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
         ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),  # Apply 'Helvetica-Bold' to the first cell
    ])

    client_info_data = [
        ["Informations Acheteur"],
        ["SCORTIS OPTIC"],
        ["38 rue Saint Denis,927000 COLOMBIS,France"],
        ["N de TVA INTRACEO : "],
        ["FR123654789 "],
    ]
    client_info_table = Table(client_info_data, style=[
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),  # Apply 'Helvetica-Bold' to the first cell
    ])

    # Create a nested table to align store_info_table and client_info_table horizontally
    nested_table_data = [
        [store_info_table, Spacer(1, 10), client_info_table]
    ]
    nested_table = Table(nested_table_data, colWidths=[250, 50, 250])  # Adjust colWidths as needed

    # Add the nested table to the elements list
    elements.append(nested_table)
    elements.append(Spacer(1, 20))
    elements.append(nested_table)
    elements.append(Spacer(1, 40))

    # Add Bon de Commande header
    bon_de_commande_data = [
        ["Reference", "Designation", "Sphere", "Cylindre", "Axe", "OEIL", "Quantité"],
        [bon_commande.produit_d.id, bon_commande.produit_d.nom, bon_commande.sphere_d,
         bon_commande.cylindre_d, bon_commande.axe_d, "DROIT", bon_commande.quatite_d],
        [bon_commande.produit_g.id, bon_commande.produit_g.nom, bon_commande.sphere_g,
         bon_commande.cylindre_g, bon_commande.axe_g, "GAUCHE", bon_commande.quatite_g],
    ]
    bon_de_commande_table = Table(bon_de_commande_data, style=[
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ])
    elements.append(bon_de_commande_table)

    # Build the PDF document
    pdf_doc.build(elements)

    # Return the HttpResponse object with the generated PDF
    subject = 'Your Bon de Commande'
    message = 'Thank you for your order. Please find your Bon de Commande attached.'
    from_email = 'salmi.ensa.ilsi@gmail.com'  # Replace with your email address
    to_email = 'salmi.ensa.ilsi@gmail.com'  # Replace with the recipient's email address

    email = EmailMessage(subject, message, from_email, [to_email])
    email.attach(f'{bon_commande.id}_bon_commande.pdf', response.getvalue(), 'application/pdf')
    email.send()

    return HttpResponse('Email sent with PDF attachment.')







def test_email(request):
    subject = 'Test Email'
    message = 'This is a test email from Django.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['recipient@example.com']

    send_mail(subject, message, from_email, recipient_list)

    return HttpResponse("Test email sent successfully.")