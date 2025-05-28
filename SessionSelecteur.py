import tkinter as tk
import csv
import subprocess
import sys
import math
import json
import os

SESSION_PROGRESS_FILE = "session_progress.json"

class SessionSelecteur(tk.Toplevel):
    def __init__(self, master, csv_path):
        super().__init__(master)
        self.title("🎯 Choisir une session")
        self.geometry("600x600")
        self.configure(bg="#f0f0f0")
        self.resizable(False, False)
        self.csv_path = csv_path

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                rows = [row for row in csv.reader(f) if any(cell.strip() for cell in row)]
            total_words = len(rows)
        except:
            total_words = 0

        self.levels = max(1, math.ceil(total_words / 5))
        self.completed = self.load_progress()
        self.create_ui()

    def load_progress(self):
        if os.path.exists(SESSION_PROGRESS_FILE):
            try:
                with open(SESSION_PROGRESS_FILE, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except:
                return set()
        return set()

    def save_progress(self):
        with open(SESSION_PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(self.completed), f, indent=2)

    def create_ui(self):
        tk.Label(self, text="Sélection de la session", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=(15, 10))

        grid_frame = tk.Frame(self, bg="#ffffff", bd=2, relief="ridge")
        grid_frame.pack(pady=10, padx=20, expand=True)

        cols = 6
        for i in range(self.levels):
            session_num = i + 1
            row = i // cols
            col = i % cols if row % 2 == 0 else cols - 1 - (i % cols)

            state = "disabled" if session_num in self.completed else "normal"
            btn = tk.Button(
                grid_frame, text=f"Session {session_num}", width=10, height=2, font=("Arial", 9, "bold"),
                bg="#ffffff", relief="raised", bd=1, state=state,
                activebackground="#d0e0ff",
                command=lambda n=session_num: self.start_level(n)
            )
            btn.grid(row=row, column=col, padx=6, pady=6)

        tk.Button(self, text="Fermer", command=self.destroy, font=("Arial", 10),
                  bg="#dddddd", relief="raised").pack(pady=(10, 15))

    def start_level(self, level_num):
        try:
            with open("level_info.txt", "w", encoding="utf-8") as f:
                f.write(f"{self.csv_path}\n{level_num}")
            subprocess.Popen([sys.executable, "MotFenetre.py"])
            self.completed.add(level_num)
            self.save_progress()
            self.destroy()
        except Exception as e:
            tk.messagebox.showerror("Erreur", f"Impossible de démarrer la session:\n{e}")