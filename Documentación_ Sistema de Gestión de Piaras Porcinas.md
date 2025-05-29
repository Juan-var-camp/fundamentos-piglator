Documentación: Sistema de Gestión de Piaras 

Descripción general  
Este programa es una aplicación de escritorio desarrollada en Python con Tkinter y SQLite3, diseñada para gestionar piaras de cerdos, calcular gastos y ganancias, y administrar usuarios. Permite a los usuarios registrar piaras, calcular proyecciones de gastos e ingresos, y personalizar precios de alimentos y ventas.

Módulos y librerías

* **sqlite3**: Manejo de la base de datos local para usuarios y piaras.  
* **hashlib**: Encriptación de contraseñas de usuarios.  
* **tkinter**: Interfaz gráfica de usuario (ventanas, botones, entradas, etc.).  
* **tkinter.messagebox**: Ventanas emergentes para mensajes y errores.  
* **tkinter.filedialog**: Diálogos para guardar archivos (exportar reportes).

Estructura de la Base de Datos

* **Tabla users**: Almacena usuarios, contraseñas (encriptadas) y precios personalizados.  
* **Tabla piaras**: Almacena piaras con nombre, tamaño, semanas y relación con el usuario.

Variables Globales

* **ventana\_activa**: Referencia a la ventana principal activa.  
* **usuario\_actual**: ID del usuario actualmente autenticado.  
* **nombre\_usuario**: Nombre del usuario autenticado.  
* **Precios y costos de alimentos y ventas** (pueden ser personalizados por usuario).

Funcionalidades Principales

1. Gestión de Usuarios  
* **Registro**: Permite crear nuevos usuarios con contraseña encriptada.  
* **Login**: Autenticación de usuarios.  
* **Cambio de contraseña y nombre de usuario**: Con validaciones y actualización en la base de datos.  
* **Personalización de precios**: Cada usuario puede modificar precios de alimentos y ventas.

2. Gestión de Piaras  
* **Crear piara**: Añadir nuevas piaras con nombre, tamaño y semanas.  
* **Eliminar piaras**: Borrar una o varias piaras seleccionadas.  
* **Configurar piara**: Editar nombre, tamaño y semanas de una piara existente.

3. Cálculo de Gastos y Ganancias  
* **Gastos**: Calcula el gasto total en alimentos y medicamentos para las piaras seleccionadas.  
* **Ganancias**: Calcula el retorno y la ganancia potencial según el tipo de venta (vivo o menudeo).  
* **Exportar reporte**: Permite guardar un reporte TXT con los datos de gastos.

4. Interfaz Gráfica  
* **Ventanas principales**: Menú de inicio, gastos, ganancias, perfil.  
* **Ventanas emergentes**: Para login, registro, cambio de contraseña, creación y edición de piaras.  
* **Barra lateral**: Navegación entre perfil, gastos y ganancias.


Funciones Clave

* **validar\_campos\_obligatorios**: Verifica que los campos requeridos no estén vacíos.  
* **cargar\_precios\_usuario**: Carga los precios personalizados del usuario desde la base de datos.  
* **calcular\_gastos\_piaras**: Calcula el gasto total en alimentos y medicamentos para las piaras seleccionadas.  
* **calcular\_ganancias\_piaras**: Calcula el retorno y la ganancia según el tipo de venta.  
* **configuracion\_avanzada:** Permite modificar los precios de alimentos y ventas.  
* **contenido\_gastos / contenido\_ganancias / contenido\_perfil**: Generan el contenido central de cada ventana principal.  
* **generar\_contenido\_ventana**: Crea la estructura de una ventana principal con barra lateral y contenido central.  
* **crear\_ventana\_emergente**: Crea ventanas emergentes para formularios y configuraciones.

Flujo de la Aplicación

1. **Inicio**: Se muestra el menú principal con opciones para registrarse o iniciar sesión.  
2. **Login/Registro**: El usuario se autentica o se registra.  
3. **Ventana principal**: El usuario navega entre gastos, ganancias y perfil.  
4. **Gestión de piaras**: Puede crear, editar, eliminar piaras y calcular gastos/ganancias.  
5. **Configuración avanzada**: Puede personalizar precios.  
6. **Exportar reportes:** Puede guardar reportes de gastos en TXT.

