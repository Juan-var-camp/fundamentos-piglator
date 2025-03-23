import sqlite3
import hashlib

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL)
''')
conn.commit()

def register_user():
    username = input("Ingrese su nombre de usuario: ")
    password = input("Ingrese una contraseña: ")
    confirmation = input("Ingrese la contraseña nuevamente: ")
    if password == confirmation:    
        cifrar_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, cifrar_password))
            print("Usuario registrado exitosamente")
            conn.commit()
        except sqlite3.IntegrityError:
            print("Error, El usuario ya existe")
    
    
def login_user():
    username = input("Ingrese su usuario: ")
    password = input("Ingrese su contraseña: ")
    cifrar_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    resultado = cursor.fetchone()
    if resultado and resultado[0] == cifrar_password:
        print("Inicio de sesion exitoso")
        return True
    else:
        print("Usuario o contraseña incorrectos")
        return False
    
def menu_principal():
    while True:
        print("1. Registrarse")
        print("2. Inicio de sesion")
        print("3. salir")
        option = int(input("Elija una opcion: "))
        if option == 1:
            register_user()
        elif option == 2:
            login_user()
        elif option == 3:
            print("Saliendo del programa")
        else:
            print("opcion Invalida")
            
prueba = int(input(": "))
hola = int(input(": "))
            
if prueba == hola:
    menu_principal()
    conn.close
        
    