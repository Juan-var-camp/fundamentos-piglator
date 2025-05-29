# Documentación de la Base de Datos - Proyecto Gestión de Piaras

Este documento describe en detalle la estructura, funciones y operaciones relacionadas con la base de datos en el sistema de gestión de piaras porcinas.

---

## 1. Inicialización y Conexión

El sistema utiliza SQLite3 como motor de base de datos local.  
La conexión se realiza con:

```python
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()
```

Esto crea (si no existe) y abre el archivo `usuarios.db` en el directorio del script.

---

## 2. Estructura de Tablas

### Tabla `users`

Almacena los datos de los usuarios, incluyendo credenciales y precios personalizados.

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
```

#### Columnas adicionales (agregadas con ALTER TABLE):

- `preiniciador` INTEGER DEFAULT 4250
- `iniciacion` INTEGER DEFAULT 3800
- `levante` INTEGER DEFAULT 3300
- `engorde` INTEGER DEFAULT 3000
- `precio_vivo_1` INTEGER DEFAULT 6000
- `precio_vivo_2` INTEGER DEFAULT 7000
- `precio_vivo_3` INTEGER DEFAULT 8000
- `precio_menudeo` INTEGER DEFAULT 11500

Estas columnas permiten que cada usuario tenga sus propios precios de alimentos y ventas.

#### Código de alteración:

```python
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
```

---

### Tabla `piaras`

Almacena los datos de cada piara registrada por los usuarios.

```sql
CREATE TABLE IF NOT EXISTS piaras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    tamaño INTEGER NOT NULL,
    semanas INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE (nombre, user_id)
)
```

- **nombre**: nombre de la piara (único por usuario)
- **tamaño**: cantidad de cerdos
- **semanas**: edad en semanas
- **user_id**: referencia al usuario propietario

---

## 3. Funciones Relacionadas con la Base de Datos

### Usuarios

#### Registrar usuario

```python
def registrar_usuario(entry_user_register, entry_password_register, entry_confirm_password_register, register_window):
    # Inserta un nuevo usuario en la tabla users
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
```

#### Login de usuario

```python
def login_usuario(entry_user_login, entry_password_login, login_window):
    # Busca el usuario y compara la contraseña encriptada
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    resultado = cursor.fetchone()
```

#### Actualizar contraseña

```python
def actualizar_contraseña(entry_password, entry_new_password, entry_password_confirmation, popup):
    # Actualiza la contraseña en la tabla users
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_new_password, usuario_actual))
    conn.commit()
```

#### Actualizar nombre de usuario

```python
def actualizar_nombre_usuario(entry_new_username, popup, nombre_usuario_var):
    cursor.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, usuario_actual))
    conn.commit()
```

#### Cargar precios personalizados del usuario

```python
def cargar_precios_usuario():
    cursor.execute("""
        SELECT preiniciador, iniciacion, levante, engorde, precio_vivo_1, precio_vivo_2, precio_vivo_3, precio_menudeo
        FROM users WHERE id = ?
    """, (usuario_actual,))
    datos = cursor.fetchone()
```

#### Actualizar precios personalizados

```python
def configuracion_avanzada():
    cursor.execute("""
        UPDATE users SET preiniciador=?, iniciacion=?, levante=?, engorde=?,
        precio_vivo_1=?, precio_vivo_2=?, precio_vivo_3=?, precio_menudeo=?
        WHERE id=?
    """, (preiniciador, iniciacion, levante, engorde, precio_vivo_1, precio_vivo_2, precio_vivo_3, precio_menudeo, usuario_actual))
    conn.commit()
```

---

### Piaras

#### Crear piara

```python
def crear_piara(entry_nombre_piara, entry_tamaño_piara, entry_semanas_piara, popup, callback_recarga=None):
    cursor.execute("INSERT INTO piaras (nombre, tamaño, semanas, user_id) VALUES (?, ?, ?, ?)", (nombre_piara, tamaño_piara, semanas_piara, usuario_actual))
    conn.commit()
```

#### Obtener piaras de un usuario

```python
def obtener_piaras_usuario(user_id):
    cursor.execute("SELECT id, nombre FROM piaras WHERE user_id = ?", (user_id,))
    return cursor.fetchall()
```

#### Eliminar piaras

```python
def eliminar_piaras(ids_piaras, listbox, callback_recarga=None):
    for piara_id in ids_piaras:
        cursor.execute("DELETE FROM piaras WHERE id = ? AND user_id = ?", (piara_id, usuario_actual))
    conn.commit()
```

#### Configurar (editar) piara

```python
def configurar_piara(piara_id, listbox, callback_recarga=None):
    cursor.execute("UPDATE piaras SET nombre=?, tamaño=?, semanas=? WHERE id=?", (nuevo_nombre, nuevo_tamaño, nuevas_semanas, piara_id))
    conn.commit()
```

---

## 4. Notas de Seguridad y Buenas Prácticas

- **Contraseñas**: Se almacenan encriptadas con SHA-256.
- **Integridad**: Uso de claves foráneas y restricciones UNIQUE para evitar duplicados.
- **Manejo de errores**: Uso de `try/except` para evitar fallos por columnas existentes o usuarios duplicados.
- **Commit**: Se realiza `conn.commit()` después de cada operación de escritura para asegurar la persistencia.

---

## 5. Resumen de Consultas SQL Utilizadas

- **CREATE TABLE**
- **ALTER TABLE**
- **INSERT INTO**
- **SELECT ... WHERE ...**
- **UPDATE ... SET ... WHERE ...**
- **DELETE FROM ... WHERE ...**

---

Esta documentación cubre toda la lógica y operaciones relacionadas con la base de datos en el proyecto.  
Si necesitas ejemplos de uso o explicación de alguna función específica, revisa el código fuente o consulta al desarrollador.