import tkinter as tk
from tkinter import simpledialog, messagebox
from tabulate import tabulate  # Pour un affichage formaté dans la console
import json
import os


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Builder")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.save_file = "graph_data.json"  # Fichier pour sauvegarder l'état
        self.nodes = {}
        self.connections = []
        self.dragged_node = None
        self.selected_node = None

        # Charger l'état précédent
        self.load_state()

        # Liaisons d'événements
        self.canvas.bind("<Button-1>", self.select_node)  # Sélection ou déplacement de nœuds
        self.canvas.bind("<B1-Motion>", self.move_node)  # Déplacer un nœud
        self.canvas.bind("<ButtonRelease-1>", self.release_node)  # Relâcher le nœud
        self.canvas.bind("<Double-Button-1>", self.add_node)  # Double clic gauche pour ajouter un nœud
        self.canvas.bind("<Button-3>", self.create_connection)  # Clic droit pour créer une connexion
        self.canvas.bind("<Shift-Button-1>", self.delete_node)  # Shift + clic gauche pour supprimer un nœud
        self.canvas.bind("<Shift-Button-3>", self.delete_connection)  # Shift + clic droit pour supprimer une connexion

        # Boutons pour gérer le graphe
        self.show_connections_button = tk.Button(
            root, text="Afficher les connexions", command=self.show_connections
        )
        self.show_connections_button.pack(pady=5)

        self.save_button = tk.Button(
            root, text="Enregistrer", command=self.save_state
        )
        self.save_button.pack(pady=5)

        self.redraw_nodes()

    def load_state(self):
        """Charge l'état des nœuds et connexions depuis un fichier JSON."""
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as file:
                data = json.load(file)
                self.nodes = data.get("nodes", {})
                self.connections = data.get("connections", [])
                print("État chargé depuis le fichier.")

    def save_state(self):
        """Sauvegarde l'état des nœuds et connexions dans un fichier JSON."""
        data = {
            "nodes": self.nodes,
            "connections": self.connections
        }
        with open(self.save_file, "w") as file:
            json.dump(data, file, indent=4)
        print("État sauvegardé.")

    def redraw_nodes(self):
        """Efface et redessine tous les nœuds."""
        self.canvas.delete("all")
        for name, (x, y) in self.nodes.items():
            self.draw_node(name, x, y)
        self.redraw_connections()

    def draw_node(self, name, x, y):
        """Dessine un nœud avec un cercle et un texte."""
        radius = 20
        self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill="lightblue", outline="black", tags=name
        )
        self.canvas.create_text(x, y, text=name, font=("Arial", 10, "bold"), tags=name)

    def redraw_connections(self):
        """Redessine toutes les connexions."""
        for node1, node2 in self.connections:
            x1, y1 = self.nodes[node1]
            x2, y2 = self.nodes[node2]
            tag = f"conn-{node1}-{node2}"  # Identifiant unique pour la connexion
            self.canvas.create_line(
                x1, y1, x2, y2, arrow=tk.LAST, width=2, tags=(tag, "connection")
            )


    def find_node(self, x, y):
        """Trouve le nœud le plus proche des coordonnées (x, y)."""
        for name, (nx, ny) in self.nodes.items():
            if (nx - x) ** 2 + (ny - y) ** 2 <= 400:  # Rayon de 20 pixels
                return name
        return None

    def find_connection(self, event):
        """Trouve une connexion sous la souris."""
        items = self.canvas.find_withtag("connection")
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("conn-"):
                    _, node1, node2 = tag.split("-")
                    return node1, node2
        return None


    def select_node(self, event):
        """Prépare le déplacement d'un nœud."""
        self.dragged_node = self.find_node(event.x, event.y)

    def move_node(self, event):
        """Déplace un nœud sélectionné."""
        if self.dragged_node:
            self.nodes[self.dragged_node] = (event.x, event.y)
            self.redraw_nodes()

    def release_node(self, event):
        """Arrête le déplacement d'un nœud."""
        if self.dragged_node:
            print(f"Nœud '{self.dragged_node}' déplacé à ({event.x}, {event.y}).")
            self.dragged_node = None

    def add_node(self, event):
        """Ajoute un nouveau nœud à la position du double-clic."""
        node_name = simpledialog.askstring("Nom du nœud", "Entrez le nom du nœud :")
        if not node_name or node_name in self.nodes:
            return  # Annuler si le nom est vide ou déjà utilisé
        self.nodes[node_name] = (event.x, event.y)
        print(f"Nœud '{node_name}' ajouté à ({event.x}, {event.y}).")
        self.redraw_nodes()

    def create_connection(self, event):
        """Crée une connexion entre deux nœuds."""
        clicked_node = self.find_node(event.x, event.y)
        if clicked_node:
            if self.selected_node is None:
                self.selected_node = clicked_node
                print(f"Nœud sélectionné : {clicked_node}")
            else:
                if self.selected_node != clicked_node:
                    self.connections.append((self.selected_node, clicked_node))
                    print(f"Connexion ajoutée : from {self.selected_node} to {clicked_node}")
                self.selected_node = None
                self.redraw_nodes()

    def delete_node(self, event):
        """Supprime un nœud et toutes ses connexions associées."""
        clicked_node = self.find_node(event.x, event.y)
        if clicked_node:
            self.nodes.pop(clicked_node)
            self.connections = [
                conn for conn in self.connections if clicked_node not in conn
            ]
            print(f"Nœud '{clicked_node}' supprimé.")
            self.redraw_nodes()

    def delete_connection(self, event):
        """Supprime uniquement la dernière connexion effectuée sur le nœud visé."""
        clicked_node = self.find_node(event.x, event.y)  # Trouver le nœud sous le curseur
        if clicked_node:
            # Trouver les connexions où le nœud visé est impliqué
            related_connections = [
                conn for conn in self.connections if clicked_node in conn
            ]
            if related_connections:
                # Supprimer la dernière connexion ajoutée parmi les connexions associées
                last_connection = related_connections[-1]
                self.connections.remove(last_connection)
                print(f"Connexion supprimée : from {last_connection[0]} to {last_connection[1]}")
                self.redraw_nodes()  # Redessiner les nœuds et connexions

    def show_connections(self):
        """Affiche toutes les connexions sous forme tabulaire."""
        if self.connections:
            headers = ["from", "to"]
            print(tabulate(self.connections, headers=headers, tablefmt="plain", showindex=True))
            connections_text = tabulate(self.connections, headers=headers, tablefmt="plain", showindex=True)
            messagebox.showinfo("Liste des connexions", connections_text)
        else:
            messagebox.showinfo("Liste des connexions", "Aucune connexion.")


# Lancer l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
