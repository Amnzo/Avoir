from decimal import Decimal
import json
import PyPDF2
from django.http import JsonResponse,HttpResponse
import re
from django.shortcuts import render
from .models import Classeur, ExcelData
from django.db.models import Q
# ExcelData.objects.create(reference=data["reference"], UC=data["UC"], HC=data["HC"], ISC=data["ISC"], SCC=data["SCC"], SRC=data["SRC"], SRB=data["SRB"], SRC_UV=data["SRC_UV"], SRBUV=data["SRBUV"], RCC=data["RCC"], price=data["price"])
def extraire_informations_D(texte):
    # Diviser le texte en lignes
    lignes = texte.split('\n')
    # Initialiser les variables pour stocker les informations
    informations_D = []
    # Indicateur pour détecter la ligne contenant uniquement "D" et "G"
    d_found = False
    # Parcourir les lignes du texte
    for ligne in lignes:
        # Vérifier si la ligne contient uniquement "D"
        if ligne.strip() == "D":
            d_found = True
            continue
        # Si "D" est trouvé, ajouter les lignes suivantes jusqu'à trouver "CT"
        if d_found:
            if ligne.strip() != "CT":
                informations_D.append(ligne)
            else:
                break
    return informations_D



def extraire_informations_G(texte):
    # Diviser le texte en lignes
    lignes = texte.split('\n')
    # Initialiser les variables pour stocker les informations
    informations_G = []
    # Indicateur pour détecter la ligne contenant uniquement "D" et "G"
    d_found = False
    # Parcourir les lignes du texte
    for ligne in lignes:
        # Vérifier si la ligne contient uniquement "D"
        if ligne.strip() == "G":
            d_found = True
            continue
        # Si "D" est trouvé, ajouter les lignes suivantes jusqu'à trouver "CT"
        if d_found:
            if ligne.strip() != "CT":
                informations_G.append(ligne)
            else:
                break

   
    return informations_G

def extraire_prix(texte):
    #print(texte)
   
    lines=texte.split("\n")
    dernieres_decimales = []
    # Diviser chaque ligne en parties distinctes et récupérer la dernière valeur décimale avant chaque "ET"
    ligne_precedente_ET = False
    for ligne in lines:
        if ligne.startswith("ET"):
            ligne_precedente_ET = True
        elif ligne_precedente_ET:
            parties = ligne.split()
            #print("Parties:", parties)
            for partie in reversed(parties):
                if partie.replace(',', '').replace('.', '').isdigit():
                    derniere_valeur = partie
                    #print("Dernière valeur décimale trouvée:", derniere_valeur)
                    dernieres_decimales.append(derniere_valeur)
                    break
            ligne_precedente_ET = False
    #print("Dernières décimales extraites:", dernieres_decimales)
    return dernieres_decimales


    
    

def decortiquer_commande(texte):
    lines = texte.split('\n')
    print(texte)
    # Initialiser les variables à None

    commande = reference = produit1 = None
    commande = lines[1]  # La deuxième ligne est la commande
    
    for i, line in enumerate(lines):
        if line.startswith("Référence"):
            reference = lines[i + 1].strip()
        elif line.startswith("Produit"):
            produit1 = lines[i + 1].strip()
           
    return commande, reference, produit1



import openpyxl
def data(request):
    chemin_fichier_excel = 'C:/Users/Amnzo/Desktop/jonathan/rania.xlsx'
    nom_feuille = 'SEIKO Gamme ECO'
    classeur_parent=Classeur.objects.get(pk=4)

    classeur = openpyxl.load_workbook(chemin_fichier_excel)
    feuille = classeur[nom_feuille]
    # Parcourir les lignes de la feuille de calcul et créer les objets ExcelData
    i=0
    for ligne in feuille.iter_rows(values_only=True):
        i=i+1
        #print("ligne:", ligne)  # Add this line for debugging
        p=ExcelData()
        p.classeur=classeur_parent
        
        p.reference=ligne[0]
        #p.HSC=Decimal(ligne[4]) if ligne[4] is not None else Decimal(0)
        # p.UC=Decimal(ligne[1]) if ligne[1] is not None else Decimal(0)
        # p.HC=Decimal(ligne[2]) if ligne[2] is not None else Decimal(0)
        # p.ISC=Decimal(ligne[3]) if ligne[3] is not None else Decimal(0)
        # p.SCC=Decimal(ligne[4]) if ligne[4] is not None else Decimal(0)
        # p.SRC=Decimal(ligne[5]) if ligne[5] is not None else Decimal(0)
        # p.SRB=Decimal(ligne[6]) if ligne[6] is not None else Decimal(0)
        # p.SRCUV=Decimal(ligne[7]) if ligne[7] is not None else Decimal(0)
        # p.SRBUV=Decimal(ligne[8]) if ligne[8] is not None else Decimal(0)
        # p.RCC=Decimal(ligne[9]) if ligne[9] is not None else Decimal()
        # seiko 2PAIRE
        # p.UC=Decimal(ligne[1]) if ligne[1] is not None else Decimal(0)
        # p.HC=Decimal(ligne[2]) if ligne[2] is not None else Decimal(0)
        # p.SCC=Decimal(ligne[3]) if ligne[3] is not None else Decimal(0)
        # p.SUNUC=Decimal(ligne[4]) if ligne[4] is not None else Decimal(0)
        # p.SUNHC=Decimal(ligne[5]) if ligne[5] is not None else Decimal(0)
        # p.SUNISC=Decimal(ligne[6]) if ligne[6] is not None else Decimal(0)
        # p.POLA_UC=Decimal(ligne[7]) if ligne[7] is not None else Decimal(0)
        # p.POLA_ISC=Decimal(ligne[8]) if ligne[8] is not None else Decimal(0)


        #DERNIER CLASSEUR Game
        p.prix=Decimal(ligne[1]) if ligne[1] is not None else Decimal(0)
        p.save()
        #print(f"{p}")
    classeur.close()
    
    return HttpResponse("DATA BASE CREATED")

from django.db.models import CharField, Value as V
from django.db.models.functions import Length

def trouver_produit_similaire(reference):
    mots_reference = reference.upper().split()  # Convertir la référence en majuscules et la diviser en mots
    #print(mots_reference)
    max_mots_communs = 0  # Initialisez le nombre maximum de mots communs
    produit_similaire = None  # Initialisez la référence du produit similaire
    # Parcourir tous les produits dans la base de données
    for produit in ExcelData.objects.all():
        mots_produit = produit.reference.upper()  # Convertir la référence du produit en majuscules et la diviser en mots
        #print(mots_produit)
        # Compter le nombre de mots communs entre la référence donnée et la référence du produit
        mots_communs = 0
        for mot in mots_reference:
            if mot in mots_produit:
                mots_communs += 1
        
        # Mettre à jour la référence du produit similaire si le nombre de mots communs est le plus grand
        if mots_communs > max_mots_communs:
            max_mots_communs = mots_communs
            produit_similaire = produit.reference

    return produit_similaire
import re
def is_word_in_string(word, string):
    pattern = re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE)
    return re.search(pattern, string) is not None

def extract_commands(content): 
    commands=content.split("Commande")
    return commands
from django.db.models import DecimalField  
from PyPDF2 import PdfReader
from io import BytesIO
def read_pdf(request):
    # Path to the PDF file
    #pdf_path = 'C:/Users/Amnzo/Desktop/jonathan/6.pdf'
    if request.method == 'POST' and request.FILES['pdf_file']:
        pdf_file = request.FILES['pdf_file']
        pdf_data = pdf_file.read()
        pdf_buffer = BytesIO(pdf_data)
        # Create a PdfReader object using the BytesIO buffer
        pdf_reader = PdfReader(pdf_buffer)
        content = ""
            #print(f"Nombre de page = {pdf_reader.pages}")
        for page_num in range(2,len(pdf_reader.pages)):
                #print(page_num)
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            encoded_text = text.encode('utf-8', 'ignore')  # Ignore characters that cannot be encoded
            decoded_text = encoded_text.decode('utf-8')
            content += decoded_text
        commands = extract_commands(content)
        formatted_commands = []
        for command in commands[1:]:
          
            commande_decortiquer,reference_decortiquer, produit_1_decortiquer=decortiquer_commande(command)
            

           
            D_decortiquer=extraire_informations_D(command)
            G_decortiquer=extraire_informations_G(command)
            
            prix_d=0
            prix_g=0
            for cmd in command.split('\n'):
                # Vérifier si la ligne contient uniquement "D"
                if cmd.strip() == "D":
                    prix_d=extraire_prix(command)[0]
                if cmd.strip() == "G":
                    prix_g=extraire_prix(command)[1]

           
            champs_excel_data = [field.name for field in ExcelData._meta.get_fields()]            
            champs_decimal = [field for field in champs_excel_data if isinstance(ExcelData._meta.get_field(field), DecimalField)]
            valuer=[""]
            valuer_2=[""]
            for champ in champs_decimal:
                if is_word_in_string(champ.upper(), produit_1_decortiquer.upper()):
                    valuer.append(champ)
                else:
                    pass

            for champ in champs_decimal:
                if is_word_in_string(champ.upper(), produit_1_decortiquer.upper()):
                    valuer_2.append(champ)
                else:
                    pass

            produit_similaire_1 = trouver_produit_similaire(produit_1_decortiquer.replace('#', ''))
            produit_similaire_2 = trouver_produit_similaire(produit_1_decortiquer.replace('#', '')) 
            product_1= ExcelData.objects.filter(reference=produit_similaire_1).first()
            product_2= ExcelData.objects.filter(reference=produit_similaire_2).first()
            prix_commande = None
            prix_commande_2 = None
            if product_1:
                for champ in reversed(valuer):
                    if hasattr(product_1, champ):
                        prix_commande = getattr(product_1, champ)
                        break  
            if  product_1 and product_1.classeur.nom=='SEIKO Classe A':
                valuer.append("HSC")
                prix_commande=Decimal(product_1.HSC).quantize(Decimal('0.01'))      
            if  product_1 and product_1.classeur.nom=='SEIKO Gamme ECO':
                valuer.append("PRIX ")
                prix_commande=product_1.prix


            #-------------------------

            if product_2:
                for champ in reversed(valuer):
                    if hasattr(product_2, champ):
                        prix_commande = getattr(product_2, champ)
                        break  
            if  product_2 and product_2.classeur.nom=='SEIKO Classe A':
                valuer.append("HSC")
                prix_commande_2=Decimal(product_2.HSC).quantize(Decimal('0.01'))      
            if  product_2 and product_2.classeur.nom=='SEIKO Gamme ECO':
                valuer.append("PRIX ")
                prix_commande_2=product_2.prix
            Diff = 0        
            try:
                Diff = 22
                #result = str(Diff)  # Convert Diff back to string for return
            except TypeError:
                Diff = 0

           
          
          
            remise_entier_1=remise_produit_1=product_1.remise
            remise_entier_2=remise_produit_2=product_2.remise
            parties = str(remise_produit_1).split(".")
            if len(parties) > 1 and int(parties[1]) == 0:
                remise_entier = int(parties[0])
            else:
                remise_entier = remise_produit_1
            taux_remise_decimal = Decimal(remise_entier) / Decimal(100)
            prix_d = prix_d.replace(',', '.')
            nouveau_montant=Decimal(prix_d)-Decimal(prix_d)*taux_remise_decimal
           
            formatted_command = {
                
                "Commande": commande_decortiquer ,#command.split("|")[0] , #.split("|")[0],
                "Référence": reference_decortiquer.split("|")[0],
                "Produit_1": produit_1_decortiquer,
                "Produit_2_": produit_1_decortiquer,
                "CorrectionD":D_decortiquer,
                "CorrectionG":G_decortiquer, 
                "Similaire_1": produit_similaire_1,
                "Similaire_1": produit_similaire_2,
                "Remise" : remise_entier,
                "Apres_Remise" : nouveau_montant,
                "Valeur" : valuer[-1],
                "Prix" :prix_commande,
                "Product_1":product_1,
                "Product_2":product_2,
                "Prix_Facture_D": prix_d,   #re.findall(r'\d+,\d+', command[3].strip())[-1]
                "Prix_Facture_G": prix_g,   #re.findall(r'\d+,\d+', command[3].strip())[-1]
                "Diff": Diff
            
                
                
            }
            formatted_commands.append(formatted_command)

        return render(request, 'excel/excel.html', {'formatted_commands': formatted_commands})
    return render(request, 'excel/excel.html')
    




import random
from decimal import Decimal
from .models import ExcelData

def generate_random_decimal():
    # Générer un nombre décimal aléatoire entre 0 et 1000 avec 2 décimales
    return Decimal(random.uniform(0, 1000)).quantize(Decimal('0.01'))

def generate_random_values(request):
    # Récupérer tous les objets ExcelData
    produits = ExcelData.objects.all()

    # Parcourir chaque produit et attribuer des valeurs décimales aléatoires
    for produit in produits:
        # Attribuer des valeurs décimales aléatoires à chaque champ DecimalField
        produit.UC = generate_random_decimal()
        produit.HC = generate_random_decimal()
        produit.ISC = generate_random_decimal()
        produit.SCC = generate_random_decimal()
        produit.SRC = generate_random_decimal()
        produit.SRB = generate_random_decimal()
        produit.SRCUV = generate_random_decimal()
        produit.SRBUV = generate_random_decimal()
        produit.RCC = generate_random_decimal()
        produit.SUNUC = generate_random_decimal()
        produit.SUNHC = generate_random_decimal()
        produit.SUNSCC = generate_random_decimal()
        produit.SUNUC = generate_random_decimal()
        produit.SUNUC = generate_random_decimal()
        produit.POLA_UC = generate_random_decimal()
        produit.POLA_ISC = generate_random_decimal()
        produit.prix = generate_random_decimal()

        # Sauvegarder les modifications dans la base de données
        produit.save()

    #print("Valeurs décimales aléatoires générées avec succès pour tous les produits.")
    return HttpResponse("*********************")




def delete(request):
    products_to_delete = ExcelData.objects.filter(classeur__nom='SEIKO Gamme ECO')
    # Delete the products
    products_to_delete.delete()
    return HttpResponse("products_to_delete")




from django.http import HttpResponse
from openpyxl import Workbook

from bs4 import BeautifulSoup
import io

def export_to_excel(request):
    # Récupérer les données du tableau HTML depuis la requête POST
    table_data = request.POST.get('table_data', '')

    # Analyser le HTML pour extraire les données de la table
    soup = BeautifulSoup(table_data, 'html.parser')
    table = soup.find('table')

    # Créer un classeur Excel et ajouter les données de la table
    wb = Workbook()
    ws = wb.active
    for row_idx, row in enumerate(table.find_all('tr')):
        for col_idx, cell in enumerate(row.find_all(['td', 'th'])):
            ws.cell(row=row_idx + 1, column=col_idx + 1, value=cell.text)

    # Créer une réponse HTTP pour le fichier Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="table_data.xlsx"'

    # Enregistrer le classeur Excel dans la réponse HTTP
    wb.save(response)

    return response





        