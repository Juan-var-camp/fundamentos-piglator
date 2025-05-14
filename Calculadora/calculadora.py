import tkinter as tk
from Modulos.interfaz_calculadora import crear_interfaz

def main():
    root = tk.Tk()
    root.title("Calculadora")
    root.geometry("400x600")
    root.resizable(False, False)
    root.config(bg="#2E2E2E")
    crear_interfaz(root)
    root.mainloop()

if __name__ == "__main__":
    main()