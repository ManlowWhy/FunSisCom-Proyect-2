# ranking.py
import tkinter as tk
import json
import os
from ui.selector_perfil import iniciar_selector
from ui.pantalla_juego import iniciar_juego

RANKING_FILE = "rankings.json"

def mostrar_ranking(root, jugador, avatar):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Ranking de Puntajes")
    tk.Label(root, text="🏆 Ranking de Jugadores", font=("Arial", 16, "bold")).pack(pady=10)

    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r') as f:
            data = json.load(f)
        ranking = sorted(data.items(), key=lambda x: x[1], reverse=True)
    else:
        ranking = []

    for nombre, puntaje in ranking:
        tk.Label(root, text=f"{nombre}: {puntaje} sets", font=("Arial", 12)).pack()

    tk.Label(root, text="\n¿Deseas continuar?", font=("Arial", 12)).pack(pady=10)

    botones = tk.Frame(root)
    botones.pack(pady=5)

    tk.Button(botones, text="Jugar con el mismo perfil",
              command=lambda: iniciar_juego(root, jugador, avatar)).grid(row=0, column=0, padx=10)
    tk.Button(botones, text="Elegir otro perfil",
              command=lambda: iniciar_selector(root)).grid(row=0, column=1, padx=10)
