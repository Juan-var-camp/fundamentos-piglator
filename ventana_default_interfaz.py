import tkinter as tk

def main():
    ventana = tk.Tk()
    ventana.title("Sidebar Example")
    
    ventana.attributes('-fullscreen', True)  # <-- Nueva línea clave
    
    ventana.grid_columnconfigure(1, weight=1)
    ventana.grid_rowconfigure(0, weight=1)

    sidebar = tk.Frame(ventana, bg="#2C3E50", width=200)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_rowconfigure(3, weight=1)

    content = tk.Frame(ventana, bg="#ECF0F1")
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

    btn_exit = tk.Button(content, text="Salir (ESC)", command=ventana.destroy)
    btn_exit.grid(row=1, column=0)
    
    ventana.bind('<Escape>', lambda e: ventana.destroy())

    ventana.mainloop()

if __name__ == "__main__":
    main()