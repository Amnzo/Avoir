from django.shortcuts import get_object_or_404, redirect, render,HttpResponse
from django.db.models import Sum

from avoirapp.forms import AvoirConsumeForm, AvoirForm
from .models import Avoir, Client

# Create your views here.

def client(request):
    clients = Client.objects.annotate(total_avoir=Sum('avoir__montant')).all()
    return render(request, 'client.html', {'clients': clients})
    #return render(request, 'client.html')

def avoir(request):
    #return render(request, 'avoir.html')
 # Query all Avoir instances where is_avoir is True
    avoirs = Avoir.objects.filter(is_avoir=True)

    # Pass the queryset to the template
    return render(request, 'avoir_list.html', {'avoirs': avoirs})

def client_details(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    # You can add additional logic or context data here if needed
    return render(request, 'client_details.html', {'client': client})

def ajouter_avoir(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = AvoirForm(request.POST, request.FILES)  # Ensure FILES is included
        if form.is_valid():
            avoir = form.save(commit=False)
            avoir.client = client
            avoir.save()
            return redirect('client_details', client_id=client.id)
    else:
        form = AvoirForm()

    return render(request, 'ajouter_avoir.html', {'client': client, 'form': form})




def consommer_avoir(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = AvoirConsumeForm(request.POST, request.FILES)
        if form.is_valid():
            montant_a_consommer = form.cleaned_data['montant_a_consommer']

            # Vérifier si le montant à consommer est valide
            total_avoir = client.total_avoir_client()
            if montant_a_consommer <= total_avoir:
                # Créer une instance de modèle Avoir pour représenter la consommation
                Avoir.objects.create(
                    client=client,
                    montant=-montant_a_consommer,
                    description=form.cleaned_data['description'],
                    facture=form.cleaned_data['facture'],
                    is_avoir=False
                )
                return redirect('client_details', client_id=client.id)
            else:
                form.add_error('montant_a_consommer', f"Impossible de consommer plus que le total de l'avoir ({total_avoir} Dh).")

    else:
        form = AvoirConsumeForm()

    return render(request, 'consommer_avoir.html', {'client': client, 'form': form})
