# selector_perfil.py
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import cv2
from ui.pantalla_juego import iniciar_juego



PROFILES_FILE = "profiles.json"
AVATAR_FOLDER = "avatars"

perfiles = []

# Cargar perfiles existentes
def cargar_perfiles():
    global perfiles
    if os.path.exists(PROFILES_FILE):
        with open(PROFILES_FILE, 'r') as f:
            perfiles = json.load(f)
    else:
        perfiles = []

# Guardar nuevo perfil
def guardar_perfiles():
    with open(PROFILES_FILE, 'w') as f:
        json.dump(perfiles, f, indent=2)

# Tomar foto con cámara y guardarla como avatar
def capturar_avatar(nombre):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ No se pudo acceder a la cámara")
        return None

    print("📸 Presioná 's' para capturar la imagen")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Presioná "s" para capturar', frame)
        key = cv2.waitKey(1)
        if key == ord('s'):
            avatar_path = os.path.join(AVATAR_FOLDER, f"{nombre}.png")
            cv2.imwrite(avatar_path, frame)
            break
    cap.release()
    cv2.destroyAllWindows()
    return f"{nombre}.png"

def iniciar_selector(root):
    cargar_perfiles()

    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    tk.Label(frame, text="Nombre del jugador:").grid(row=0, column=0)
    entry_nombre = tk.Entry(frame)
    entry_nombre.grid(row=0, column=1)

    def crear_perfil():
        nombre = entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return
        for p in perfiles:
            if p["nombre"] == nombre:
                messagebox.showerror("Error", "El nombre ya existe")
                return

        if not os.path.exists(AVATAR_FOLDER):
            os.makedirs(AVATAR_FOLDER)

        usar_camara = messagebox.askyesno("Avatar", "¿Deseás tomar una foto como avatar?")
        if usar_camara:
            avatar = capturar_avatar(nombre)
            if not avatar:
                messagebox.showerror("Error", "No se pudo capturar la imagen")
                return
        else:
            avatars = os.listdir(AVATAR_FOLDER)
            if not avatars:
                messagebox.showerror("Error", "No hay avatares disponibles")
                return
            avatar = avatars[0]  # usa el primero si no se elige otro

        perfiles.append({"nombre": nombre, "avatar": avatar})
        guardar_perfiles()
        iniciar_juego(root, nombre, avatar)

    def elegir_existente():
        if not perfiles:
            messagebox.showinfo("Info", "No hay perfiles registrados")
            return
        elegir_win = tk.Toplevel(root)
        elegir_win.title("Elegir Perfil")
        lb = tk.Listbox(elegir_win, width=30)
        lb.pack(padx=10, pady=10)
        for p in perfiles:
            lb.insert(tk.END, p["nombre"])

        def seleccionar():
            sel = lb.curselection()
            if not sel:
                return
            elegido = perfiles[sel[0]]
            elegir_win.destroy()
            iniciar_juego(root, elegido["nombre"], elegido["avatar"])

        tk.Button(elegir_win, text="Seleccionar", command=seleccionar).pack(pady=5)

    tk.Button(frame, text="Crear Perfil", command=crear_perfil).grid(row=2, column=0, pady=10)
    tk.Button(frame, text="Elegir Perfil", command=elegir_existente).grid(row=2, column=1, pady=10)
    tk.Button(frame, text="Ver Ranking", command=lambda: __ver_ranking(root)).grid(row=3, column=0, columnspan=2, pady=10)

def __ver_ranking(root):
    from ui.ranking import mostrar_ranking
    mostrar_ranking(root, "anonimo", "default.png")

