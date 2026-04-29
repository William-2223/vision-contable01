import customtkinter as ctk
from tkinter import ttk, messagebox
import pyodbc


def conectar():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\SQLEXPRESS;"
        "DATABASE=VisionContable;"
        "Trusted_Connection=yes;"
    )


class CatalogoCuentas(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("Catálogo de cuentas")
        self.geometry("980x620")
        self.minsize(920, 560)

        self._construir_ui()
        self.cargar_datos()

    def _construir_ui(self):
        ctk.CTkLabel(self, text="Catálogo de cuentas", font=("Arial", 26, "bold")).pack(pady=(18, 4))
        ctk.CTkLabel(self, text="Registro y consulta de cuentas contables", font=("Arial", 13)).pack(pady=(0, 10))

        contenedor = ctk.CTkFrame(self, corner_radius=14)
        contenedor.pack(pady=(0, 16), padx=20, fill="both", expand=True)

        form = ctk.CTkFrame(contenedor)
        form.pack(pady=16, padx=16, fill="x")

        self.codigo = ctk.CTkEntry(form, placeholder_text="Código", width=140)
        self.codigo.grid(row=0, column=0, padx=8, pady=10)

        self.nombre = ctk.CTkEntry(form, placeholder_text="Nombre", width=250)
        self.nombre.grid(row=0, column=1, padx=8, pady=10)

        self.tipo = ctk.CTkComboBox(
            form,
            values=["ACTIVO", "PASIVO", "PATRIMONIO", "INGRESO", "COSTO", "GASTO"],
            width=170
        )
        self.tipo.grid(row=0, column=2, padx=8, pady=10)
        self.tipo.set("ACTIVO")

        self.naturaleza = ctk.CTkComboBox(form, values=["DEUDORA", "ACREEDORA"], width=150)
        self.naturaleza.grid(row=0, column=3, padx=8, pady=10)
        self.naturaleza.set("DEUDORA")

        ctk.CTkButton(form, text="Guardar", width=120, command=self.guardar).grid(row=0, column=4, padx=8, pady=10)

        tabla_frame = ctk.CTkFrame(contenedor)
        tabla_frame.pack(padx=16, pady=(0, 16), fill="both", expand=True)

        self.tabla = ttk.Treeview(tabla_frame, columns=("Codigo", "Nombre", "Tipo", "Naturaleza", "Activa"), show="headings")

        columnas = {
            "Codigo": 120,
            "Nombre": 300,
            "Tipo": 140,
            "Naturaleza": 140,
            "Activa": 90,
        }

        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

    def guardar(self):
        codigo = self.codigo.get().strip()
        nombre = self.nombre.get().strip()
        tipo = self.tipo.get().strip()
        naturaleza = self.naturaleza.get().strip()

        if not codigo or not nombre:
            messagebox.showwarning("Aviso", "Ingrese código y nombre")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO CatalogoCuentas (Codigo, Nombre, Tipo, Naturaleza)
                VALUES (?, ?, ?, ?)
                """,
                (codigo, nombre, tipo, naturaleza)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo("Correcto", "Cuenta guardada")
            self.limpiar()
            self.cargar_datos()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT Codigo, Nombre, Tipo, Naturaleza, Activa
            FROM CatalogoCuentas
            ORDER BY Codigo
            """
        )

        for fila in cursor.fetchall():
            self.tabla.insert("", "end", values=tuple(fila))

        conn.close()

    def limpiar(self):
        self.codigo.delete(0, "end")
        self.nombre.delete(0, "end")
        self.codigo.focus()
