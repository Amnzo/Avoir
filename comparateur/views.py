import json
import PyPDF2
from django.http import JsonResponse,HttpResponse
import re
from django.shortcuts import render
from .models import Classeur, ExcelData
from django.db.models import Q
# ExcelData.objects.create(reference=data["reference"], UC=data["UC"], HC=data["HC"], ISC=data["ISC"], SCC=data["SCC"], SRC=data["SRC"], SRB=data["SRB"], SRC_UV=data["SRC_UV"], SRBUV=data["SRBUV"], RCC=data["RCC"], price=data["price"])


def extraire_D_correction(texte):
    lines = texte.split('\n')
    #print("**********************************")
    correction_D = []  # List to store decimals
    for line in lines:
        if line.startswith("D"):  # Check if the line starts with "D"
            #print(line)  # Print the line with "D"
            index = lines.index(line) + 1  # Get the index of the next line
            while index < len(lines) and not lines[index].startswith(("D", "CT")):
                # Iterate through subsequent lines until you encounter the next string
                correction_D.append(lines[index])
                #print(lines[index])  # Print the line
                index += 1
    #print("**********************************")
    return correction_D

def extraire_G_correction(texte):
    lines = texte.split('\n')
    #print(lines)
    #print("**********************************")
    correction_G = []  # List to store decimals
    for line in lines:
        if line.startswith("G"):  # Check if the line starts with "D"
            #print(line)  # Print the line with "D"
            index = lines.index(line) + 1  # Get the index of the next line
            while index < len(lines) and not lines[index].startswith(("G", "CT")):
                # Iterate through subsequent lines until you encounter the next string
                correction_G.append(lines[index])
                #print(lines[index])  # Print the line
                index += 1
    #print("**********************************")
    return correction_G
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

#def extract_product_info(text):
def extract_product_info(text):
    pattern = r'Produit\s(.*?)\sD'  # Capture the part after "Produit" and before "D"
    match = re.search(pattern, text)
    if match:
        product_name = match.group(1)
        if "#" in product_name:
            product_name = product_name.replace("#", "")  # Supprimer le caractère "#"
        return product_name
    else:
        return None

def extraire_second_decimal_apres_ET(texte):
    lignes = texte.split('\n')
    chiffres_apres_ET = []  # Initialiser la liste pour stocker les chiffres extraits
    ajouter_ligne_suivante = False  # Variable pour suivre si la ligne suivante doit être ajoutée

    for i, line in enumerate(lignes):
        if line.startswith("ET"):
            ajouter_ligne_suivante = True  # Activer l'ajout de la ligne suivante
        elif ajouter_ligne_suivante:
            chiffres_apres_ET.append(line)  # Ajouter la ligne suivante à la liste
            ajouter_ligne_suivante = False  # Réinitialiser la variable après l'ajout de la ligne

    print(chiffres_apres_ET)
    return chiffres_apres_ET
                 
           

    return chiffres_apres_ET
def extract_value_after_CT_ET(text):
    
    pattern = r'CT\s+ET\s+(\d+,\d+)'  # Expression régulière mise à jour pour capturer la valeur après "CT ET"
    match = re.search(pattern, text)
    if match:
        value = match.group(1)
        return value.replace(',', '.')  # Remplace les virgules par des points pour les nombres décimaux
    else:
        return None
   

    
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
           
            champs_excel_data = [field.name for field in ExcelData._meta.get_fields()]            
            champs_decimal = [field for field in champs_excel_data if isinstance(ExcelData._meta.get_field(field), DecimalField)]
            valuer=[""]
            for champ in champs_decimal:
                if is_word_in_string(champ.upper(), command.split("|")[2].upper()):
                    valuer.append(champ)
                else:
                    pass
            produit = extract_product_info(command.split("|")[2])
            prix_facture=0.0
            if produit is None:
                #print("NONE TYPEEEE")
                c=command.split("|")[2]
                produit=c.split("Produit")[1]
            if produit :
                produit_similaire = trouver_produit_similaire(produit)
                prix_facture = extract_value_after_CT_ET(command.split("|")[2])
              
            product= ExcelData.objects.filter(reference=produit_similaire).first()
            prix_commande = None
            if product:
                for champ in reversed(valuer):
                    if hasattr(product, champ):
                        prix_commande = getattr(product, champ)
                        break  
            if  product and product.classeur.nom=='SEIKO Classe A':
                valuer.append("HSC")
                prix_commande=Decimal(product.HSC).quantize(Decimal('0.01'))      
            if  product and product.classeur.nom=='SEIKO Gamme ECO':
                valuer.append("PRIX ")
                prix_commande=product.prix
            Diff = 0        
            try:
                Diff = Decimal(prix_facture) - Decimal(prix_commande)
                #result = str(Diff)  # Convert Diff back to string for return
            except TypeError:
                Diff = 0

            prix_factures=extraire_second_decimal_apres_ET(command.split("|")[2])
            prix_facture_d=prix_factures[0]
            prix_facture_g=prix_factures[0]
            if len(prix_factures)==2:
                prix_facture_g=prix_factures[1]


         
            print(command)
            if command.startswith("S00126538"):
                print(command)
            
            formatted_command = {
                
                "Commande": command.split("|")[0] ,#command.split("|")[0] , #.split("|")[0],
                "Référence": command.split("Référence")[1].split("Produit")[0].split("|")[0],
                "Produit": produit,
                "CorrectionD":extraire_D_correction(command.split("|")[2].split("ET")[0]),
                "CorrectionG":extraire_G_correction(command.split("|")[2]),
                "Similaire": produit_similaire, 
                "Valeur" : valuer[-1],
                "Prix" :prix_commande,
                "Product":product,
                "Prix_Facture_D": prix_facture_d,   #re.findall(r'\d+,\d+', command[3].strip())[-1]
                "Prix_Facture_G": prix_facture_g,   #re.findall(r'\d+,\d+', command[3].strip())[-1]
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





        