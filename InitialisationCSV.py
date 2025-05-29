import csv
import json

with open('state.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    
input_file = data["csv_path"]

# Liste temporaire pour stocker les données modifiées
updated_data = []

with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile, delimiter=';')
    
    for row in reader:
        # Vérifier que la ligne contient au moins deux colonnes
        if len(row) >= 2:
            french = row[0].strip()
            english = row[1].strip()
            # Ajouter les nouvelles colonnes à la ligne existante
            updated_row = row[:2] + ["NonConnait", "0", "0"]
            updated_data.append(updated_row)

# Écraser le fichier original avec les données mises à jour
with open(input_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile, delimiter=';')  
    writer.writerows(updated_data)

print(f"Le fichier {input_file} a été mis à jour avec succès!")
print(f"Nombre de lignes traitées : {len(updated_data)}")