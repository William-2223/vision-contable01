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


class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vision Contable")
        self.geometry("420x360")
        self.resizable(False, False)

        self._construir_ui()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, corner_radius=14)
        container.pack(padx=24, pady=24, fill="both", expand=True)

        ctk.CTkLabel(
            container,
            text="Vision Contable",
            font=("Arial", 26, "bold")
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            container,
            text="Inicio de sesión",
            font=("Arial", 14)
        ).pack(pady=(0, 16))

        self.entry_user = ctk.CTkEntry(container, placeholder_text="Usuario", width=280)
        self.entry_user.pack(pady=8)

        self.entry_pass = ctk.CTkEntry(container, placeholder_text="Contraseña", show="*", width=280)
        self.entry_pass.pack(pady=8)

        btn_login = ctk.CTkButton(container, text="Ingresar", command=self.login, width=280, height=40)
        btn_login.pack(pady=(16, 12))

        self.entry_user.focus()
        self.bind("<Return>", lambda _event: self.login())

    def login(self):
        usuario = self.entry_user.get().strip()
        clave = self.entry_pass.get()

        if not usuario or not clave:
            messagebox.showwarning("Aviso", "Ingrese usuario y contraseña")
            return

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

            if not resultado:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
                return

            nombre, rol = resultado
            self.destroy()

            menu = MenuPrincipal(nombre, rol)
            menu.mainloop()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
