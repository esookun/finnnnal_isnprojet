import csv                                      
import json                                     
import tkinter as tk                            
from tkinter import messagebox                  
import os                                       

# Constantes
STATE_FILE = 'level_info.txt'                   # Fichier stockant le chemin du CSV et le numéro de session
PROGRESS_FILE = 'session_progress.json'         # Fichier stockant les sessions déjà complétées
DAILY_REVIEW_LIMIT = None                       # Pas de limite quotidienne
SESSION_SIZE = 5                                # Nombre de nouveaux mots par session
KNOWN_INTERVALS = [1, 2, 4, 7, 15, 30]          # Intervalles de révision pour les mots connus

class Word:
    def __init__(self, english, french, mastery='NonConnait', times=0, days_since=0):
        # Initialise un objet mot avec anglais, français, niveau de maîtrise, nombre de répétitions, et jours depuis dernière révision
        self.english = english
        self.french = french
        self.mastery = mastery
        self.times = int(times)
        self.days_since = int(days_since)

    def is_due(self):
        # Détermine si le mot doit être revu, selon mastery et days_since
        if self.times == 0:
            return False
        if self.mastery == 'Connait':
            idx = self.times - 1
            threshold = KNOWN_INTERVALS[idx] if idx < len(KNOWN_INTERVALS) else KNOWN_INTERVALS[-1]
        elif self.mastery == 'Incertain':
            idx = self.times - 2
            threshold = KNOWN_INTERVALS[idx] if 0 <= idx < len(KNOWN_INTERVALS) else 1
        else:
            threshold = 1
        return self.days_since >= threshold

    def to_csv_row(self):
        # Retourne la ligne CSV correspondante au mot
        return [self.french, self.english, self.mastery, str(self.times), str(self.days_since)]

class WordBank:
    def __init__(self, words):
        # Initialise la banque avec une liste d’objets Word
        self.words = words
        
    @classmethod
    def load_csv(cls, filename):
        # Charge les mots depuis un fichier CSV
        words = []
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 5:
                    row += ['NonConnait', '0', '0']
                french, english, mastery, times, days_since = row
                words.append(Word(english.strip(), french.strip(), mastery.strip(), times, days_since))
        return cls(words)

    def save_csv(self, filename):
        # Sauvegarde la liste de mots dans un fichier CSV
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for word in self.words:
                writer.writerow(word.to_csv_row())

    def increment_days(self):
        # Incrémente le compteur days_since pour tous les mots déjà vus
        for w in self.words:
            if w.times > 0:
                w.days_since += 1

    def get_words_for_session(self, session_number):
        # Sélectionne les mots à réviser : mots dus et nouveaux mots de la session
        start_idx = (session_number - 1) * SESSION_SIZE
        session_words = self.words[start_idx : start_idx + SESSION_SIZE]
        review_candidates = [w for w in self.words if w.is_due()]
        return review_candidates + [w for w in session_words if w.times == 0]

def load_session_info():
    # Lit le fichier STATE_FILE pour récupérer le CSV et le numéro de session
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            csv_path = lines[0].strip()
            session_number = int(lines[1].strip())
            return csv_path, session_number
    except:
        return "mots_initialises.csv", 1

def record_session_completion(session_number):
    # Enregistre la session complétée dans PROGRESS_FILE
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            completed = set(json.load(f))
    else:
        completed = set()
    completed.add(session_number)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(completed), f, indent=2)

def main():
    # Fonction principale : charge l’état, prépare la session et gère l’interface
    CSV_FILE, session_number = load_session_info()
    wb = WordBank.load_csv(CSV_FILE)
    wb.increment_days()
    today_words = wb.get_words_for_session(session_number)
    current_list = today_words.copy()
    retry_list = []

    # Initialisation de la fenêtre Tkinter
    root = tk.Tk()
    root.title(f"Session {session_number}")

    # Variables liées aux widgets
    eng_var, fr_var, prog_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
    label_eng = tk.Label(root, textvariable=eng_var, font=("Arial", 22))
    label_fr  = tk.Label(root, textvariable=fr_var,  font=("Arial", 14))
    label_prog= tk.Label(root, textvariable=prog_var,font=("Arial", 10))
    btn_show  = tk.Button(root, text="Afficher la signification", width=25, height=2)
    btn_known = tk.Button(root, text="Je connais", width=25, height=2)
    btn_fuzzy = tk.Button(root, text="Je suis incertain", width=25, height=2)
    btn_unknown = tk.Button(root, text="Je ne connais pas", width=25, height=2)

    # Placement des widgets dans la grille
    label_eng.grid(row=0, column=0, columnspan=3, pady=10)
    label_fr.grid(row=1, column=0, columnspan=3, pady=5)
    btn_known.grid(row=3, column=0, padx=5, pady=10)
    btn_fuzzy.grid(row=3, column=1, padx=5, pady=10)
    btn_unknown.grid(row=3, column=2, padx=5, pady=10)
    label_prog.grid(row=4, column=0, columnspan=3, pady=5)

    idx = 0  # index courant dans la liste de mots

    def show_word(i):
        # Affiche le mot anglais et met à jour l’état
        nonlocal idx
        w = current_list[i]
        eng_var.set(w.english)
        fr_var.set("")
        btn_show.grid(row=2, column=0, columnspan=3, pady=5)
        btn_show.config(state=tk.NORMAL)
        idx = i
        prog_var.set(f"Mot {i+1}/{len(current_list)}")

    def reveal():
        # Montre la traduction française
        fr_var.set(current_list[idx].french)
        btn_show.config(state=tk.DISABLED)

    def feedback(response):
        # Traite le retour utilisateur (connait/incertain/nonConnait)
        w = current_list[idx]
        if response == 'Je connais':
            w.mastery = 'Connait'
            w.times += 1
            w.days_since = 0
        elif response == 'Je suis incertain':
            w.mastery = 'Incertain'
            retry_list.append(w)
        else:
            w.mastery = 'NonConnait'
            retry_list.append(w)
        next_word()

    def next_word():
        # Passe au mot suivant ou recommence les mots non maîtrisés
        if idx + 1 < len(current_list):
            show_word(idx + 1)
        else:
            if retry_list:
                messagebox.showinfo("Renforcement", "Répétons les mots non maîtrisés !")
                current_list.clear()
                current_list.extend(retry_list)
                retry_list.clear()
                show_word(0)
            else:
                record_session_completion(session_number)
                messagebox.showinfo("Fini", "Session terminée avec succès !")
                root.destroy()

    # Liaison des boutons aux fonctions
    btn_show.config(command=reveal)
    btn_known.config(command=lambda: feedback("Je connais"))
    btn_fuzzy.config(command=lambda: feedback("Je suis incertain"))
    btn_unknown.config(command=lambda: feedback("Je ne connais pas"))

    # Démarrage de la session ou message si aucun mot
    if current_list:
        show_word(0)
    else:
        messagebox.showinfo("Info", "Aucun mot pour cette session.")
        root.destroy()

    root.mainloop()
    wb.save_csv(CSV_FILE)

if __name__ == '__main__':
    main()
