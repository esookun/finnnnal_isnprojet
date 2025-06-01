from VISUEL import *
def main():
    """
    Usage :
    Lance l'application graphique de révision et gère la logique de session.
    """
    CSV_FILE, session_number = load_session_info()
    wb = WordBank.load_csv(CSV_FILE)
    wb.increment_days()
    today_words = wb.get_words_for_session(session_number)
    current_list = today_words.copy()
    retry_list = []
    first_feedback = []  # tuples (Word, 'Incertain'/'NonConnu')

    root = tk.Tk()
    root.title(f"Session {session_number}")

    eng_var, fr_var, prog_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
    label_eng = tk.Label(root, textvariable=eng_var, font=("Arial", 22))
    label_fr  = tk.Label(root, textvariable=fr_var,  font=("Arial", 14))
    label_prog= tk.Label(root, textvariable=prog_var,font=("Arial", 10))
    btn_show   = tk.Button(root, text="Afficher la signification", width=25, height=2)
    btn_known  = tk.Button(root, text="Mot facile", width=25, height=2)
    btn_fuzzy  = tk.Button(root, text="Mot moyen", width=25, height=2)
    btn_unknown= tk.Button(root, text="Mot difficile", width=25, height=2)

    label_eng.grid(row=0, column=0, columnspan=3, pady=10)
    label_fr.grid(row=1, column=0, columnspan=3, pady=5)
    btn_known.grid(row=3, column=0, padx=5, pady=10)
    btn_fuzzy.grid(row=3, column=1, padx=5, pady=10)
    btn_unknown.grid(row=3, column=2, padx=5, pady=10)
    label_prog.grid(row=4, column=0, columnspan=3, pady=5)

    idx = 0

    def show_word(i):
        nonlocal idx
        w = current_list[i]
        eng_var.set(w.english)
        fr_var.set("")
        btn_show.grid(row=2, column=0, columnspan=3, pady=5)
        btn_show.config(state=tk.NORMAL)
        idx = i
        prog_var.set(f"Mot {i+1}/{len(current_list)}")

    def reveal():
        fr_var.set(current_list[idx].french)
        btn_show.config(state=tk.DISABLED)

    def feedback(response):
        w = current_list[idx]
        if response != 'Mot facile' and all(w is not fb[0] for fb in first_feedback):
            val = 'En cours' if response == 'Mot moyen' else 'Non Connu'
            first_feedback.append((w, val))
        if response == 'Mot facile':
            w.mastery = 'Connu'
            w.times += 1
            w.days_since = 0
        elif response == 'Mot moyen':
            w.mastery = 'En cours'
            retry_list.append(w)
        else:
            w.mastery = 'Non connu'
            retry_list.append(w)
        next_word()

    def next_word():
        nonlocal idx
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
                increment_state_day()
                messagebox.showinfo("Fini", "Session terminée avec succès !")
                root.destroy()

    btn_show.config(command=reveal)
    btn_known.config(command=lambda: feedback("Mot facile"))
    btn_fuzzy.config(command=lambda: feedback("Mot moyen"))
    btn_unknown.config(command=lambda: feedback("Mot difficile"))

    if current_list:
        show_word(0)
    else:
        messagebox.showinfo("Info", "Aucun mot pour cette session.")
        increment_state_day()
        root.destroy()

    root.mainloop()

    for w, val in first_feedback:
        w.mastery = val
    wb.save_csv(CSV_FILE)

if __name__ == '__main__':
    main()
