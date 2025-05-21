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
    semanas INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (nombre, user_id)
    
)''')
conn.commit()

#Funciones encargadas de las piaras
def calcular_gastos_piaras(ids_piaras):
    semana_consumo = {
        1: 0.22, 2: 0.37, 3: 0.53, 4: 0.73, 5: 0.88, 6: 1, 7: 1.35, 8: 1.5, 9: 1.65, 10: 1.8,
        11: 1.95, 12: 2.05, 13: 2.15, 14: 2.25, 15: 2.35, 16: 2.45, 17: 2.55, 18: 2.65, 19: 2.75,
        20: 2.8, 21: 2.85
    }
    preiniciador = 4250
    iniciacion = 3800
    levante = 3300
    engorde = 3000

    total_cerdos = 0
    total_alimento = 0
    total_medicamentos = 0  # Puedes agregar lógica para medicamentos si la tienes

    for piara_id in ids_piaras:
        cursor.execute("SELECT tamaño, semanas FROM piaras WHERE id = ? AND user_id = ?", (piara_id, usuario_actual))
        piara = cursor.fetchone()
        if not piara:
            continue
        tamaño, semanas = piara
        total_cerdos += tamaño
        calculo_a = 0
        aux = 0
        s = semanas
        if s < 4:
            for i in range(s, 4):
                aux += 7 * semana_consumo.get(i, 0)
            aux *= preiniciador
            calculo_a += aux
            aux = 0
            s = 4
        if s < 8:
            for i in range(s, 8):
                aux += 7 * semana_consumo.get(i, 0)
            aux *= iniciacion
            calculo_a += aux
            aux = 0
            s = 8
        if s < 12:
            for i in range(s, 12):
                aux += 7 * semana_consumo.get(i, 0)
            aux *= levante
            calculo_a += aux
            aux = 0
            s = 12
        if s < 22:
            for i in range(s, 22):
                aux += 7 * semana_consumo.get(i, 0)
            aux *= engorde
            calculo_a += aux
        total_alimento += calculo_a * tamaño

    total_gastos = total_alimento + total_medicamentos
    return {
        "total_piaras": len(ids_piaras),
        "total_cerdos": total_cerdos,
        "gasto_alimentos": total_alimento,
        "gasto_medicamentos": total_medicamentos,
        "total_gastos": total_gastos
    }
def eliminar_piaras(ids_piaras, listbox):
    global usuario_actual
    if not ids_piaras:
        messagebox.showerror("Error", "Selecciona al menos una piara para eliminar.")
        return
    if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar las piaras seleccionadas?"):
        return
    for piara_id in ids_piaras:
        cursor.execute("DELETE FROM piaras WHERE id = ? AND user_id = ?", (piara_id, usuario_actual))
    conn.commit()
    # Actualiza el listbox
    listbox.delete(0, tk.END)
    piaras = obtener_piaras_usuario(usuario_actual)
    for piara in piaras():
        listbox.insert(tk.END, piara[1])
def configurar_piara(piara_id, listbox, callback_recarga=None):
    cursor.execute("SELECT nombre, tamaño, semanas FROM piaras WHERE id = ? AND user_id = ?", (piara_id, usuario_actual))
    piara = cursor.fetchone()
    if not piara:
        messagebox.showerror("Error", "No se encontró la piara.")
        return

    def guardar_cambios():
        nuevo_nombre = entry_nombre.get()
        nuevo_tamaño = entry_tamaño.get()
        nuevas_semanas = entry_semanas.get()
        if not nuevo_nombre or not nuevo_tamaño or not nuevas_semanas:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        try:
            nuevo_tamaño = int(nuevo_tamaño)
            nuevas_semanas = int(nuevas_semanas)
        except ValueError:
            messagebox.showerror("Error", "Tamaño y semanas deben ser números enteros.")
            return
        try:
            cursor.execute("UPDATE piaras SET nombre=?, tamaño=?, semanas=? WHERE id=?",
                           (nuevo_nombre, nuevo_tamaño, nuevas_semanas, piara_id))
            conn.commit()
            messagebox.showinfo("Éxito", "Piara actualizada correctamente.")
            popup.destroy()
            if callback_recarga:
                callback_recarga()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de la piara ya existe.")

    popup = tk.Toplevel(ventana_activa)
    popup.title("Configurar Piara")
    tk.Label(popup, text="Nombre:").grid(row=0, column=0, padx=10, pady=5)
    entry_nombre = tk.Entry(popup)
    entry_nombre.insert(0, piara[0])
    entry_nombre.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(popup, text="Tamaño:").grid(row=1, column=0, padx=10, pady=5)
    entry_tamaño = tk.Entry(popup)
    entry_tamaño.insert(0, piara[1])
    entry_tamaño.grid(row=1, column=1, padx=10, pady=5)
    tk.Label(popup, text="Semanas:").grid(row=2, column=0, padx=10, pady=5)
    entry_semanas = tk.Entry(popup)
    entry_semanas.insert(0, piara[2])
    entry_semanas.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(popup, text="Guardar", command=guardar_cambios).grid(row=3, column=0, columnspan=2, pady=10)
    tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=4, column=0, columnspan=2, pady=5)

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
def crear_piara(entry_nombre_piara, entry_tamaño_piara, entry_semanas_piara, popup, callback_recarga=None):
    nombre_piara = entry_nombre_piara.get()
    tamaño_piara = entry_tamaño_piara.get()
    semanas_piara = entry_semanas_piara.get()

    if not nombre_piara or not tamaño_piara or not semanas_piara:
        messagebox.showerror("Error", "Todos los campos son obligatorios.")
        return

    try:
        if len(nombre_piara) > 20:
            messagebox.showerror(title="ERROR", message="El nombre de la piara debe tener al menos 1 carácter y no más de 20")
            return
        tamaño_piara = int(tamaño_piara)
        semanas_piara = int(semanas_piara)
        
        if semanas_piara>21:
            messagebox.showerror(title="ERROR",message="La edad no puede ser mayor a 21 semanas")
            return
    except ValueError:
        messagebox.showerror("Error", "El tamaño y las semanas deben ser números enteros.")
        return

    try:
        cursor.execute("INSERT INTO piaras (nombre, tamaño, semanas, user_id) VALUES (?, ?, ?, ?)", (nombre_piara, tamaño_piara, semanas_piara, usuario_actual))
        conn.commit()
        messagebox.showinfo("Éxito", "Piara creada correctamente.")
        popup.destroy()
        if callback_recarga:
            callback_recarga()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El nombre de la piara ya existe.")
def obtener_piaras_usuario(user_id):
    cursor.execute("SELECT id, nombre FROM piaras WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

#Funciones para el contenido de las ventanas
def contenido_gastos(content):
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
    tk.Button(
        content_right,
        text="Crear piara",
        font=("Arial", 12),
        relief="solid",
        borderwidth=1,
        command=lambda: crear_ventana_emergente(
            "Crear Piara",
            lambda popup: contenido_creacion_piara(popup, recargar_lista_piaras),
            ventana_padre=ventana_activa
        )
    ).pack(pady=10)
    tk.Label(content_right, text="Piaras creadas", font=("Arial", 14), bg="#ECF0F1").pack(pady=10)
    
    list_frame = tk.Frame(content_right, bg="white", relief="solid", borderwidth=1)
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    scroll = tk.Scrollbar(list_frame)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    etiquetas_piaras = tk.Listbox(list_frame, yscrollcommand=scroll.set, selectmode=tk.MULTIPLE)
    etiquetas_piaras.pack(fill="both", expand=True)
    
    scroll.config(command=etiquetas_piaras.yview)
    etiquetas_piaras.config(yscrollcommand=scroll.set)
    
    # Obtener las piaras de la base de datos
    piaras = obtener_piaras_usuario(usuario_actual)
    piara_id_map ={}
    for piara in piaras:
        piara_id_map[piara[1]] = piara [0]
        etiquetas_piaras.insert(tk.END, piara[1])

    resultado_frame = tk.Frame(content_left, bg="white")
    resultado_frame.pack(fill="x", pady=10)
    
    def recargar_lista_piaras():
        etiquetas_piaras.delete(0, tk.END)
        piara_id_map.clear()
        piaras = obtener_piaras_usuario(usuario_actual)
        for piara in piaras:
            piara_id_map[piara[1]] = piara[0]
            etiquetas_piaras.insert(tk.END, piara[1])
    def mostrar_gastos():
        seleccion = etiquetas_piaras.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Selecciona al menos una piara")
            return
        # Obtener los IDs de las piaras seleccionadas
        nombres_seleccionados = [etiquetas_piaras.get(i) for i in seleccion]
        ids_seleccionados = [piara_id_map[nombre] for nombre in nombres_seleccionados]
        resultados = calcular_gastos_piaras(ids_seleccionados)
        # Limpiar el frame antes de mostrar nuevos resultados
        for widget in resultado_frame.winfo_children():
            widget.destroy()
        tk.Label(resultado_frame, text=f"TOTAL DE PIARAS: {resultados['total_piaras']}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(resultado_frame, text=f"TOTAL DE CERDOS: {resultados['total_cerdos']}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(resultado_frame, text=f"GASTO EN ALIMENTOS: {resultados['gasto_alimentos']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(resultado_frame, text=f"GASTO EN MEDICAMENTOS: {resultados['gasto_medicamentos']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(resultado_frame, text=f"TOTAL GASTOS: {resultados['total_gastos']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
    def eliminar_seleccionadas():
        seleccion = etiquetas_piaras.curselection()
        nombres_seleccionados = [etiquetas_piaras.get(i) for i in seleccion]
        ids_seleccionados = [piara_id_map[nombre] for nombre in nombres_seleccionados]
        eliminar_piaras(ids_seleccionados, etiquetas_piaras)
        recargar_lista_piaras()
    def configurar_seleccionada():
        seleccion = etiquetas_piaras.curselection()
        if len(seleccion) != 1:
            messagebox.showerror("Error", "Selecciona solo una piara para configurar.")
            return
        nombre = etiquetas_piaras.get(seleccion[0])
        piara_id = piara_id_map[nombre]
        configurar_piara(piara_id, etiquetas_piaras, recargar_lista_piaras)
    
    # Botón para calcular gastos
    tk.Button(content_right, text="Calcular gastos", font=("Arial", 12), relief="solid", borderwidth=1, command=mostrar_gastos).pack(pady=10)
    tk.Button(content_right, text="Eliminar piara(s)", font=("Arial", 12), relief="solid", borderwidth=1, command=eliminar_seleccionadas).pack(pady=5)
    tk.Button(content_right, text="Configurar piara", font=("Arial", 12), relief="solid", borderwidth=1, command=configurar_seleccionada).pack(pady=5)

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
def contenido_cambiar_usuario(popup, nombre_usuario_var, recargar_lista_piaras):
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
def contenido_creacion_piara(popup, recargar_lista_piaras):
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
        command=lambda: crear_piara(entry_nombre_piara, entry_tamaño_piara, entry_semanas_piara, popup, recargar_lista_piaras)
    ).grid(row=3, column=1, padx=10, pady=5)

#Funciones de las ventanas
def ventana_gastos():
    generar_contenido_ventana("Ventana gastos", [("perfil", window_perfil), ("gastos", ventana_gastos), ("ganancias", window_ganancias)], contenido_gastos)
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