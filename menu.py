import customtkinter as ctk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import pyodbc

from catalogo_cuentas import CatalogoCuentas
from partidas_contables import PartidasContables

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def conectar():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\SQLEXPRESS;"
        "DATABASE=VisionContable;"
        "Trusted_Connection=yes;"
    )


class MenuPrincipal(ctk.CTk):
    def __init__(self, nombre_usuario="Administrador", rol="ADMIN"):
        super().__init__()

        self.nombre_usuario = nombre_usuario
        self.rol = rol

        self.title("Vision Contable")
        self.geometry("1280x760")
        self.minsize(1180, 700)

        self.main_content = None
        self._construir_shell()
        self.mostrar_dashboard()

    def _construir_shell(self):
        layout = ctk.CTkFrame(self, corner_radius=0)
        layout.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(layout, width=250, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="Vision Contable", font=("Arial", 24, "bold")).pack(pady=(22, 2), padx=16)
        ctk.CTkLabel(sidebar, text="Estilo QuickBooks", font=("Arial", 12)).pack(pady=(0, 14), padx=16)

        self.nav_items = [
            "Dashboard",
            "Catálogo de cuentas",
            "Partidas contables",
            "Balance de saldos",
            "Estado de resultados",
            "Balance general",
            "Libro diario",
            "Libro mayor",
            "Salir",
        ]

        for item in self.nav_items:
            is_exit = item == "Salir"
            ctk.CTkButton(
                sidebar,
                text=item,
                width=210,
                height=38,
                anchor="w",
                fg_color=("#d9534f", "#b13f3b") if is_exit else None,
                hover_color=("#c64541", "#963633") if is_exit else None,
                command=lambda x=item: self.accion_navegacion(x),
            ).pack(pady=5, padx=18)

        right = ctk.CTkFrame(layout, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(right, corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Sistema Contable", font=("Arial", 24, "bold")).pack(side="left", padx=18)
        ctk.CTkLabel(header, text=f"Usuario: {self.nombre_usuario}  |  Rol: {self.rol}", font=("Arial", 13)).pack(side="right", padx=18)

        self.main_content = ctk.CTkFrame(right, corner_radius=0)
        self.main_content.pack(fill="both", expand=True, padx=16, pady=16)

    def _limpiar_contenido(self):
        for w in self.main_content.winfo_children():
            w.destroy()

    def _crear_card(self, parent, titulo, valor):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(side="left", fill="both", expand=True, padx=8)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 14)).pack(pady=(14, 4), padx=12, anchor="w")
        ctk.CTkLabel(card, text=valor, font=("Arial", 24, "bold")).pack(pady=(0, 14), padx=12, anchor="w")

    def mostrar_dashboard(self):
        self._limpiar_contenido()

        ctk.CTkLabel(self.main_content, text="Dashboard", font=("Arial", 28, "bold")).pack(anchor="w", pady=(0, 12))

        cards_row = ctk.CTkFrame(self.main_content, fg_color="transparent")
        cards_row.pack(fill="x", pady=(0, 10))

        total_activo, total_pasivo, total_patrimonio, diferencia = self._obtener_totales_dashboard()
        self._crear_card(cards_row, "Total activo", f"{total_activo:.2f}")
        self._crear_card(cards_row, "Total pasivo", f"{total_pasivo:.2f}")
        self._crear_card(cards_row, "Total patrimonio", f"{total_patrimonio:.2f}")
        self._crear_card(cards_row, "Diferencia contable", f"{diferencia:.2f}")

        actions = ctk.CTkFrame(self.main_content)
        actions.pack(fill="x", pady=(6, 10))
        ctk.CTkLabel(actions, text="Acciones rápidas", font=("Arial", 16, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        quick = ctk.CTkFrame(actions, fg_color="transparent")
        quick.pack(fill="x", padx=8, pady=(0, 12))
        ctk.CTkButton(quick, text="Nueva partida", width=170, command=lambda: self.accion_navegacion("Partidas contables")).pack(side="left", padx=6)
        ctk.CTkButton(quick, text="Nueva cuenta", width=170, command=lambda: self.accion_navegacion("Catálogo de cuentas")).pack(side="left", padx=6)
        ctk.CTkButton(quick, text="Ver libro diario", width=170, command=lambda: self.accion_navegacion("Libro diario")).pack(side="left", padx=6)

        ultimas = ctk.CTkFrame(self.main_content)
        ultimas.pack(fill="both", expand=True, pady=(8, 0))
        ctk.CTkLabel(ultimas, text="Últimas partidas registradas", font=("Arial", 16, "bold")).pack(anchor="w", padx=12, pady=(10, 8))

        tabla_frame = ctk.CTkFrame(ultimas)
        tabla_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        tabla = ttk.Treeview(tabla_frame, columns=("IdPartida", "Fecha", "Concepto", "Usuario"), show="headings")
        for col, ancho in {"IdPartida": 120, "Fecha": 150, "Concepto": 540, "Usuario": 150}.items():
            tabla.heading(col, text=col)
            tabla.column(col, width=ancho, anchor="center")

        sb = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=sb.set)
        tabla.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        sb.pack(side="right", fill="y", padx=(0, 8), pady=8)

        for fila in self._obtener_ultimas_partidas():
            tabla.insert("", "end", values=fila)

    def _obtener_totales_dashboard(self):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    C.Tipo,
                    CASE 
                        WHEN C.Tipo = 'ACTIVO' THEN SUM(D.Debe) - SUM(D.Haber)
                        WHEN C.Tipo IN ('PASIVO', 'PATRIMONIO') THEN SUM(D.Haber) - SUM(D.Debe)
                        ELSE 0
                    END AS Saldo
                FROM PartidaDetalle D
                INNER JOIN Partidas P ON P.IdPartida = D.IdPartida
                INNER JOIN CatalogoCuentas C ON C.IdCuenta = D.IdCuenta
                WHERE C.Tipo IN ('ACTIVO', 'PASIVO', 'PATRIMONIO')
                GROUP BY C.Tipo
            """)
            total_activo = total_pasivo = total_patrimonio = 0
            for tipo, saldo in cursor.fetchall():
                saldo = float(saldo or 0)
                if tipo == "ACTIVO":
                    total_activo += saldo
                elif tipo == "PASIVO":
                    total_pasivo += saldo
                elif tipo == "PATRIMONIO":
                    total_patrimonio += saldo
            conn.close()
            return total_activo, total_pasivo, total_patrimonio, total_activo - (total_pasivo + total_patrimonio)
        except Exception:
            return 0, 0, 0, 0

    def _obtener_ultimas_partidas(self):
        try:
            conn = conectar(); cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 10 IdPartida, Fecha, Concepto, Usuario
                FROM Partidas
                ORDER BY IdPartida DESC
            """)
            filas = cursor.fetchall()
            conn.close()
            return filas
        except Exception:
            return []

    def abrir_archivo(self, nombre_archivo):
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), nombre_archivo)
        subprocess.Popen([sys.executable, ruta])

    def accion_navegacion(self, opcion):
        if opcion == "Salir":
            self.destroy()
        elif opcion == "Dashboard":
            self.mostrar_dashboard()
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
            messagebox.showwarning("Aviso", f"Módulo no disponible: {opcion}")


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()
