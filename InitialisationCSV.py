# Importation du module CSV
import csv

# Fichiers d'entrée et de sortie
input_file = 'vocabulaire_flashcards_2colonnes.csv'
output_file = 'mots_initialises.csv'

# Liste pour stocker les lignes initialisées
initialized_rows = []
with open(input_file, 'r', encoding='utf-8') as infile:
    # Lecture du CSV avec point-virgule comme délimiteur
    reader = csv.reader(infile, delimiter=';')
    # Sauter l'en-tête
    header = next(reader)
    for row in reader:
        # Vérifier que la ligne contient au moins deux colonnes
        if len(row) >= 2:
            french, english = row[0].strip(), row[1].strip()
            # Ajouter les champs initiaux pour Connait/NonConnait et compteurs
            initialized_rows.append([french, english, "NonConnait", "0", "0"])

with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    # Écriture des lignes initialisées dans le nouveau fichier CSV
    writer = csv.writer(outfile)
    writer.writerows(initialized_rows)
