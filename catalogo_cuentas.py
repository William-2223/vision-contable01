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
        self.geometry("850x500")

        ctk.CTkLabel(self, text="Catálogo de cuentas", font=("Arial", 22, "bold")).pack(pady=15)

        form = ctk.CTkFrame(self)
        form.pack(pady=10, padx=20, fill="x")

        self.codigo = ctk.CTkEntry(form, placeholder_text="Código")
        self.codigo.grid(row=0, column=0, padx=10, pady=10)

        self.nombre = ctk.CTkEntry(form, placeholder_text="Nombre", width=250)
        self.nombre.grid(row=0, column=1, padx=10, pady=10)

        self.tipo = ctk.CTkComboBox(form, values=["ACTIVO", "PASIVO", "PATRIMONIO", "INGRESO", "COSTO", "GASTO"])
        self.tipo.grid(row=0, column=2, padx=10, pady=10)

        self.naturaleza = ctk.CTkComboBox(form, values=["DEUDORA", "ACREEDORA"])
        self.naturaleza.grid(row=0, column=3, padx=10, pady=10)

        ctk.CTkButton(form, text="Guardar", command=self.guardar).grid(row=0, column=4, padx=10)

        self.tabla = ttk.Treeview(
            self,
            columns=("Codigo", "Nombre", "Tipo", "Naturaleza", "Activa"),
            show="headings"
        )

        for col in ("Codigo", "Nombre", "Tipo", "Naturaleza", "Activa"):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=140)

        self.tabla.pack(padx=20, pady=20, fill="both", expand=True)

        self.cargar_datos()

    def guardar(self):
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO CatalogoCuentas (Codigo, Nombre, Tipo, Naturaleza)
                VALUES (?, ?, ?, ?)
            """, (
                self.codigo.get(),
                self.nombre.get(),
                self.tipo.get(),
                self.naturaleza.get()
            ))

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
        cursor.execute("""
            SELECT Codigo, Nombre, Tipo, Naturaleza, Activa
            FROM CatalogoCuentas
            ORDER BY Codigo
        """)

        for fila in cursor.fetchall():
            self.tabla.insert("", "end", values=tuple(fila))

        conn.close()

    def limpiar(self):
        self.codigo.delete(0, "end")
        self.nombre.delete(0, "end")