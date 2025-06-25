# pantalla_juego.py
import tkinter as tk
from PIL import Image, ImageTk
import threading
import json
import socket
import os
import pygame

RANKING_FILE = "rankings.json"
PORT = 8001

# Reproductor de música de fondo
pygame.mixer.init()
def reproducir_musica():
    try:
        pygame.mixer.music.load("music/fondo.mp3")
        pygame.mixer.music.play(-1)
    except:
        print("🎵 Música no disponible")

# Guardar ranking actualizado
def guardar_ranking(nombre, puntaje):
    if os.path.exists(RANKING_FILE):
        with open(RANKING_FILE, 'r') as f:
            ranking = json.load(f)
    else:
        ranking = {}
    if nombre not in ranking or puntaje > ranking[nombre]:
        ranking[nombre] = puntaje
        with open(RANKING_FILE, 'w') as f:
            json.dump(ranking, f, indent=2)

# Pantalla principal de juego
def iniciar_juego(root, nombre, avatar):
    root.title("Juego en Progreso")
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=f"Jugador: {nombre}", font=("Arial", 16)).pack(pady=10)

    try:
        img = Image.open(f"avatars/{avatar}")
        img = img.resize((80, 80))
        tk_img = ImageTk.PhotoImage(img)
        tk.Label(root, image=tk_img).pack()
        root.tk_img = tk_img
    except:
        pass

    puntaje_var = tk.StringVar()
    puntaje_var.set("Puntaje: 0")
    tk.Label(root, textvariable=puntaje_var, font=("Arial", 20)).pack(pady=20)

    reproducir_musica()

    # Hilo que escucha la Pico
    def escuchar():
        server = socket.socket()
        server.bind(("0.0.0.0", PORT))
        server.listen(1)
        print(f"🖥️ Esperando datos en el puerto {PORT}...")

        max_puntaje = 0

        while True:
            conn, addr = server.accept()
            data = conn.recv(1024).decode()
            try:
                obj = json.loads(data)
                puntaje = obj.get("set_count", 0)
                puntaje_var.set(f"Puntaje: {puntaje}")
                print("📩 Puntaje recibido:", puntaje)
                if puntaje > max_puntaje:
                    max_puntaje = puntaje
                conn.send(b"Recibido")
            except:
                print("❌ Error al interpretar mensaje")
            conn.close()

            if max_puntaje >= 15:
                guardar_ranking(nombre, max_puntaje)
                pygame.mixer.music.stop()
                break

    threading.Thread(target=escuchar, daemon=True).start()
