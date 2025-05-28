import tkinter as tk
import csv
import subprocess
import sys
import math
import os

# Nombre de mots par session
SESSION_SIZE = 5

class SessionSelecteur(tk.Toplevel):
    def __init__(self, master, csv_path):
        super().__init__(master)
        self.title("🎯 Choisir une session")
        self.geometry("800x500")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)
        self.csv_path = csv_path

        # Lecture du nombre total de mots dans le CSV
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                rows = [row for row in csv.reader(f) if any(cell.strip() for cell in row)]
            total_words = len(rows)
        except:
            total_words = 0

        # Calcul du nombre de sessions nécessaires
        self.levels = max(1, math.ceil(total_words / SESSION_SIZE))
        self.create_ui()

    def is_session_mastered(self, session_num):
        """Retourne True si tous les mots de la session sont marqués 'Connait'"""
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                rows = [row for row in csv.reader(f) if any(cell.strip() for cell in row)]
        except:
            return False
        start = (session_num - 1) * SESSION_SIZE
        end = start + SESSION_SIZE
        session_rows = rows[start:end]
        if not session_rows:
            return False
        # Vérifie que la colonne 'mastery' est 'Connait' pour chaque mot
        return all(len(r) >= 3 and r[2].strip() == "Connait" for r in session_rows)

    def create_ui(self):
        # En-tête de la fenêtre
        tk.Label(self, text="Sélection de la session", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=(15, 10))

        # Cadre pour la grille des boutons
        grid_frame = tk.Frame(self, bg="#ffffff", bd=2, relief="ridge")
        grid_frame.pack(pady=10, padx=20, expand=True)

        cols = 6  # Nombre de colonnes
        for i in range(self.levels):
            session_num = i + 1
            row = i // cols
            col = i % cols if row % 2 == 0 else cols - 1 - (i % cols)

            # Désactive le bouton si la session est entièrement maîtrisée
            state = "disabled" if self.is_session_mastered(session_num) else "normal"

            btn = tk.Button(
                grid_frame,
                text=f"Session {session_num}",
                width=10, height=2,
                font=("Arial", 9, "bold"),
                bg="#ffffff", relief="raised", bd=1,
                state=state,
                activebackground="#d0e0ff",
                command=lambda n=session_num: self.start_level(n)
            )
            btn.grid(row=row, column=col, padx=6, pady=6)

        # Bouton pour fermer la fenêtre
        tk.Button(
            self,
            text="Fermer",
            command=self.destroy,
            font=("Arial", 10),
            bg="#dddddd",
            relief="raised"
        ).pack(pady=(10, 15))

    def start_level(self, level_num):
        try:
            # Écriture des informations de session dans un fichier
            with open("level_info.txt", "w", encoding="utf-8") as f:
                f.write(f"{self.csv_path}\n{level_num}")
            # Lancement du script de la fenêtre de mot
            subprocess.Popen([sys.executable, "MotFenetre.py"]);
            self.destroy()
        except Exception as e:
            tk.messagebox.showerror("Erreur", f"Impossible de démarrer la session:\n{e}")
