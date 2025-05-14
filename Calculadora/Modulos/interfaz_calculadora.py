import tkinter as tk
from Modulos.logica_calculadora import ingresar_numero, ingresar_operador, calcular, borrar, borrar_todo
def crear_interfaz(root):
    entrada = tk.Entry(root, font=("Arial", 24), bg="#2E2E2E", fg="white")
    entrada.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    botones = [
        ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
        ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
        ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
        ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
        ("CE", 5, 0), ("C", 5, 1), ("^", 5, 2), ("!", 5, 3),
    ]

    for (text, row, col) in botones:
        if text.isdigit() or text == ".":
            cmd = lambda t=text: ingresar_numero(entrada, t)
        elif text in "+-*/^!":
            cmd = lambda t=text: ingresar_operador(entrada, t)
        elif text == "=":
            cmd = lambda: calcular(entrada)
        elif text == "C":
            cmd = lambda: borrar(entrada)
        elif text == "CE":
            cmd = lambda: borrar_todo(entrada)

        boton = tk.Button(root, text=text, width=5, height=2, bg="#4B4B4B", fg="white", font=("Arial", 20), command=cmd)
        boton.grid(row=row, column=col)