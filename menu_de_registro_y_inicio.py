import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

#Hace el inicio de la base datos y si esta no existe la crea
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL)
''')
conn.commit()

def login_usuario(entry_user_login,entry_password_login,login_window):
    username = entry_user_login.get()
    password = entry_password_login.get()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if not username or not password:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    resultado = cursor.fetchone()
    if resultado and resultado[0] == hashed_password:
        if resultado and resultado[0] == hashed_password:
            messagebox.showinfo("Felicidades", "Inicio de sesion exitoso")
            login_window.destroy()
            menu_principal.destroy()
            ventana_principal()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        

def registrar_usuario(entry_user_register, entry_password_register, entry_confirm_password_register,register_window):
    username = entry_user_register.get()
    password = entry_password_register.get()
    confirmation = entry_confirm_password_register.get()
    #Son los prevenciones para el registro
    if password != confirmation:
        messagebox.showerror("Error", "Las contraseñas no coinciden")
        return    
    if not username or not password or not confirmation:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    if len(password) < 8:
        messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres")
        return
      
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        messagebox.showinfo("Felicidades", "registro exitoso")
        register_window.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El usuario ya existe")

def open_window_register():
    register_window = tk.Toplevel(menu_principal)
    register_window.title("Registro de Usuario")
    register_window.grab_set()  # Bloquea la interacción con otras ventanas
    register_window.transient(menu_principal)  # Indica que es hija de la ventana principal

    tk.Label(register_window, text="Nombre de Usuario").grid(row=0, column=0, padx=10, pady=5)
    entry_user_register = tk.Entry(register_window)
    entry_user_register.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(register_window, text="Contraseña").grid(row=1, column=0, padx=10, pady=5)
    entry_password_register = tk.Entry(register_window, show="*")
    entry_password_register.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(register_window, text="Confirmar Contraseña").grid(row=2, column=0, padx=10, pady=5)
    entry_confirm_password_register = tk.Entry(register_window, show="*")
    entry_confirm_password_register.grid(row=2, column=1, padx=10, pady=5)
    
    register_window.bind('<Return>', lambda e: registrar_usuario(entry_user_register,entry_password_register,entry_confirm_password_register,register_window))
    register_window.bind('<Escape>', lambda e: register_window.destroy())
    
    tk.Button(register_window,text="Cancelar",command=register_window.destroy).grid(row=3, column=0, pady=5)
    boton_register = tk.Button(
        register_window, 
        text="Registrarse", 
        command=lambda: registrar_usuario(entry_user_register,entry_password_register,entry_confirm_password_register,register_window))
    boton_register.grid(row=3, column=1, padx=10, pady=5)

def open_window_login():
    login_window = tk.Toplevel(menu_principal)
    login_window.title("Inicio de sesion")
    login_window.grab_set()  # Bloquea la interacción con otras ventanas
    login_window.transient(menu_principal)  # Indica que es hija de la ventana principal

    tk.Label(login_window, text="Nombre de Usuario").grid(row=0, column=0, padx=10, pady=5)
    entry_user_login = tk.Entry(login_window)
    entry_user_login.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(login_window, text="Contraseña").grid(row=1, column=0, padx=10, pady=5)
    entry_password_login = tk.Entry(login_window, show="*")
    entry_password_login.grid(row=1, column=1, padx=10, pady=5)
    
    login_window.bind('<Return>', lambda e: login_usuario(entry_user_login,entry_password_login,login_window))
    login_window.bind('<Escape>', lambda e: login_window.destroy())
    
    tk.Button(login_window,text="Cancelar",command=login_window.destroy).grid(row=3, column=0, pady=5)
    boton_login = tk.Button(
        login_window, 
        text="Iniciar Sesion", 
        command= lambda: login_usuario(entry_user_login,entry_password_login,login_window))
    boton_login.grid(row=3, column=1, padx=10, pady=5)
    
def ventana_principal():
    ventana_principal = tk.Toplevel(root)
    ventana_principal.title("Ventana principal")
    ventana_principal.state("zoomed")
    ventana_principal.grid_columnconfigure(1, weight=1)
    ventana_principal.grid_rowconfigure(0, weight=1)
    sidebar = tk.Frame(ventana_principal, bg="#2C3E50", width=200)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_rowconfigure(3, weight=1)
    content = tk.Frame(ventana_principal, bg="#ECF0F1")
    content.grid(row=0, column=1, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)
    btn1 = tk.Button(sidebar, text="perfil", width=15)
    btn2 = tk.Button(sidebar, text="gastos", width=15)
    btn3 = tk.Button(sidebar, text="ganancias", width=15)
    btn1.grid(row=0, column=0, pady=10, padx=10, sticky="w")
    btn2.grid(row=1, column=0, pady=10, padx=10, sticky="w")
    btn3.grid(row=2, column=0, pady=10, padx=10, sticky="w")
    label = tk.Label(content, text="Cabrones", font=("Arial", 20))
    label.grid(row=0, column=0, pady=50)
    
def cerrar_aplicacion(ventana_root):
    conn.close()  # Cierra la conexión a la base de datos
    ventana_root.destroy()# Destruye la raíz para cerrar la app
    
#Se crea una ventana raiz oculta para que el resto de ventanas sean una toplevel de esta
root = tk.Tk()
root.withdraw()

#Se crea el menu principal
menu_principal = tk.Toplevel(root)
menu_principal.title("Ventana del menu de inicio")
menu_principal.state("zoomed")

#Se configura el grid del menu principal
menu_principal.grid_columnconfigure(0, weight=1)
menu_principal.grid_rowconfigure(0, weight=1)
menu_principal.grid_rowconfigure(1, weight=1)
menu_principal.grid_rowconfigure(2, weight=1)

boton_register = tk.Button(menu_principal, text="Registrarse", width=15)
boton_login = tk.Button(menu_principal, text="Iniciar sesion", width=15)

boton_register.grid(row=1, column=0, padx=10, pady=5)
boton_login.grid(row=2, column=0, padx=10, pady=5)
boton_register.config(command=open_window_register)
boton_login.config(command=open_window_login)

menu_principal.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))
menu_principal.mainloop()