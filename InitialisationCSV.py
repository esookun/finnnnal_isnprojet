import csv

input_file = 'vocabulaire_flashcards_2colonnes.csv'
output_file = 'mots_initialises.csv'

initialized_rows = []
with open(input_file, 'r', encoding='utf-8') as infile:
    reader = csv.reader(infile, delimiter=';')
    header = next(reader)
    for row in reader:
        if len(row) >= 2:
            french, english = row[0].strip(), row[1].strip()
            initialized_rows.append([french, english, "NonConnait", "0", "0"])

with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerows(initialized_rows)