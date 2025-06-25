import tkinter as tk
from ui.selector_perfil import iniciar_selector

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Selector de Perfil")
    iniciar_selector(root)
    root.mainloop()
