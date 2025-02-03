import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import sys

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('(\d+)', s)]

def renommer_fichiers(chemin_dossier, nom_base, debut_numero, saisonact, custom_zero_enabled, longueur_zero):
    try:
        fichiers = os.listdir(chemin_dossier)
        fichiers.sort(key=natural_sort_key)

        nombre_total_fichiers = len(fichiers)
        zero_padding = longueur_zero if custom_zero_enabled else len(str(debut_numero + nombre_total_fichiers - 1))

        global historique_noms
        original_new_names = []
        buffer = []

        for index, fichier in enumerate(fichiers):
            extension = os.path.splitext(fichier)[1]
            numero_actuel = debut_numero + index
            if saisonact:
                nouveau_nom = f"{nom_base} - {saisonact}E{numero_actuel:0{zero_padding}d}{extension}"
            else:
                nouveau_nom = f"{nom_base} - E{numero_actuel:0{zero_padding}d}{extension}"
            ancien_chemin = os.path.join(chemin_dossier, fichier)
            nouveau_chemin = os.path.join(chemin_dossier, nouveau_nom)
            
            if os.path.exists(nouveau_chemin):
                buffer.append((ancien_chemin, nouveau_chemin))
                continue
            
            os.rename(ancien_chemin, nouveau_chemin)
            print(f"Renommé '{fichier}' en '{nouveau_nom}'")
            original_new_names.append((nouveau_chemin, ancien_chemin))
        
        while buffer:
            retry_buffer = []
            for ancien_chemin, nouveau_chemin in buffer:
                if not os.path.exists(nouveau_chemin):
                    os.rename(ancien_chemin, nouveau_chemin)
                    print(f"Renommé (de la mémoire tampon) '{os.path.basename(ancien_chemin)}' en '{os.path.basename(nouveau_chemin)}'")
                    original_new_names.append((nouveau_chemin, ancien_chemin))
                else:
                    retry_buffer.append((ancien_chemin, nouveau_chemin))
            if len(retry_buffer) == len(buffer):  # No progress made
                break
            buffer = retry_buffer

        if buffer:
            print("\n=== Certains fichiers n'ont pas pu être renommés à cause de conflits persistants ===\n")
            for ancien_chemin, nouveau_chemin in buffer:
                print(f"Impossible de renommer '{os.path.basename(ancien_chemin)}', conflit persistant avec '{os.path.basename(nouveau_chemin)}'")

        historique_noms.append(original_new_names)
        
        print("\n=== Renommage terminé ===\n")
        messagebox.showinfo("Succès", "Les fichiers ont été renommés avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

def revert_names():
    if not historique_noms:
        messagebox.showinfo("Info", "Aucun historique de renommage disponible.")
        return

    try:
        original_new_names = historique_noms.pop()
        buffer = []

        for new_name, original_name in original_new_names:
            if os.path.exists(original_name):
                buffer.append((new_name, original_name))
                continue
            
            os.rename(new_name, original_name)
            print(f"Retour de '{os.path.basename(new_name)}' à '{os.path.basename(original_name)}'")
        
        while buffer:
            retry_buffer = []
            for new_name, original_name in buffer:
                if not os.path.exists(original_name):
                    os.rename(new_name, original_name)
                    print(f"Retour (de la mémoire tampon) de '{os.path.basename(new_name)}' à '{os.path.basename(original_name)}'")
                else:
                    retry_buffer.append((new_name, original_name))
            if len(retry_buffer) == len(buffer):  # No progress made
                break
            buffer = retry_buffer

        if buffer:
            print("\n=== Certains fichiers n'ont pas pu être restaurés à cause de conflits persistants ===\n")
            for new_name, original_name in buffer:
                print(f"Impossible de restaurer '{os.path.basename(new_name)}', conflit persistant avec '{os.path.basename(original_name)}'")

        print("\n=== Restauration terminée ===\n")
        messagebox.showinfo("Succès", "Les fichiers ont été restaurés à leurs noms précédents.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la restauration : {e}")

def choisir_dossier():
    chemin = filedialog.askdirectory()
    if chemin:
        dossier_var.set(chemin)
        update_preview()

def lancer_renommage():
    chemin_dossier = dossier_var.get()
    nom_base = nom_serie_entry.get()
    try:
        debut_numero = int(numero_debut_entry.get())
    except ValueError:
        messagebox.showerror("Erreur", "Le numéro de début doit être un entier.")
        return
    saisonact = saison_entry.get()
    if saisonact == placeholders[saison_entry]:
        saisonact = ''
    custom_zero_enabled = custom_zero_var.get()
    try:
        longueur_zero = int(longueur_zero_entry.get())
    except ValueError:
        longueur_zero = 1  # Default if invalid input

    if not chemin_dossier or not nom_base or \
       nom_serie_entry.get() == placeholders[nom_serie_entry] or \
       numero_debut_entry.get() == placeholders[numero_debut_entry]:
        messagebox.showerror("Erreur", "Tous les champs doivent être remplis sauf la saison qui est optionnelle.")
        return

    renommer_fichiers(chemin_dossier, nom_base, debut_numero, saisonact, custom_zero_enabled, longueur_zero)

def set_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg='grey')
    entry.bind("<FocusIn>", lambda event: clear_placeholder(event, placeholder))
    entry.bind("<FocusOut>", lambda event: add_placeholder(event.widget, placeholder))

def clear_placeholder(event, placeholder):
    if event.widget.get() == placeholder:
        event.widget.delete(0, tk.END)
        event.widget.config(fg='black')

def add_placeholder(entry, placeholder):
    if entry.get() == '':
        entry.insert(0, placeholder)
        entry.config(fg='grey')

def update_preview(*args):
    chemin_dossier = dossier_var.get()
    nom_base = nom_serie_entry.get()
    try:
        debut_numero = int(numero_debut_entry.get())
    except ValueError:
        debut_numero = 1
    saisonact = saison_entry.get()
    if saisonact == placeholders[saison_entry]:
        saisonact = ''
    custom_zero_enabled = custom_zero_var.get()
    try:
        longueur_zero = int(longueur_zero_entry.get())
    except ValueError:
        longueur_zero = 1  # Default length if invalid

    if chemin_dossier and nom_base and \
       nom_serie_entry.get() != placeholders[nom_serie_entry] and \
       numero_debut_entry.get() != placeholders[numero_debut_entry]:
        try:
            fichiers = os.listdir(chemin_dossier)
            nombre_total_fichiers = len(fichiers)
            zero_padding = longueur_zero if custom_zero_enabled else len(str(debut_numero + nombre_total_fichiers - 1))

            if saisonact:
                preview_nom = f"{nom_base} - {saisonact}E{debut_numero:0{zero_padding}d}.ext"
            else:
                preview_nom = f"{nom_base} - E{debut_numero:0{zero_padding}d}.ext"
        except Exception as e:
            preview_nom = "Erreur de prévisualisation"
        
        preview_label.config(text=f"Prévisualisation: {preview_nom}")
    else:
        preview_label.config(text="Prévisualisation: ")

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

# Création de l'interface graphique
root = tk.Tk()
root.title("Renommage de fichiers")

# Variables
dossier_var = tk.StringVar()
dossier_var.trace_add("write", update_preview)
custom_zero_var = tk.IntVar()  # Variable for custom zero length toggle

historique_noms = []

# Widgets
nom_serie_entry = tk.Entry(root)
numero_debut_entry = tk.Entry(root)
saison_entry = tk.Entry(root)
longueur_zero_entry = tk.Entry(root)

# Placeholders
placeholders = {
    nom_serie_entry: "ex: Demon Slayer",
    numero_debut_entry: "ex: 1",
    saison_entry: "ex: S01",
    longueur_zero_entry: "Nombre total de zéros (ex: 3)"
}

# Set placeholders and attach events
set_placeholder(nom_serie_entry, placeholders[nom_serie_entry])
set_placeholder(numero_debut_entry, placeholders[numero_debut_entry])
set_placeholder(saison_entry, placeholders[saison_entry])
set_placeholder(longueur_zero_entry, placeholders[longueur_zero_entry])

# Bind entries to refresh preview instantly
nom_serie_entry.bind("<KeyRelease>", update_preview)
numero_debut_entry.bind("<KeyRelease>", update_preview)
saison_entry.bind("<KeyRelease>", update_preview)
longueur_zero_entry.bind("<KeyRelease>", update_preview)

choisir_dossier_btn = tk.Button(root, text="Choisir Dossier", command=choisir_dossier)
choisir_dossier_btn.grid(row=0, column=0, padx=10, pady=10)

dossier_label = tk.Label(root, textvariable=dossier_var)
dossier_label.grid(row=0, column=1, padx=10, pady=10)

nom_serie_label = tk.Label(root, text="Nom de la série :")
nom_serie_label.grid(row=1, column=0, padx=10, pady=10)
nom_serie_entry.grid(row=1, column=1, padx=10, pady=10)

numero_debut_label = tk.Label(root, text="Numéro de début :")
numero_debut_label.grid(row=2, column=0, padx=10, pady=10)
numero_debut_entry.grid(row=2, column=1, padx=10, pady=10)

saison_label = tk.Label(root, text="Saison :")
saison_label.grid(row=3, column=0, padx=10, pady=10)
saison_entry.grid(row=3, column=1, padx=10, pady=10)

custom_zero_checkbox = tk.Checkbutton(root, text="Activer longueur de zéro personnalisée", variable=custom_zero_var, command=update_preview)
custom_zero_checkbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

longueur_zero_label = tk.Label(root, text="Longueur des zéros :")
longueur_zero_label.grid(row=5, column=0, padx=10, pady=10)
longueur_zero_entry.grid(row=5, column=1, padx=10, pady=10)

lancer_btn = tk.Button(root, text="Lancer le renommage", command=lancer_renommage)
lancer_btn.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

revert_btn = tk.Button(root, text="Revenir aux noms initiaux", command=revert_names)
revert_btn.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

# Prévisualisation
preview_label = tk.Label(root, text="Prévisualisation: ")
preview_label.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

# Zone de texte pour les logs avec scrollbar
log_frame = tk.Frame(root)
log_frame.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

log_text = tk.Text(log_frame, height=10, wrap='word')
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

log_text.config(yscrollcommand=scrollbar.set)

# Rediriger stdout vers la zone de texte
sys.stdout = RedirectText(log_text)

root.mainloop()

# Restaurer stdout à sa valeur d'origine
sys.stdout = sys.__stdout__
