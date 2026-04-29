import customtkinter as ctk
from tkinter import messagebox
import pyodbc
from menu import MenuPrincipal

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def conectar():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\SQLEXPRESS;"
        "DATABASE=VisionContable;"
        "Trusted_Connection=yes;"
    )

def login():
    usuario = entry_user.get()
    clave = entry_pass.get()

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT Nombre, Rol
            FROM Usuarios
            WHERE Usuario = ? AND Clave = ? AND Activo = 1
            """,
            (usuario, clave)
        )

        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            nombre, rol = resultado
            app.destroy()

            menu = MenuPrincipal(nombre, rol)
            menu.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    except Exception as e:
        messagebox.showerror("Error", str(e))

app = ctk.CTk()
app.title("Vision Contable")
app.geometry("350x300")

titulo = ctk.CTkLabel(app, text="Vision Contable", font=("Arial", 22, "bold"))
titulo.pack(pady=25)

entry_user = ctk.CTkEntry(app, placeholder_text="Usuario", width=220)
entry_user.pack(pady=10)

entry_pass = ctk.CTkEntry(app, placeholder_text="Contraseña", show="*", width=220)
entry_pass.pack(pady=10)

btn_login = ctk.CTkButton(app, text="Ingresar", command=login, width=220)
btn_login.pack(pady=20)

app.mainloop()