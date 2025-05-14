import tkinter as tk
from tkinter import messagebox

operando1 = None
operador = None
resetear_entrada = False

def ingresar_numero(entrada, numero):
    global resetear_entrada
    if resetear_entrada:
        entrada.delete(0, tk.END)
        resetear_entrada = False
    entrada.insert(tk.END, str(numero))

def ingresar_operador(entrada, op):
    global operando1, operador, resetear_entrada
    if entrada.get() == "":
        messagebox.showerror("Error", "Por favor ingrese un número antes de seleccionar un operador")
        return
    if operando1 is None:
        operando1 = float(entrada.get())
        operador = op
        resetear_entrada = True
    else:
        calcular(entrada)
    operador = op
    resetear_entrada = True

def factorial(n):
    if n < 0:  
        messagebox.showerror("Error", "El factorial no está definido para números negativos")
        return None
    elif n == 0 or n == 1:  
        return 1
    else:
        return n * factorial(n - 1)

def calcular(entrada):
    global operando1, operador, resetear_entrada
    if operador and operando1 is not None:
        try:
            if operador == '!':
                if operando1.is_integer() and operando1 >= 0:
                    resultado = factorial(int(operando1))
                else:
                    messagebox.showerror("Error", "El factorial solo está definido para enteros no negativos")
                    return
            else:
                operando2 = float(entrada.get())
                if operador == '+':
                    resultado = operando1 + operando2
                elif operador == '-':
                    resultado = operando1 - operando2
                elif operador == '*':
                    resultado = operando1 * operando2
                elif operador == '/':
                    if operando2 == 0:
                        messagebox.showerror("Error", "División por cero no permitida")
                        return
                    resultado = operando1 / operando2
                elif operador == '^':
                    resultado = operando1 ** operando2
                else:
                    resultado = 0

            entrada.delete(0, tk.END)
            entrada.insert(tk.END, str(resultado))
            resetear_entrada = True
            operando1 = None
            operador = None
        except ValueError:
            messagebox.showerror("Error", "Entrada no válida")

def borrar(entrada):
    entrada.delete(0, tk.END)

def borrar_todo(entrada):
    global operando1, operador, resetear_entrada
    entrada.delete(0, tk.END)
    operando1 = None
    operador = None
    resetear_entrada = False