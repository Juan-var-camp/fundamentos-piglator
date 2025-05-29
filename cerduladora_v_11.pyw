import sqlite3
import hashlib
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

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
    nombre TEXT NOT NULL,
    tamaño INTEGER NOT NULL,
    semanas INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (nombre, user_id)
    
)''')
conn.commit()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN preiniciador INTEGER DEFAULT 4250")
    cursor.execute("ALTER TABLE users ADD COLUMN iniciacion INTEGER DEFAULT 3800")
    cursor.execute("ALTER TABLE users ADD COLUMN levante INTEGER DEFAULT 3300")
    cursor.execute("ALTER TABLE users ADD COLUMN engorde INTEGER DEFAULT 3000")
    cursor.execute("ALTER TABLE users ADD COLUMN precio_vivo_1 INTEGER DEFAULT 6000")
    cursor.execute("ALTER TABLE users ADD COLUMN precio_vivo_2 INTEGER DEFAULT 7000")
    cursor.execute("ALTER TABLE users ADD COLUMN precio_vivo_3 INTEGER DEFAULT 8000")
    cursor.execute("ALTER TABLE users ADD COLUMN precio_menudeo INTEGER DEFAULT 11500")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Las columnas ya existen

#constantes
semana_consumo = {
    "1": 0.22, "2": 0.37, "3": 0.53, "4": 0.73, "5": 0.88, "6": 1, "7": 1.35, "8": 1.5, "9": 1.65, "10": 1.8,
    "11": 1.95, "12": 2.05, "13": 2.15, "14": 2.25, "15": 2.35, "16": 2.45, "17": 2.55, "18": 2.65, "19": 2.75,
    "20": 2.8, "21": 2.85
}
    
semana_peso={"1":6.665,"2":8.31,"3":10.655,"4":13.84,"5":17.865,"6":22.52,"7":27.6,"8":32.95,"9":38.55,"10":44.3,
                "11":50.15,"12":56.2,"13":62.4,"14":68.8,"15":75.3,"16":81.95,"17":88.75,"18":95.7,"19":102.75,
                "20":109.9,"21":117.1}
costes_medicamentos={"Hierro":10000,"Vacuna PPC":18000,"Ivermectina":35000,"Oxitetraciclina":45000,"Albendazol":22500,"Suero":15000}
medicamentos_extra= costes_medicamentos["Oxitetraciclina"]*4/25+costes_medicamentos["Suero"]

semana_medicamento = {"1":costes_medicamentos["Hierro"]/50,"6":costes_medicamentos["Ivermectina"]/50,
                      "8":costes_medicamentos["Vacuna PPC"]+costes_medicamentos["Albendazol"]/125,
                "20":costes_medicamentos["Vacuna PPC"]+costes_medicamentos["Albendazol"]/125,
                "21":costes_medicamentos["Ivermectina"]/50}

precio_vivo_1 = 6000
precio_vivo_2 = 7000
precio_vivo_3 = 8000
precio_menudeo = 11500

preiniciador = 4250
iniciacion = 3800
levante = 3300
engorde = 3000

#Funciones encargadas de las piaras
def calcular_gastos_piaras(ids_piaras):
    
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
        
        #Calculo de los alimentos
        calculo_a = 0
        aux = 0
        s = semanas
        if s < 4:
            for i in range(s, 4):
                aux += 7 * semana_consumo.get(str(i), 0)
            aux *= preiniciador
            calculo_a += aux
            aux = 0
            s = 4
        if s < 8:
            for i in range(s, 8):
                aux += 7 * semana_consumo.get(str(i), 0)
            aux *= iniciacion
            calculo_a += aux
            aux = 0
            s = 8
        if s < 12:
            for i in range(s, 12):
                aux += 7 * semana_consumo.get(str(i), 0)
            aux *= levante
            calculo_a += aux
            aux = 0
            s = 12
        if s < 22:
            for i in range(s, 22):
                aux += 7 * semana_consumo.get(str(i), 0)
            aux *= engorde
            calculo_a += aux
        total_alimento += calculo_a * tamaño
        
        #Calculo de los medicamentos
        calculo_m = medicamentos_extra
        for i in range(semanas, 21):
            if str(i) in semana_medicamento:
                calculo_m += semana_medicamento[str(i)]
        total_medicamentos += calculo_m * tamaño

    total_gastos = total_alimento + total_medicamentos
    return {
        "total_piaras": len(ids_piaras),
        "total_cerdos": total_cerdos,
        "gasto_alimentos": total_alimento,
        "gasto_medicamentos": total_medicamentos,
        "total_gastos": total_gastos
    }

def eliminar_piaras(ids_piaras, listbox, callback_recarga=None):
    global usuario_actual
    if not ids_piaras:
        messagebox.showerror("Error", "Selecciona al menos una piara para eliminar.")
        return
    if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar las piaras seleccionadas?"):
        return
    for piara_id in ids_piaras:
        cursor.execute("DELETE FROM piaras WHERE id = ? AND user_id = ?", (piara_id, usuario_actual))
    conn.commit()
    if callback_recarga:
        callback_recarga()

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
        
        if not validar_campos_obligatorios([nuevo_nombre, nuevo_tamaño, nuevas_semanas]):
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
            popup.destroy()
            messagebox.showinfo("Éxito", "Piara actualizada correctamente.")
            if callback_recarga:
                callback_recarga()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "El nombre de la piara ya existe.")

    popup = tk.Toplevel(ventana_activa)
    popup.title("Configurar Piara")
    popup.grab_set()
    popup.resizable(False, False)
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
    centrar_ventana(popup)

def calcular_ganancias_piaras(ids_piaras, tipo_venta=0):
    "tipo de venta: 0 = vender vivo, 1 = vender menudeo"
    
    total_gasto = 0
    total_kilos = 0
    retorno = 0
    
    for piara_id in ids_piaras:
        cursor.execute("SELECT tamaño, semanas FROM piaras WHERE id = ? AND user_id = ?", (piara_id, usuario_actual))
        piara = cursor.fetchone()
        if not piara:
            continue
        tamaño, semanas = piara

        gasto_base = calcular_gasto_base()["gasto_base_alimentos"] + calcular_gasto_base()["gasto_base_medicamentos"]
        gasto_base = gasto_base*tamaño

        gasto_restante = calcular_gastos_restantes(semanas)["gasto_restante_alimentos"] + calcular_gastos_restantes(semanas)["gasto_restante_medicamentos"]
        gasto_restante = gasto_restante * tamaño

        total_gasto += gasto_base - gasto_restante

        kilos = semana_peso.get(str(semanas), 0) * tamaño
        total_kilos += kilos
        
        if tipo_venta == 0:  # Venta en vivo
            if semana_peso.get(str(semanas), 0) < 30:
                retorno += kilos * precio_vivo_1
            elif semana_peso.get(str(semanas), 0) < 100:
                retorno += kilos * precio_vivo_2
            else:
                retorno += kilos * precio_vivo_3
        else:  # Menudeo
            retorno += (kilos*0.75) * precio_menudeo

    if tipo_venta != 0:
        total_kilos *= 0.75  

    ganancia = retorno - total_gasto

    return {
        "total_kilos": total_kilos,
        "retorno": retorno,
        "total_gasto": total_gasto,
        "ganancia": ganancia
    }

def calcular_gasto_base():

    # Calcular gasto en alimentos
    gasto_alimentos = 0
    # Preiniciador: semanas 1-3 (3 semanas)
    for i in range(1, 4):
        gasto_alimentos += 7 * semana_consumo[str(i)] * preiniciador
    # Iniciación: semanas 4-7 (4 semanas)
    for i in range(4, 8):
        gasto_alimentos += 7 * semana_consumo[str(i)] * iniciacion
    # Levante: semanas 8-11 (4 semanas)
    for i in range(8, 12):
        gasto_alimentos += 7 * semana_consumo[str(i)] * levante
    # Engorde: semanas 12-21 (10 semanas)
    for i in range(12, 22):
        gasto_alimentos += 7 * semana_consumo[str(i)] * engorde

    # Calcular gasto en medicamentos
    gasto_medicamentos = medicamentos_extra
    for i in range(1, 22):
        if str(i) in semana_medicamento:
            gasto_medicamentos += semana_medicamento[str(i)]

    return {
        "gasto_base_alimentos": round(gasto_alimentos, 3),
        "gasto_base_medicamentos": round(gasto_medicamentos, 3)
    }

def calcular_gastos_restantes(semana_actual):

    gasto_alimentos = 0
    # Preiniciador: semanas 1-3
    for i in range(max(semana_actual, 1), 4):
        gasto_alimentos += 7 * semana_consumo[str(i)] * preiniciador
    # Iniciación: semanas 4-7
    for i in range(max(semana_actual, 4), 8):
        gasto_alimentos += 7 * semana_consumo[str(i)] * iniciacion
    # Levante: semanas 8-11
    for i in range(max(semana_actual, 8), 12):
        gasto_alimentos += 7 * semana_consumo[str(i)] * levante
    # Engorde: semanas 12-21
    for i in range(max(semana_actual, 12), 22):
        gasto_alimentos += 7 * semana_consumo[str(i)] * engorde

    # Medicamentos
    gasto_medicamentos = medicamentos_extra
    if semana_actual <= 21:
        for i in range(semana_actual, 22):
            if str(i) in semana_medicamento:
                gasto_medicamentos += semana_medicamento[str(i)]

    return {
        "gasto_restante_alimentos": round(gasto_alimentos, 3),
        "gasto_restante_medicamentos": round(gasto_medicamentos, 3)
    }

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

def validar_campos_obligatorios(campos, mensaje="Todos los campos son obligatorios."):
    if any(not campo for campo in campos):
        messagebox.showerror("Error", mensaje)
        return False
    return True

def cargar_piaras_en_listbox(listbox, piara_id_map, user_id):
    listbox.delete(0, tk.END)
    piara_id_map.clear()
    piaras = obtener_piaras_usuario(user_id)
    for piara in piaras:
        piara_id_map[piara[1]] = piara[0]
        listbox.insert(tk.END, piara[1])

def obtener_ids_seleccionados(listbox, piara_id_map):
    seleccion = listbox.curselection()
    nombres_seleccionados = [listbox.get(i) for i in seleccion]
    return [piara_id_map[nombre] for nombre in nombres_seleccionados]

def configuracion_avanzada():
    def guardar_cambios():
        try:
            global preiniciador, iniciacion, levante, engorde
            global precio_vivo_1, precio_vivo_2, precio_vivo_3, precio_menudeo

            preiniciador = int(entry_preiniciador.get())
            iniciacion = int(entry_iniciacion.get())
            levante = int(entry_levante.get())
            engorde = int(entry_engorde.get())
            precio_vivo_1 = int(entry_vivo1.get())
            precio_vivo_2 = int(entry_vivo2.get())
            precio_vivo_3 = int(entry_vivo3.get())
            precio_menudeo = int(entry_menudeo.get())
            
            cursor.execute("""
                UPDATE users SET preiniciador=?, iniciacion=?, levante=?, engorde=?,
                precio_vivo_1=?, precio_vivo_2=?, precio_vivo_3=?, precio_menudeo=?
                WHERE id=?
            """, (preiniciador, iniciacion, levante, engorde, precio_vivo_1, precio_vivo_2, precio_vivo_3, precio_menudeo, usuario_actual))
            conn.commit()

            popup.destroy()
            messagebox.showinfo("Éxito", "Precios actualizados correctamente.")
        except ValueError:
            messagebox.showerror("Error", "Todos los valores deben ser números enteros.")

    popup = tk.Toplevel(ventana_activa)
    popup.title("Configuración avanzada")
    popup.grab_set()
    popup.resizable(False, False)

    tk.Label(popup, text="Precios de alimentos (por kg):", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
    tk.Label(popup, text="Preiniciador:").grid(row=1, column=0, sticky="e")
    entry_preiniciador = tk.Entry(popup)
    entry_preiniciador.insert(0, str(preiniciador))
    entry_preiniciador.grid(row=1, column=1)

    tk.Label(popup, text="Iniciación:").grid(row=2, column=0, sticky="e")
    entry_iniciacion = tk.Entry(popup)
    entry_iniciacion.insert(0, str(iniciacion))
    entry_iniciacion.grid(row=2, column=1)

    tk.Label(popup, text="Levante:").grid(row=3, column=0, sticky="e")
    entry_levante = tk.Entry(popup)
    entry_levante.insert(0, str(levante))
    entry_levante.grid(row=3, column=1)

    tk.Label(popup, text="Engorde:").grid(row=4, column=0, sticky="e")
    entry_engorde = tk.Entry(popup)
    entry_engorde.insert(0, str(engorde))
    entry_engorde.grid(row=4, column=1)

    tk.Label(popup, text="Precios de venta (por kg):", font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=2, pady=5)
    tk.Label(popup, text="Venta vivo (<30kg):").grid(row=6, column=0, sticky="e")
    entry_vivo1 = tk.Entry(popup)
    entry_vivo1.insert(0, str(precio_vivo_1))
    entry_vivo1.grid(row=6, column=1)

    tk.Label(popup, text="Venta vivo (30-100kg):").grid(row=7, column=0, sticky="e")
    entry_vivo2 = tk.Entry(popup)
    entry_vivo2.insert(0, str(precio_vivo_2))
    entry_vivo2.grid(row=7, column=1)

    tk.Label(popup, text="Venta vivo (>100kg):").grid(row=8, column=0, sticky="e")
    entry_vivo3 = tk.Entry(popup)
    entry_vivo3.insert(0, str(precio_vivo_3))
    entry_vivo3.grid(row=8, column=1)

    tk.Label(popup, text="Venta menudeo:").grid(row=9, column=0, sticky="e")
    entry_menudeo = tk.Entry(popup)
    entry_menudeo.insert(0, str(precio_menudeo))
    entry_menudeo.grid(row=9, column=1)

    tk.Button(popup, text="Guardar", command=guardar_cambios).grid(row=10, column=0, columnspan=2, pady=10)
    tk.Button(popup, text="Cancelar", command=popup.destroy).grid(row=11, column=0, columnspan=2, pady=5)

    centrar_ventana(popup)

def cargar_precios_usuario():
    global preiniciador, iniciacion, levante, engorde
    global precio_vivo_1, precio_vivo_2, precio_vivo_3, precio_menudeo
    cursor.execute("""
        SELECT preiniciador, iniciacion, levante, engorde, precio_vivo_1, precio_vivo_2, precio_vivo_3, precio_menudeo
        FROM users WHERE id = ?
    """, (usuario_actual,))
    datos = cursor.fetchone()
    if datos:
        preiniciador, iniciacion, levante, engorde, precio_vivo_1, precio_vivo_2, precio_vivo_3, precio_menudeo = datos

#Funciones referentes a la base de datos
def actualizar_contraseña(entry_password, entry_new_password, entry_password_confirmation, popup):
    global usuario_actual
    current_password = entry_password.get()
    new_password = entry_new_password.get()
    confirm_password = entry_password_confirmation.get()

    if not validar_campos_obligatorios([current_password, new_password, confirm_password]):
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
    popup.destroy()
    messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")

def actualizar_nombre_usuario(entry_new_username, popup, nombre_usuario_var):
    global usuario_actual, nombre_usuario
    new_username = entry_new_username.get()
    if not validar_campos_obligatorios([new_username]):
        return
    
    try:
        cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, usuario_actual))
        conn.commit()
        nombre_usuario = new_username
        nombre_usuario_var.set(f"Bienvenido usuario, {nombre_usuario}")
        popup.destroy()
        messagebox.showinfo("Éxito", "Nombre de usuario actualizado correctamente.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El nombre de usuario ya existe. Por favor, elige otro.")

def login_usuario(entry_user_login,entry_password_login,login_window):
    global usuario_actual, nombre_usuario
    username = entry_user_login.get()
    password = entry_password_login.get()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if not validar_campos_obligatorios([username, password]):
        return
    
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    resultado = cursor.fetchone()
    if resultado and resultado[1] == hashed_password:
        usuario_actual = resultado[0]  
        nombre_usuario = username
        cargar_precios_usuario()
        try:
            login_window.destroy()
        except:
            pass
        try:
            menu_principal.destroy()
        except:
            pass
        ventana_gastos()
        messagebox.showinfo("Felicidades", "Inicio de sesion exitoso")
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
    if not validar_campos_obligatorios([username, password, confirmation]):
        return
    if len(password) < 8:
        messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres")
        return

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        register_window.destroy()
        messagebox.showinfo("Felicidades", "registro exitoso")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El usuario ya existe")

def crear_piara(entry_nombre_piara, entry_tamaño_piara, entry_semanas_piara, popup, callback_recarga=None):
    nombre_piara = entry_nombre_piara.get()
    tamaño_piara = entry_tamaño_piara.get()
    semanas_piara = entry_semanas_piara.get()

    if not validar_campos_obligatorios([nombre_piara, tamaño_piara, semanas_piara]):
        return

    try:
        if len(nombre_piara) > 20:
            messagebox.showerror(title="ERROR", message="El nombre de la piara debe tener al menos 1 carácter y no más de 20")
            return
        tamaño_piara = int(tamaño_piara)
        semanas_piara = int(semanas_piara)
        
        if tamaño_piara <= 0 or semanas_piara <= 0:
            messagebox.showerror(title="ERROR", message="El tamaño y las semanas deben ser mayores a 0")
            return

        if tamaño_piara > 10000:
            messagebox.showerror(title="ERROR", message="El tamaño de la piara no puede exceder los 10000")
            return

        if semanas_piara>21:
            messagebox.showerror(title="ERROR",message="La edad no puede ser mayor a 21 semanas")
            return
    except ValueError:
        messagebox.showerror("Error", "El tamaño y las semanas deben ser números enteros.")
        return

    try:
        cursor.execute("INSERT INTO piaras (nombre, tamaño, semanas, user_id) VALUES (?, ?, ?, ?)", (nombre_piara, tamaño_piara, semanas_piara, usuario_actual))
        conn.commit()
        popup.destroy()
        if callback_recarga:
            callback_recarga()
        messagebox.showinfo("Éxito", "Piara creada correctamente.")
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
    tk.Button(content_right,text="Crear piara",font=("Arial", 12),relief="solid",borderwidth=1,command=lambda: crear_ventana_emergente("Crear Piara",lambda popup: contenido_creacion_piara(popup, recargar_lista_piaras),ventana_padre=ventana_activa)).pack(pady=10)
    tk.Label(content_right, text="Piaras creadas", font=("Arial", 14), bg="#ECF0F1").pack(pady=10)
    
    list_frame = tk.Frame(content_right, bg="white", relief="solid", borderwidth=1)
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    scroll = tk.Scrollbar(list_frame)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    etiquetas_piaras = tk.Listbox(list_frame, yscrollcommand=scroll.set, selectmode=tk.MULTIPLE, font=("Arial", 18))
    etiquetas_piaras.pack(fill="both", expand=True)
    
    scroll.config(command=etiquetas_piaras.yview)
    etiquetas_piaras.config(yscrollcommand=scroll.set)
    
    # Obtener las piaras de la base de datos
    piara_id_map = {}
    cargar_piaras_en_listbox(etiquetas_piaras, piara_id_map, usuario_actual)

    def recargar_lista_piaras():
        cargar_piaras_en_listbox(etiquetas_piaras, piara_id_map, usuario_actual)
        
    def mostrar_gastos():
        ids_seleccionados = obtener_ids_seleccionados(etiquetas_piaras, piara_id_map)
        if not ids_seleccionados:
            messagebox.showerror("Error", "Selecciona al menos una piara")
            return
        resultados = calcular_gastos_piaras(ids_seleccionados)
        # Limpiar el frame antes de mostrar nuevos resultados
        for widget in table_frame.winfo_children():
            widget.destroy()
        tk.Label(table_frame, text=f"TOTAL DE PIARAS: {resultados['total_piaras']}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(table_frame, text=f"TOTAL DE CERDOS: {resultados['total_cerdos']}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(table_frame, text=f"GASTO EN ALIMENTOS: {resultados['gasto_alimentos']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(table_frame, text=f"GASTO EN MEDICAMENTOS: {resultados['gasto_medicamentos']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(table_frame, text=f"TOTAL GASTOS: {resultados['total_gastos']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")

    def eliminar_seleccionadas():
        ids_seleccionados = obtener_ids_seleccionados(etiquetas_piaras, piara_id_map)
        eliminar_piaras(ids_seleccionados, etiquetas_piaras, recargar_lista_piaras)

    def configurar_seleccionada():
        ids_seleccionados = obtener_ids_seleccionados(etiquetas_piaras, piara_id_map)
        if len(ids_seleccionados) != 1:
            messagebox.showerror("Error", "Selecciona solo una piara para configurar.")
            return
        configurar_piara(ids_seleccionados[0], etiquetas_piaras, recargar_lista_piaras)
    
    def exportar_gastos_txt():
        ids_seleccionados = obtener_ids_seleccionados(etiquetas_piaras, piara_id_map)
        if not ids_seleccionados:
            messagebox.showerror("Error", "Selecciona al menos una piara")
            return
        resultados = calcular_gastos_piaras(ids_seleccionados)
        detalles = []
        for piara_id in ids_seleccionados:
            cursor.execute("SELECT nombre, tamaño, semanas FROM piaras WHERE id = ? AND user_id = ?", (piara_id, usuario_actual))
            piara = cursor.fetchone()
            if piara:
                detalles.append(f"Nombre: {piara[0]}, Tamaño: {piara[1]}, Semanas: {piara[2]}")
        contenido = "REPORTE DE PIARAS Y GASTOS\n\n"
        contenido += "\n".join(detalles) + "\n\n"
        contenido += f"TOTAL DE PIARAS: {resultados['total_piaras']}\n"
        contenido += f"TOTAL DE CERDOS: {resultados['total_cerdos']}\n"
        contenido += f"GASTO EN ALIMENTOS: {resultados['gasto_alimentos']:.2f}\n"
        contenido += f"GASTO EN MEDICAMENTOS: {resultados['gasto_medicamentos']:.2f}\n"
        contenido += f"TOTAL GASTOS: {resultados['total_gastos']:.2f}\n"

        # Diálogo para elegir ubicación y nombre del archivo
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt")],
            title="Guardar reporte de gastos"
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Éxito", f"Reporte exportado en:\n{ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")
    
    # Botón para calcular gastos
    tk.Button(content_right, text="Calcular gastos", font=("Arial", 12), relief="solid", borderwidth=1, command=mostrar_gastos).pack(pady=10)
    tk.Button(content_right, text="Eliminar piara(s)", font=("Arial", 12), relief="solid", borderwidth=1, command=eliminar_seleccionadas).pack(pady=5)
    tk.Button(content_right, text="Configurar piara", font=("Arial", 12), relief="solid", borderwidth=1, command=configurar_seleccionada).pack(pady=5)
    tk.Button(content_right, text="Exportar a TXT", font=("Arial", 12), relief="solid", borderwidth=1, command=exportar_gastos_txt).pack(pady=10)

    # Botón de configuración avanzada
    tk.Button(content_right, text="Configuración avanzada", font=("Arial", 12), relief="solid", borderwidth=1,command=configuracion_avanzada).pack(pady=10)

def contenido_ganancias(content):
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
    tk.Label(content_left, text="Proyeccion de las ganancias", font=("Arial", 16), bg="#ECF0F1").pack(pady=20)
    table_frame = tk.Frame(content_left, bg="white", relief="solid", borderwidth=1)
    table_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Panel derecho
    tk.Label(content_right, text="Piaras", font=("Arial", 14), bg="#ECF0F1").pack(pady=10)
    
    list_frame = tk.Frame(content_right, bg="white", relief="solid", borderwidth=1)
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    scroll = tk.Scrollbar(list_frame)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    etiquetas_piaras = tk.Listbox(list_frame, yscrollcommand=scroll.set, selectmode=tk.MULTIPLE, font=("Arial", 18))
    etiquetas_piaras.pack(fill="both", expand=True)
    
    scroll.config(command=etiquetas_piaras.yview)
    etiquetas_piaras.config(yscrollcommand=scroll.set)
    
    # Obtener las piaras de la base de datos
    piara_id_map = {}
    cargar_piaras_en_listbox(etiquetas_piaras, piara_id_map, usuario_actual)

    tipo_venta_var = tk.IntVar(value=0)
    tk.Radiobutton(content_right, text="Vender vivo", variable=tipo_venta_var, value=0, bg="#ECF0F1").pack()
    tk.Radiobutton(content_right, text="Vender en menudeo", variable=tipo_venta_var, value=1, bg="#ECF0F1").pack()

    def mostrar_ganancias():
        ids_seleccionados = obtener_ids_seleccionados(etiquetas_piaras, piara_id_map)
        if not ids_seleccionados:
            messagebox.showerror("Error", "Selecciona al menos una piara")
            return
        resultados = calcular_ganancias_piaras(ids_seleccionados, tipo_venta=tipo_venta_var.get())
        for widget in table_frame.winfo_children():
            widget.destroy()
        tk.Label(table_frame, text=f"TOTAL KILOS: {resultados['total_kilos']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(table_frame, text=f"TOTAL RETORNO: {resultados['retorno']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(table_frame, text=f"TOTAL INVERTIDO: {resultados['total_gasto']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(table_frame, text=f"TOTAL GANANCIAS: {resultados['ganancia']:.2f}", bg="white", font=("Arial", 12)).pack(anchor="w")

    tk.Button(content_right, text="Calcular ganancias", font=("Arial", 12), relief="solid", borderwidth=1, command=mostrar_ganancias).pack(pady=10)

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
    ventana_activa.geometry(f"{ancho_pantalla}x{alto_pantalla}")
    ventana_activa.state("zoomed")  
    ventana_activa.iconbitmap("logo.ico") 
    
    ventana_activa.grid_columnconfigure(1, weight=1)
    ventana_activa.grid_rowconfigure(0, weight=1)
    ventana_activa.bind('<Control-Alt-Shift-KeyPress-P>', no_importa)
    
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
    popup.resizable(False, False)
    
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
root.iconbitmap("logo.ico")  
root.withdraw()

def no_importa(event=None):
    ventana_easter = tk.Toplevel(root)
    ventana_easter.title("¡Easter Egg!")
    ventana_easter.resizable(False, False)
    ventana_easter.configure(bg="#fff0f6")
    tk.Label(ventana_easter, text="❤️", font=("Arial", 60), bg="#fff0f6", fg="#e63946").pack(padx=30, pady=(30,10))
    tk.Label(ventana_easter, text="¡Encontraste el corazón secreto de la Cerduladora!", font=("Arial", 16), bg="#fff0f6", fg="#e63946").pack(padx=20, pady=(0,30))
    ventana_easter.grab_set()
    centrar_ventana(ventana_easter)

#Se crea el menu principal
menu_principal = tk.Toplevel(root)
menu_principal.title("Cerduladora v1.1")
menu_principal.state("zoomed")  
menu_principal.iconbitmap("logo.ico")  

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()
menu_principal.geometry(f"{ancho_pantalla}x{alto_pantalla}")  


def prevent_maximize(event=None):
    if menu_principal.state() != 'zoomed':  # Si NO está maximizada
        menu_principal.state('zoomed')      # Fuerza a maximizarse

menu_principal.bind("<Map>", prevent_maximize)        # Al restaurar desde minimizado
menu_principal.bind("<Configure>", prevent_maximize)  # Al cambiar tamaño
menu_principal.bind('<Control-Alt-Shift-KeyPress-P>', no_importa)

boton_register = tk.Button(menu_principal, text="Registrarse", width=15, height=2)
boton_login = tk.Button(menu_principal, text="Iniciar sesion", width=15, height=2)

boton_register.place(relx=0.5, rely=0.46, anchor="center")
boton_login.place(relx=0.5, rely=0.54, anchor="center")      
boton_register.config(command=open_window_register)
boton_login.config(command=open_window_login)

menu_principal.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion(root))
root.mainloop() 