import customtkinter as ctk
import subprocess
import sys
import os

from catalogo_cuentas import CatalogoCuentas
from partidas_contables import PartidasContables

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MenuPrincipal(ctk.CTk):
    def __init__(self, nombre_usuario="Administrador", rol="ADMIN"):
        super().__init__()

        self.nombre_usuario = nombre_usuario
        self.rol = rol

        self.title("Vision Contable - Menú Principal")
        self.geometry("900x650")

        ctk.CTkLabel(
            self,
            text="Vision Contable",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        ctk.CTkLabel(
            self,
            text=f"Usuario: {nombre_usuario} | Rol: {rol}",
            font=("Arial", 14)
        ).pack(pady=5)

        frame = ctk.CTkFrame(self)
        frame.pack(pady=30, padx=30, fill="both", expand=True)

        opciones = [
            "Catálogo de cuentas",
            "Partidas contables",
            "Balance de saldos",
            "Estado de resultados",
            "Balance general",
            "Libro diario",
            "Libro mayor",
            "Salir"
        ]

        for opcion in opciones:
            ctk.CTkButton(
                frame,
                text=opcion,
                width=250,
                height=40,
                command=lambda x=opcion: self.accion(x)
            ).pack(pady=8)

    def abrir_archivo(self, nombre_archivo):
        ruta = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            nombre_archivo
        )
        subprocess.Popen([sys.executable, ruta])

    def accion(self, opcion):
        opcion = opcion.strip()

        if opcion == "Salir":
            self.destroy()

        elif opcion == "Catálogo de cuentas":
            CatalogoCuentas()

        elif opcion == "Partidas contables":
            PartidasContables(self.nombre_usuario)

        elif opcion == "Balance de saldos":
            self.abrir_archivo("balance_saldos.py")

        elif opcion == "Estado de resultados":
            self.abrir_archivo("estado_resultados.py")

        elif opcion == "Balance general":
            self.abrir_archivo("balance_general.py")

        elif opcion == "Libro diario":
            self.abrir_archivo("libro_diario.py")

        elif opcion == "Libro mayor":
            self.abrir_archivo("libro_mayor.py")

        else:
            print("Opción no conectada:", repr(opcion))


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()