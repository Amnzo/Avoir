import pandas as pd

# Charger le fichier Excel
excel_file = "MAPPING.xlsx"
df = pd.read_excel(excel_file)

# Extraire les prix des produits
prix_produits = df.iloc[1:, 1:].values.flatten().tolist()

# Extraire les prix des commandes
prix_commandes = []

# Parcourir les colonnes pour trouver les prix des commandes
for col in df.columns:
    for value in df[col]:
        if isinstance(value, str) and "Total commande" in value:
            prix_commandes.append(float(value.split()[-1].replace(',', '.')))

print("Prix des produits:", prix_produits)
print("Prix des commandes:", prix_commandes)
