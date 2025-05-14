import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox

ventana_activa = None
usuario_actual = None
nombre_usuario = None

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

#Hace el inicio de la base datos y si esta no existe la crea
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL)
''')
conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS piaras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tamaño INTEGER NOT NULL,
    semanas INTEGER NOT NULL
)''')
conn.commit()

#Funciones auxiliares
def centrar_ventana(ventana):
    ventana.update_idletasks()  # Asegura que las dimensiones de la ventana estén actualizadas
    width = ventana.winfo_width()
    height = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (width // 2)
    y = (ventana.winfo_screenheight() // 2) - (height // 2)
    ventana.geometry(f"{width}x{height}+{x}+{y}")
def cerrar_ventana_activa():
    global ventana_activa
    if ventana_activa and ventana_activa.winfo_exists():
        ventana_activa.destroy()
        ventana_activa = None

#Funciones referentes a la base de datos
def actualizar_contraseña(entry_password, entry_new_password, entry_password_confirmation, popup):
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
    popup.destroy()
def actualizar_nombre_usuario(entry_new_username, popup, nombre_usuario_var):
    global usuario_actual, nombre_usuario
    new_username = entry_new_username.get()
    if not new_username:
        messagebox.showerror("Error", "El campo de nombre de usuario no puede estar vacío.")
        return
    
    try:
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, usuario_actual))
        conn.commit()
        nombre_usuario = new_username
        nombre_usuario_var.set(f"Bienvenido usuario, {nombre_usuario}")
        messagebox.showinfo("Éxito", "Nombre de usuario actualizado correctamente.")
        popup.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El nombre de usuario ya existe. Por favor, elige otro.")
def login_usuario(entry_user_login,entry_password_login,login_window):
    global usuario_actual, nombre_usuario
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
        nombre_usuario = username
        messagebox.showinfo("Felicidades", "Inicio de sesion exitoso")
        login_window.destroy()
        menu_principal.destroy()
        ventana_gastos()
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
def crear_piara(entry_nombre_piara, entry_tamaño_piara, entry_semanas_piara, popup):
    nombre_piara = entry_nombre_piara.get()
    tamaño_piara = entry_tamaño_piara.get()
    semanas_piara = entry_semanas_piara.get()

    if not nombre_piara or not tamaño_piara or not semanas_piara:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    try:
        tamaño_piara = int(tamaño_piara)
        semanas_piara = int(semanas_piara)
    except ValueError:
        messagebox.showerror("Error", "El tamaño y las semanas deben ser números enteros.")
        return

    try:
        cursor.execute("INSERT INTO piaras (nombre, tamaño, semanas) VALUES (?, ?, ?)", (nombre_piara, tamaño_piara, semanas_piara))
        conn.commit()
        messagebox.showinfo("Éxito", "Piara creada correctamente.")
        popup.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El nombre de la piara ya existe.")

#Funciones para el contenido de las ventanas
def contenido_ventana_gastos(content):
    # Configurar las columnas para que ocupen la mitad del espacio cada una
    content.grid_columnconfigure(0, weight=1)  # Primera columna (panel izquierdo)
    content.grid_columnconfigure(1, weight=1)  # Segunda columna (panel derecho)
    content.grid_rowconfigure(0, weight=1)    # Fila única para que ocupe todo el espacio vertical

    # Crear el panel izquierdo
    content_left = tk.Frame(content, bg="#ECF0F1", relief="solid", borderwidth=1)
    content_left.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    # Crear el panel derecho
    content_right = tk.Frame(content, bg="#ECF0F1", relief="solid", borderwidth=1)
    content_right.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    # Panel izquierdo: Proyeccion de los gastos
    tk.Label(content_left, text="Proyeccion de los gastos", font=("Arial", 16), bg="#ECF0F1").pack(pady=20)
    table_frame = tk.Frame(content_left, bg="white", relief="solid", borderwidth=1)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Panel derecho: Crear piara y piaras creadas
    tk.Button(content_right, text="Crear piara", font=("Arial", 12), relief="solid", borderwidth=1, command=ventana_creacion_piara).pack(pady=10)
    tk.Label(content_right, text="Piaras creadas", font=("Arial", 14), bg="#ECF0F1").pack(pady=10)
    list_frame = tk.Frame(content_right, bg="white", relief="solid", borderwidth=1)
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Botón de configuración avanzada
    tk.Button(content_right, text="Configuración avanzada", font=("Arial", 12), relief="solid", borderwidth=1).pack(pady=10)
def contenido_ganancias(content):
    tk.Label(content, text="Las ganancias", font=("Arial", 20)).grid(row=0, column=0, pady=50)
def contenido_perfil(content):
    global nombre_usuario
    nombre_usuario_var = tk.StringVar(value=f"Bienvenido usuario, {nombre_usuario}")
    
    center_container = tk.Frame(content, bg="#ECF0F1")
    center_container.place(relx=0.5, rely=0.5, anchor="center")
    
    profile_frame = tk.Frame(center_container, bg="#8B0000", padx=20, pady=20, relief="solid", borderwidth=2)
    profile_frame.pack()
    
    tk.Label(profile_frame, text="Configuración del perfil", font=("Arial", 20), bg="#8B0000", fg="white").pack(pady=10)
    tk.Label(profile_frame, textvariable=nombre_usuario_var, font=("Arial", 14), bg="#8B0000", fg="white").pack(pady=10)
    
    tk.Button(profile_frame, text="Cambiar nombre de usuario", width=25, relief="solid", borderwidth=1, command=lambda: change_username(nombre_usuario_var)).pack(pady=10)
    tk.Button(profile_frame, text="Cambiar contraseña", width=25, relief="solid", borderwidth=1, command=change_password).pack(pady=10)
def generar_contenido_ventana(titulo, botones_sidebar, contenido_central):
    global ventana_activa
    cerrar_ventana_activa()
    ventana_activa = tk.Toplevel(root)
    ventana_activa.title(titulo)
    ventana_activa.state("zoomed")
    
    ventana_activa.grid_columnconfigure(1, weight=1)
    ventana_activa.grid_rowconfigure(0, weight=1)
    
    # Crear la barra lateral
    sidebar = tk.Frame(ventana_activa, bg="#2C3E50", width=200)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_rowconfigure(len(botones_sidebar), weight=1)
    
    # Crear el contenido principal
    content = tk.Frame(ventana_activa, bg="#ECF0F1")
    content.grid(row=0, column=1, sticky="nsew")
    content.grid_columnconfigure(0, weight=1)
    content.grid_rowconfigure(0, weight=1)
    
    # Crear los botones de la barra lateral
    for i, (texto, comando) in enumerate(botones_sidebar):
        tk.Button(sidebar, text=texto, width=15, command=comando).grid(row=i, column=0, pady=10, padx=10, sticky="w")

    #Agregar el contenido central
    contenido_central(content)

    ventana_activa.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))
def crear_ventana_emergente(titulo, contenido_func, ventana_padre=None, centrada=True):
    popup = tk.Toplevel(ventana_padre or root)
    popup.title(titulo)
    popup.grab_set()
    popup.transient(ventana_padre or root)
    
    contenido_func(popup)
    
    if centrada:
        centrar_ventana(popup)

    popup.bind('<Escape>', lambda e: popup.destroy())

#Funciones para el contenido de ventanas emergentes
def contenido_login(popup):
    tk.Label(popup, text="Nombre de Usuario").grid(row=0, column=0, padx=10, pady=5)
    entry_user_login = tk.Entry(popup)
    entry_user_login.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(popup, text="Contraseña").grid(row=1, column=0, padx=10, pady=5)
    entry_password_login = tk.Entry(popup, show="*")
    entry_password_login.grid(row=1, column=1, padx=10, pady=5)
    
    popup.bind('<Return>', lambda e: login_usuario(entry_user_login, entry_password_login, popup))
    popup.bind('<Escape>', lambda e: popup.destroy())
    
    tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=3, column=0, pady=5)
    tk.Button(
        popup, 
        text="Iniciar Sesion", 
        command=lambda: login_usuario(entry_user_login, entry_password_login, popup)
    ).grid(row=3, column=1, padx=10, pady=5)
def contenido_registro(popup):
    tk.Label(popup, text="Nombre de Usuario").grid(row=0, column=0, padx=10, pady=5)
    entry_user_register = tk.Entry(popup)
    entry_user_register.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(popup, text="Contraseña").grid(row=1, column=0, padx=10, pady=5)
    entry_password_register = tk.Entry(popup, show="*")
    entry_password_register.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(popup, text="Confirmar Contraseña").grid(row=2, column=0, padx=10, pady=5)
    entry_confirm_password_register = tk.Entry(popup, show="*")
    entry_confirm_password_register.grid(row=2, column=1, padx=10, pady=5)
    
    popup.bind('<Return>', lambda e: registrar_usuario(entry_user_register, entry_password_register, entry_confirm_password_register, popup))
    popup.bind('<Escape>', lambda e: popup.destroy())
    
    tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=3, column=0, pady=5)
    tk.Button(
        popup, 
        text="Registrarse", 
        command=lambda: registrar_usuario(entry_user_register, entry_password_register, entry_confirm_password_register, popup)
    ).grid(row=3, column=1, padx=10, pady=5)
def contenido_cambiar_password(popup):
    tk.Label(popup, text="Contraseña actual").grid(row=0, column=0, padx=10, pady=5)
    entry_password = tk.Entry(popup, show="*")
    entry_password.grid(row=0, column=1, padx=10, pady=5)
    
    tk.Label(popup, text="Nueva Contraseña").grid(row=1, column=0, padx=10, pady=5)
    entry_new_password = tk.Entry(popup, show="*")
    entry_new_password.grid(row=1, column=1, padx=10, pady=5)
    
    tk.Label(popup, text="Confirmar Nueva Contraseña").grid(row=2, column=0, padx=10, pady=5)
    entry_password_confirmation = tk.Entry(popup, show="*")
    entry_password_confirmation.grid(row=2, column=1, padx=10, pady=5)
    
    tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=3, column=0, pady=10)
    tk.Button(
        popup, 
        text="Confirmar", 
        command=lambda: actualizar_contraseña(entry_password, entry_new_password, entry_password_confirmation, popup)
    ).grid(row=3, column=1, padx=10, pady=5)
def contenido_cambiar_usuario(popup, nombre_usuario_var):
    tk.Label(popup, text="Nuevo nombre de Usuario").grid(row=0, column=0, padx=10, pady=5)
    entry_new_username = tk.Entry(popup)
    entry_new_username.grid(row=0, column=1, padx=10, pady=5)
    
    popup.bind('<Return>', lambda e: actualizar_nombre_usuario(entry_new_username, popup, nombre_usuario_var))
    popup.bind('<Escape>', lambda e: popup.destroy())
    
    tk.Button(popup,text="Cancelar",command=popup.destroy).grid(row=3, column=0, pady=5)
    tk.Button(
        popup, 
        text="Confirmar", 
        command=lambda: actualizar_nombre_usuario(entry_new_username, popup, nombre_usuario_var)
    ).grid(row=3, column=1, padx=10, pady=5)
def contenido_creacion_piara(popup):
    tk.Label(popup, text="Nombre de la Piara").grid(row=0, column=0, padx=10, pady=5)
    entry_nombre_piara = tk.Entry(popup)
    entry_nombre_piara.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(popup, text="Tamaño de la Piara").grid(row=1, column=0, padx=10, pady=5)
    entry_tamaño_piara = tk.Entry(popup)
    entry_tamaño_piara.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(popup, text="Semanas desde el nacimiento de la Piara").grid(row=2, column=0, padx=10, pady=5)
    entry_semanas_piara = tk.Entry(popup)
    entry_semanas_piara.grid(row=2, column=1, padx=10, pady=5)

    tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=3, column=0, pady=5)
    tk.Button(
        popup,
        text="Crear Piara",
        command=lambda: crear_piara(entry_nombre_piara, entry_tamaño_piara, entry_semanas_piara, popup)
    ).grid(row=3, column=1, padx=10, pady=5)

#Funciones de las ventanas
def ventana_gastos():
    generar_contenido_ventana("Ventana gastos", [("perfil", window_perfil), ("gastos", ventana_gastos), ("ganancias", window_ganancias)], contenido_ventana_gastos)
def window_ganancias():
    generar_contenido_ventana("Ganancias", [("perfil", window_perfil), ("gastos", ventana_gastos), ("ganancias", window_ganancias)], contenido_ganancias)
def window_perfil():
    generar_contenido_ventana("Configuracion de perfil", [("perfil", window_perfil), ("gastos", ventana_gastos), ("ganancias", window_ganancias)], contenido_perfil)
def open_window_register():
    crear_ventana_emergente("Registro de Usuario", contenido_registro, ventana_padre=menu_principal)
def open_window_login():
    crear_ventana_emergente("Inicio de Sesión", contenido_login, ventana_padre=menu_principal)
def change_password():
    crear_ventana_emergente("Cambiar contraseña", contenido_cambiar_password, ventana_padre=ventana_activa)
def change_username(nombre_usuario_var):
    crear_ventana_emergente("Cambiar Usuario", lambda popup : contenido_cambiar_usuario(popup, nombre_usuario_var), ventana_padre=ventana_activa)
def ventana_creacion_piara():
    crear_ventana_emergente("Crear Piara", contenido_creacion_piara, ventana_padre=ventana_activa)
def cerrar_aplicacion(ventana_root):
    cerrar_ventana_activa()
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