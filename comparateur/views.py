from decimal import Decimal, InvalidOperation
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



    
    

def decortiquer_commande(texte):
    lines = texte.split('\n')
    #print(texte)
    # Initialiser les variables à None

    commande = reference = produit1 = option=None
    commande = lines[1]  # La deuxième ligne est la commande
    option=option1=option2=option3=option4=option5=some1=some2=None
    for i, line in enumerate(lines):
        if line.startswith("Référence"):
            reference = lines[i + 1].strip()
        elif line.startswith("Produit"):
            produit1 = lines[i + 1].strip()
        elif line.startswith("Options"):
            option=f"{lines[i + 1].strip()}"
            option1 = f"{lines[i + 2].strip()}"
            option2 = f"{lines[i + 3].strip()}"
            option3=f"{lines[i + 4].strip()}"
           
            if i + 5 < len(lines):
                option4 = lines[i + 5].strip()
            if i + 6 < len(lines):
                option5 = lines[i + 6].strip()
           # Decimal(str(prix_d).replace(',', '.'))
            some1 = Decimal(str(option1).replace(',', '.'))-Decimal(str(option2).replace(',', '.'))
            if option4 is not None and option5 is not None:
                try:
                    option4_decimal = Decimal(option4.replace(',', '.'))
                    option5_decimal = Decimal(option5.replace(',', '.'))
                    some2 = option4_decimal - option5_decimal
                except InvalidOperation:
                    some2 = Decimal(0)
            else:
                some2 = Decimal(0)
            
            
           
    return commande, reference, produit1,option,option1,option2,option3,option4,option5,some1,some2



import openpyxl
def data(request):
    chemin_fichier_excel = 'C:/Users/Amnzo/Desktop/jonathan/rania.xlsx'
    nom_feuille = 'SEIKO Offre 2e paire'
    classeur_parent=Classeur.objects.get(pk=3)

    classeur = openpyxl.load_workbook(chemin_fichier_excel)
    feuille = classeur[nom_feuille]
    # Parcourir les lignes de la feuille de calcul et créer les objets ExcelData
    i=0
    for ligne in feuille.iter_rows(values_only=True):
        i=i+1
        print("ligne:", ligne)  # Add this line for debugging
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
        # p.RCC=Decimal(ligne[9]) if ligne[9] is not None else Decimal(0)
        #seiko 2PAIRE
        p.UC=Decimal(ligne[1]) if ligne[1] is not None else Decimal(0)
        p.HC=Decimal(ligne[2]) if ligne[2] is not None else Decimal(0)
        p.SCC=Decimal(ligne[3]) if ligne[3] is not None else Decimal(0)
        p.SUNUC=Decimal(ligne[4]) if ligne[4] is not None else Decimal(0)
        p.SUNHC=Decimal(ligne[5]) if ligne[5] is not None else Decimal(0)
        p.SUNISC=Decimal(ligne[6]) if ligne[6] is not None else Decimal(0)
        p.POLA_UC=Decimal(ligne[7]) if ligne[7] is not None else Decimal(0)
        p.POLA_ISC=Decimal(ligne[8]) if ligne[8] is not None else Decimal(0)


        #DERNIER CLASSEUR Game
        p.prix=Decimal(ligne[1]) if ligne[1] is not None else Decimal(0)
        p.save()
        print(f"{p}")
    classeur.close()
    
    return HttpResponse("DATA BASE CREATED")

from django.db.models import CharField, Value as V
from django.db.models.functions import Length



    #return produits_similaires
from Levenshtein import distance
def trouver_produit_similaire2(reference):
    produits = ExcelData.objects.all()
    distances = [(produit.reference, distance(reference, produit.reference)) for produit in produits]
    distances.sort(key=lambda x: x[1])
    print(distances[0][0])
    return distances[0][0]
def trouver_produit_similaire(reference):

    if "JETSTAR" in reference:
        reference=trouver_produit_similaire2(reference)

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
        
        # Vérifier si le produit contient "kids" et la référence donnée ne contient pas "kids"
        if "KIDS" in produit.reference.upper() and "KIDS" not in reference.upper():
            continue  # Passer au produit suivant
        
        # Mettre à jour la référence du produit similaire si le nombre de mots communs est le plus grand
        if mots_communs > max_mots_communs:
            max_mots_communs = mots_communs
           
            produit_similaire = produit.reference

    return produit_similaire






import re
def is_word_in_string(word, string):
    pattern = re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE)
    return re.search(pattern, string) is not None


def extraire_prix2(texte):
    lines = texte.split("\n")
    dernier_decimal_apres_ET = []
    ligne_precedente_ET = False
    
    for i, ligne in enumerate(lines):
        if ligne.startswith("ET"):
            parties = ligne.split()
            derniers_decimaux = []
            for j in range(i + 1, len(lines)):
                parties_suivantes = lines[j].split()
                for partie in reversed(parties_suivantes):
                    if partie.replace(',', '').replace('.', '').isdigit():
                        dernier_dec = partie.replace(',', '.')  # Assurez-vous que la virgule est au format décimal
                        derniers_decimaux.append(dernier_dec)
                        break
                else:
                    # Si aucun nombre n'est trouvé dans cette ligne, arrêtez la boucle
                    break
            dernier_decimal_apres_ET.append(derniers_decimaux)
    #print(dernier_decimal_apres_ET)
              
    return dernier_decimal_apres_ET

# def extraire_prix(texte):
#     lines = texte.split("\n")
#     #print(lines)
#     dernier_decimal_apres_ET = []
#     ligne_precedente_ET = False
    
#     for i, ligne in enumerate(lines):
#         if ligne.startswith("ET"):
#             ligne_precedente_ET = True
#         elif ligne_precedente_ET:
#             parties = ligne.split()
#             dernier_dec = None
#             for j in range(i, len(lines)):
#                 parties_suivantes = lines[j].split()
#                 for partie in reversed(parties_suivantes):
#                     if partie.replace(',', '').replace('.', '').isdigit():
#                         dernier_dec = partie
#                         break
#                 if dernier_dec:
#                     break
#             if dernier_dec:
#                 dernier_dec = dernier_dec.replace(',', '.')  # Assurez-vous que la virgule est au format décimal
#                 dernier_decimal_apres_ET.append(dernier_dec)
#             else:
#                 dernier_decimal_apres_ET.append("Pas de décimal trouvé")
#             ligne_precedente_ET = False
              
#     return dernier_decimal_apres_ET


def analyser_commande(commande):
    #prices = extraire_prix(commande)
    prices_ = extraire_prix2(commande)
    #print(prices_)
    is_d = is_g = False

    for cmd in commande.split('\n'):
        # Vérifier si la ligne contient uniquement "D" ou "G"
        if cmd.strip() == "D":
            is_d = True
        if cmd.strip() == "G":
            is_g = True

    prix_d = prix_g = 0

    if len(prices_) == 2:
        prix_d = prices_[0][-1]
        prix_g = prices_[1][-1]
        #print(f" both {is_d} - {is_g} {prices}")

    elif len(prices_) == 1:
        if is_d:
            prix_d = prices_[0][-1]
            #print(f" D {is_d} - {is_g} {prices}")
        elif is_g:
            prix_g = prices_[0][-1]
            #print(f" G {is_d} - {is_g} {prices}")

    #print(f"Prix pour D: {prix_d}, Prix pour G: {prix_g}")
    return prix_d,prix_g




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
          
            commande_decortiquer,reference_decortiquer, produit_1_decortiquer,option,option1,option2,option3,option4,option5,some1,some2=decortiquer_commande(command)
            #print("Option")
            #print(option)
            

           
            D_decortiquer=extraire_informations_D(command)
            G_decortiquer=extraire_informations_G(command)
            prix_d,prix_g=analyser_commande(command)
            extraire_prix2(command)
            
           
            champs_excel_data = [field.name for field in ExcelData._meta.get_fields()]            
            champs_decimal = [field for field in champs_excel_data if isinstance(ExcelData._meta.get_field(field), DecimalField)]
            valuer=["UC"]
            valuer_2=["UC"]
            for champ in champs_decimal:
                if is_word_in_string(champ.upper(), produit_1_decortiquer.upper()):
                    valuer[0]=champ
                else:
                    pass

            for champ in champs_decimal:
                if is_word_in_string(champ.upper(), produit_1_decortiquer.upper()):
                    #valuer_2.append(champ)
                    valuer_2[0]=champ
                else:
                    pass

            produit_similaire_1 = trouver_produit_similaire(produit_1_decortiquer.replace('JET STAR','JETSTAR').replace('85%','')) 
            produit_similaire_2 = trouver_produit_similaire(produit_1_decortiquer.replace('JET STAR','JETSTAR').replace('85%','')) 
            product_1= ExcelData.objects.filter(reference=produit_similaire_1).first()
            product_2= ExcelData.objects.filter(reference=produit_similaire_2).first()
            prix_catalogue_1 = None
            prix_catalogue_2 = None
            if product_1:
                for champ in reversed(valuer):
                    if hasattr(product_1, champ):
                        prix_catalogue_1 = getattr(product_1, champ)
                        break
            if  product_1 and product_1.reference.startswith('CLASSE A'):
                
                valuer[0]="HSC"
                print(valuer)
                print(product_1)
                print(product_1.HSC)
                prix_catalogue_1=Decimal(product_1.HSC).quantize(Decimal('0.01'))
            startvision=["STARVISION","JETSTAR","SENSO"]      
            if  product_1 and any(product_1.reference.startswith(start) for start in startvision):
                print("***************************************************")
                valuer[0]="PRIX"
                print(valuer)
                print(product_1)
                print(product_1.prix)
                prix_catalogue_1=Decimal(product_1.prix).quantize(Decimal('0.01'))  
            #if product_1 and "non traité" in produit_1_decortiquer and not  product_1.classeur.nom=='SEIKO Classe A':
                #print("***************************************************")
                #print("non triater trouver----------------------------------")
                #print(produit_1_decortiquer)
                #valuer.append("UC")
                #print(valuer)
                #print(product_2)
                #print(product_2.UC)
                #print("***************************************************")
                #prix_catalogue_1=product_1.UC.quantize(Decimal('0.01'))
                #print(prix_catalogue_1) 
            if product_2 and "non traité" in produit_1_decortiquer and not product_2.classeur.nom=='SEIKO Classe A':
                #print("non triater trouver----------------------------------")
                #valuer.append("UC")
                prix_catalogue_2=product_2.UC.quantize(Decimal('0.01'))
                #print(prix_catalogue_2) 
            


            #-------------------------

            if product_2:
                for champ in reversed(valuer):
                    if hasattr(product_2, champ):
                        prix_catalogue_2 = getattr(product_2, champ)
                        break  
            if  product_2 and product_2.classeur.nom=='SEIKO Classe A':
                valuer.append("HSC")
                prix_catalogue_2=Decimal(product_2.HSC).quantize(Decimal('0.01'))      
            if  product_2 and product_2.classeur.nom=='SEIKO Gamme ECO':
                valuer.append("PRIX ")
                prix_catalogue_2=Decimal(product_2.prix).quantize(Decimal('0.01'))  
                #print(f"prix_catalogue_2 {prix_catalogue_2}")
            

           
          
            if product_1:
                remise_entier_1=remise_produit_1=product_1.remise
            if product_1:
                remise_entier_2=remise_produit_2=product_2.remise
            
            
            parties = str(remise_produit_1).split(".")
            if len(parties) > 1 and int(parties[1]) == 0:
                remise_entier = int(parties[0])
            else:
                remise_entier = remise_produit_1
            taux_remise_decimal_d =Decimal(str(prix_d).replace(',', '.'))-((Decimal(remise_entier) / Decimal(100))*Decimal(str(prix_d).replace(',', '.')))
            taux_remise_decimal_g =Decimal(str(prix_g).replace(',', '.'))-((Decimal(remise_entier) / Decimal(100))*Decimal(str(prix_g).replace(',', '.')))
            #taux_remise_decimal = Decimal(remise_entier) / Decimal(100)  # Calcul du taux de remise en décimal
            #montant_remise = Decimal(str(prix_d).replace(',', '.')) - taux_remise_decimal

            Diff_d=Diff_g = 0        
            try:
                Diff_d = (prix_catalogue_1-taux_remise_decimal_d ).quantize(Decimal('0.01'))
                #result = str(Diff)  # Convert Diff back to string for return
            except TypeError:
                Diff_d = 0
            try:
                Diff_g = (prix_catalogue_2-taux_remise_decimal_g).quantize(Decimal('0.01'))
                #result = str(Diff)  # Convert Diff back to string for return
            except TypeError:
                Diff_g = 0
            
           
            formatted_command = {
                
                "Commande": commande_decortiquer ,#command.split("|")[0] , #.split("|")[0],
                "Référence": reference_decortiquer,
                "Produit_1": produit_1_decortiquer,
                "Produit_2_": produit_1_decortiquer,
                "CorrectionD":D_decortiquer,
                "CorrectionG":G_decortiquer, 
                "Similaire_1": produit_similaire_1,
                "Similaire_1": produit_similaire_2,
                "Remise" : remise_entier,
                "Apres_Remise_d" : taux_remise_decimal_d.quantize(Decimal('0.01')),
                "Apres_Remise_g" : taux_remise_decimal_g.quantize(Decimal('0.01')),
                "Valeur" : valuer[-1],
                "Prix_catalogue_1" :prix_catalogue_1,
                "Prix_catalogue_2" :prix_catalogue_2,
                "Product_1":product_1,
                "Product_2":product_2,
                "Prix_Facture_D": prix_d,   #re.findall(r'\d+,\d+', command[3].strip())[-1]
                "Prix_Facture_G": prix_g,   #re.findall(r'\d+,\d+', command[3].strip())[-1]
                "Diff_d":Diff_d,
                "Diff_g":Diff_g,
                "Option":option,
                "Option1":option1,
                "Option2":option2,
                "Option3":option3,
                "Option4":option4,
                "Option5":option5,
                "Some1":some1,
                "Some2":some2

            
                
                
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

from openpyxl import Workbook
from django.http import HttpResponse

# Fonction pour exporter les données vers Excel
from openpyxl import Workbook
from django.http import HttpResponse
from bs4 import BeautifulSoup

# Fonction pour extraire les données du tableau HTML
# Fonction pour extraire les données du tableau HTML
def extract_table_data(html_data):
    # Initialiser une liste pour stocker les données du tableau
    table_data = []
    # Utiliser BeautifulSoup pour parser le HTML
    soup = BeautifulSoup(html_data, 'html.parser')

    # Trouver le premier tableau dans le HTML
    table = soup.find('table')

    # Si un tableau est trouvé
    if table:
        # Trouver toutes les lignes dans le tableau
        rows = table.find_all('tr')

        # Pour chaque ligne dans le tableau
        for row in rows:
            # Trouver toutes les cellules dans la ligne
            cells = row.find_all(['td', 'th'])

            # Extraire le texte de chaque cellule et ajouter à la liste des données du tableau
            row_data = [cell.get_text(strip=True) for cell in cells]

            # Vérifier si la colonne "Correction" est présente et la nettoyer
            if "Correction" in row_data:
                correction_index = row_data.index("Correction") + 1
                row_data[correction_index] = row_data[correction_index].strip()

            table_data.append(row_data)

    return table_data


# Fonction pour exporter les données vers Excel
def export_to_excel(request):
    # Récupérer les données du formulaire POST
    table_data = request.POST.get('table_data')

    # Extraire les données du tableau HTML
    data = extract_table_data(table_data)

    # Créer un nouveau classeur Excel
    wb = Workbook()
    ws = wb.active

    # Ajouter les données au classeur Excel
    for row in data:
        ws.append(row)

    # Définir la largeur de colonne pour chaque colonne
    for col in ws.columns:
        max_length = 0
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[col[0].column_letter].width = adjusted_width

    # Enregistrer le classeur Excel dans un objet BytesIO
    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # Retourner une réponse de téléchargement du fichier Excel
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="commandes.xlsx"'
    return response





        