import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox

ventana_activa = None
usuario_actual = None

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

#Hace el inicio de la base datos y si esta no existe la crea
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL)
''')
conn.commit()

def centrar_ventana(ventana):
    ventana.update_idletasks()  # Asegura que las dimensiones de la ventana estén actualizadas
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry(f"{width}x{height}+{x}+{y}")

def change_password():
    popup_change_password = tk.Toplevel(ventana_activa)
    popup_change_password.title("Cambiar Contraseña")
    popup_change_password.grab_set()  # Bloquea la interacción con otras ventanas
    popup_change_password.transient(ventana_activa)  # Indica que es hija de la ventana principal

    tk.Label(popup_change_password, text="Contraseña actual").grid(row=0, column=0, padx=10, pady=5)
    entry_password = tk.Entry(popup_change_password, show="*")
    entry_password.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(popup_change_password, text="Nueva Contraseña").grid(row=1, column=0, padx=10, pady=5)
    entry_new_password = tk.Entry(popup_change_password, show="*")
    entry_new_password.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(popup_change_password, text="Confirmar Nueva Contraseña").grid(row=2, column=0, padx=10, pady=5)
    entry_password_confirmation = tk.Entry(popup_change_password, show="*")
    entry_password_confirmation.grid(row=2, column=1, padx=10, pady=5)
    
    popup_change_password.bind('<Return>', lambda e: actualizar_contraseña(entry_password, entry_new_password, entry_password_confirmation, popup_change_password))
    popup_change_password.bind('<Escape>', lambda e: popup_change_password.destroy())
    
    tk.Button(popup_change_password,text="Cancelar",command=popup_change_password.destroy).grid(row=3, column=0, pady=10)
    tk.Button(
        popup_change_password, 
        text="Confirmar", 
        command=lambda: actualizar_contraseña(entry_password, entry_new_password, entry_password_confirmation, popup_change_password)
    ).grid(row=3, column=1, padx=10, pady=5)
    
    centrar_ventana(popup_change_password)

def actualizar_contraseña(entry_password, entry_new_password, entry_password_confirmation, popup_change_password):
    global usuario_actual
    current_password = entry_password.get()
    new_password = entry_new_password.get()
    confirm_password = entry_password_confirmation.get()

    if not current_password or not new_password or not confirm_password:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    if new_password != confirm_password:
        messagebox.showerror("Error", "Las contraseñas no coinciden.")
        return

    if len(new_password) < 8:
        messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres.")
        return

    hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()
    cursor.execute("SELECT password FROM users WHERE id = ?", (usuario_actual,)) 
    resultado = cursor.fetchone()

    if not resultado or resultado[0] != hashed_current_password:
        messagebox.showerror("Error", "La contraseña actual es incorrecta.")
        return

    hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_new_password, usuario_actual))  # Cambia `id = 1` por el usuario actual
    conn.commit()
    messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
    popup_change_password.destroy()

def change_username():
    popup_change_username = tk.Toplevel(ventana_activa)
    popup_change_username.title("Cambiar Nombre de Usuario")
    popup_change_username.grab_set()  # Bloquea la interacción con otras ventanas
    popup_change_username.transient(ventana_activa)  # Indica que es hija de la ventana principal

    tk.Label(popup_change_username, text="Nuevo nombre de Usuario").grid(row=0, column=0, padx=10, pady=5)
    entry_new_username = tk.Entry(popup_change_username)
    entry_new_username.grid(row=0, column=1, padx=10, pady=5)
    
    popup_change_username.bind('<Return>', lambda e: actualizar_nombre_usuario(entry_new_username, popup_change_username))
    popup_change_username.bind('<Escape>', lambda e: popup_change_username.destroy())
    
    tk.Button(popup_change_username,text="Cancelar",command=popup_change_username.destroy).grid(row=3, column=0, pady=5)
    tk.Button(
        popup_change_username, 
        text="Confirmar", 
        command=lambda: actualizar_nombre_usuario(entry_new_username, popup_change_username)
    ).grid(row=3, column=1, padx=10, pady=5)
    
    centrar_ventana(popup_change_username)

def actualizar_nombre_usuario(entry_new_username, popup_change_username):
    global usuario_actual
    new_username = entry_new_username.get()
    if not new_username:
        messagebox.showerror("Error", "El campo de nombre de usuario no puede estar vacío.")
        return
    
    try:
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, usuario_actual))
        conn.commit()
        messagebox.showinfo("Éxito", "Nombre de usuario actualizado correctamente.")
        popup_change_username.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El nombre de usuario ya existe. Por favor, elige otro.")

def cerrar_ventana_activa():
    global ventana_activa
    if ventana_activa and ventana_activa.winfo_exists():
        ventana_activa.destroy()
        ventana_activa = None

def login_usuario(entry_user_login,entry_password_login,login_window):
    global usuario_actual
    username = entry_user_login.get()
    password = entry_password_login.get()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if not username or not password:
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return
    
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    resultado = cursor.fetchone()
    if resultado and resultado[1] == hashed_password:
        usuario_actual = resultado[0]  
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
    
    #Esta parte es para centrar la ventana emergente en la pantalla
    centrar_ventana(register_window)

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
    
    #Esta parte es para centrar la ventana emergente en la pantalla
    centrar_ventana(login_window)
    
def window_perfil():
    global ventana_activa
    cerrar_ventana_activa()
    ventana_activa = tk.Toplevel(root)
    ventana_activa.title("Configuracion de perfil")
    ventana_activa.state("zoomed")
    
    ventana_activa.grid_columnconfigure(1, weight=1)
    ventana_activa.grid_rowconfigure(0, weight=1)
    
    sidebar = tk.Frame(ventana_activa, bg="#2C3E50", width=200)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_rowconfigure(3, weight=1)
    
    content = tk.Frame(ventana_activa, bg="#ECF0F1")
    content.grid(row=0, column=1, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)
    
    #Botones de la barra lateral
    #Se le asigna la funcion de abrir la ventana correspondiente a cada boton
    buttom_perfil = tk.Button(sidebar, text="perfil", width=15)
    buttom_gastos = tk.Button(sidebar, text="gastos", width=15, command=ventana_principal)
    buttom_ganancias = tk.Button(sidebar, text="ganancias", width=15, command=window_ganancias)

    #Distribucion de los botones en la barra lateral
    buttom_perfil.grid(row=0, column=0, pady=10, padx=10, sticky="w")
    buttom_gastos.grid(row=1, column=0, pady=10, padx=10, sticky="w")
    buttom_ganancias.grid(row=2, column=0, pady=10, padx=10, sticky="w")
    
    center_container = tk.Frame(content, bg="#ECF0F1")
    center_container.place(relx=0.5, rely=0.5, anchor="center")
    
    profile_frame = tk.Frame(center_container, bg="#8B0000", padx=20, pady=20, relief="solid", borderwidth=2)
    profile_frame.pack()
    
    tk.Label(profile_frame, text="Configuración del perfil", font=("Arial", 20), bg="#8B0000", fg="white").pack(pady=10)
    tk.Label(profile_frame, text=f"Bienvenido usuario, {usuario_actual}", font=("Arial", 14), bg="#8B0000", fg="white").pack(pady=10)
    
    buttom_change_u = tk.Button(profile_frame, text="Cambiar nombre de usuario", width=25, relief="solid", borderwidth=1, command=change_username)
    buttom_change_u.pack(pady=10)
    
    buttom_change_p = tk.Button(profile_frame, text="Cambiar contraseña", width=25, relief="solid", borderwidth=1, command=change_password)
    buttom_change_p.pack(pady=10)
    
    ventana_activa.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))
    
def window_ganancias():
    global ventana_activa
    cerrar_ventana_activa()
    ventana_activa = tk.Toplevel(root)
    ventana_activa.title("Ganancias")
    ventana_activa.state("zoomed")
    
    ventana_activa.grid_columnconfigure(1, weight=1)
    ventana_activa.grid_rowconfigure(0, weight=1)
    
    sidebar = tk.Frame(ventana_activa, bg="#2C3E50", width=200)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_rowconfigure(3, weight=1)
    
    content = tk.Frame(ventana_activa, bg="#ECF0F1")
    content.grid(row=0, column=1, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)
    
    buttom_perfil = tk.Button(sidebar, text="perfil", width=15, command=window_perfil)
    buttom_gastos = tk.Button(sidebar, text="gastos", width=15, command=ventana_principal)
    buttom_ganancias = tk.Button(sidebar, text="ganancias", width=15)
    
    buttom_perfil.grid(row=0, column=0, pady=10, padx=10, sticky="w")
    buttom_gastos.grid(row=1, column=0, pady=10, padx=10, sticky="w")
    buttom_ganancias.grid(row=2, column=0, pady=10, padx=10, sticky="w")
    
    label = tk.Label(content, text="Las ganancias", font=("Arial", 20))
    label.grid(row=0, column=0, pady=50)
    
    ventana_activa.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))
    
def ventana_principal():
    global ventana_activa
    cerrar_ventana_activa()
    ventana_activa = tk.Toplevel(root)
    ventana_activa.title("Ventana principal")
    ventana_activa.state("zoomed")
    
    ventana_activa.grid_columnconfigure(1, weight=1)
    ventana_activa.grid_rowconfigure(0, weight=1)
    
    sidebar = tk.Frame(ventana_activa, bg="#2C3E50", width=200)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_rowconfigure(3, weight=1)
    
    # Crear frames para el contenido principal dividido
    content_left = tk.Frame(ventana_activa, bg="#ECF0F1", relief="solid", borderwidth=1)
    content_left.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    
    content_right = tk.Frame(ventana_activa, bg="#ECF0F1", relief="solid", borderwidth=1)
    content_right.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
    
    # Configurar pesos de las columnas para el contenido
    ventana_activa.grid_columnconfigure(1, weight=1)
    ventana_activa.grid_columnconfigure(2, weight=1)
    
    buttom_perfil = tk.Button(sidebar, text="perfil", width=15, command=window_perfil)
    buttom_gastos = tk.Button(sidebar, text="gastos", width=15)
    buttom_ganancias = tk.Button(sidebar, text="ganancias", width=15, command=window_ganancias)
    
    buttom_perfil.grid(row=0, column=0, pady=10, padx=10, sticky="w")
    buttom_gastos.grid(row=1, column=0, pady=10, padx=10, sticky="w")
    buttom_ganancias.grid(row=2, column=0, pady=10, padx=10, sticky="w")
    
 # Títulos para los paneles de contenido
    tk.Label(content_left, text="Panel Izquierdo", font=("Arial", 16), bg="#ECF0F1").pack(pady=20)
    tk.Label(content_right, text="Panel Derecho", font=("Arial", 16), bg="#ECF0F1").pack(pady=20)
    
    ventana_activa.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root)) 
    
def cerrar_aplicacion(ventana_root):
    conn.close()# Cierra la conexión a la base de datos
    ventana_root.destroy()# Destruye la raíz para cerrar la app
    
#Se crea una ventana raiz oculta para que el resto de ventanas sean una toplevel de esta
root = tk.Tk()
root.withdraw()

#Se crea el menu principal
menu_principal = tk.Toplevel(root)
menu_principal.title("Ventana del menu de inicio")
menu_principal.state("zoomed")

boton_register = tk.Button(menu_principal, text="Registrarse", width=15, height=2)
boton_login = tk.Button(menu_principal, text="Iniciar sesion", width=15, height=2)

boton_register.place(relx=0.5, rely=0.46, anchor="center")
boton_login.place(relx=0.5, rely=0.54, anchor="center")      
boton_register.config(command=open_window_register)
boton_login.config(command=open_window_login)

menu_principal.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))
root.mainloop() 