import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
import pyodbc


def conectar():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.\\SQLEXPRESS;"
        "DATABASE=VisionContable;"
        "Trusted_Connection=yes;"
    )


class PartidasContables(ctk.CTkToplevel):
    def __init__(self, usuario="admin"):
        super().__init__()

        self.usuario = usuario
        self.detalles = []
        self.cuentas = {}

        self.title("Partidas contables")
        self.geometry("1160x720")
        self.minsize(1100, 680)

        self._construir_ui()

    def _construir_ui(self):
        ctk.CTkLabel(self, text="Partidas contables", font=("Arial", 26, "bold")).pack(pady=(16, 4))
        ctk.CTkLabel(self, text=f"Usuario: {self.usuario}", font=("Arial", 13)).pack(pady=(0, 10))

        root_frame = ctk.CTkFrame(self, corner_radius=14)
        root_frame.pack(padx=20, pady=(0, 16), fill="both", expand=True)

        encabezado = ctk.CTkFrame(root_frame)
        encabezado.pack(padx=16, pady=(14, 8), fill="x")

        ctk.CTkLabel(encabezado, text="Encabezado de la partida", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(10, 2))

        self.fecha = ctk.CTkEntry(encabezado, placeholder_text="Fecha YYYY-MM-DD", width=160)
        self.fecha.insert(0, str(date.today()))
        self.fecha.grid(row=1, column=0, padx=8, pady=10)

        self.concepto = ctk.CTkEntry(encabezado, placeholder_text="Concepto de la partida", width=780)
        self.concepto.grid(row=1, column=1, padx=8, pady=10)

        detalle = ctk.CTkFrame(root_frame)
        detalle.pack(padx=16, pady=8, fill="x")

        ctk.CTkLabel(detalle, text="Detalle de líneas", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=5, sticky="w", padx=8, pady=(10, 2))

        self.cargar_cuentas()

        self.combo_cuenta = ctk.CTkComboBox(detalle, values=list(self.cuentas.keys()), width=350)
        self.combo_cuenta.grid(row=1, column=0, padx=8, pady=10)

        self.debe = ctk.CTkEntry(detalle, placeholder_text="Debe", width=120)
        self.debe.grid(row=1, column=1, padx=8, pady=10)

        self.haber = ctk.CTkEntry(detalle, placeholder_text="Haber", width=120)
        self.haber.grid(row=1, column=2, padx=8, pady=10)

        self.descripcion = ctk.CTkEntry(detalle, placeholder_text="Descripción", width=300)
        self.descripcion.grid(row=1, column=3, padx=8, pady=10)

        ctk.CTkButton(detalle, text="Agregar línea", width=130, command=self.agregar_linea).grid(row=1, column=4, padx=8, pady=10)

        tabla_frame = ctk.CTkFrame(root_frame)
        tabla_frame.pack(padx=16, pady=8, fill="both", expand=True)

        self.tabla = ttk.Treeview(tabla_frame, columns=("Cuenta", "Debe", "Haber", "Descripcion"), show="headings")

        columnas = {
            "Cuenta": 420,
            "Debe": 130,
            "Haber": 130,
            "Descripcion": 380,
        }
        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        scrollbar_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        scrollbar_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tabla.pack(side="top", fill="both", expand=True, padx=8, pady=(8, 0))
        scrollbar_x.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        scrollbar_y.pack(side="right", fill="y", padx=(0, 8), pady=8)

        totales = ctk.CTkFrame(root_frame)
        totales.pack(padx=16, pady=8, fill="x")

        self.lbl_debe = ctk.CTkLabel(totales, text="Total debe: 0.00", font=("Arial", 15, "bold"))
        self.lbl_debe.pack(side="left", padx=20)

        self.lbl_haber = ctk.CTkLabel(totales, text="Total haber: 0.00", font=("Arial", 15, "bold"))
        self.lbl_haber.pack(side="left", padx=20)

        self.lbl_diferencia = ctk.CTkLabel(totales, text="Diferencia: 0.00", font=("Arial", 15, "bold"))
        self.lbl_diferencia.pack(side="left", padx=20)

        botones = ctk.CTkFrame(root_frame)
        botones.pack(padx=16, pady=(8, 14), fill="x")

        ctk.CTkButton(botones, text="Guardar partida", command=self.guardar_partida).pack(side="left", padx=8)
        ctk.CTkButton(botones, text="Eliminar línea seleccionada", command=self.eliminar_linea).pack(side="left", padx=8)
        ctk.CTkButton(botones, text="Limpiar", command=self.limpiar_todo).pack(side="left", padx=8)

    def cargar_cuentas(self):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT IdCuenta, Codigo, Nombre
            FROM CatalogoCuentas
            WHERE Activa = 1
            ORDER BY Codigo
            """
        )

        for id_cuenta, codigo, nombre in cursor.fetchall():
            texto = f"{codigo} - {nombre}"
            self.cuentas[texto] = id_cuenta

        conn.close()

    def convertir_numero(self, valor):
        if valor.strip() == "":
            return 0.00
        return float(valor.replace(",", ""))

    def agregar_linea(self):
        try:
            cuenta_texto = self.combo_cuenta.get()
            debe = self.convertir_numero(self.debe.get())
            haber = self.convertir_numero(self.haber.get())
            descripcion = self.descripcion.get().strip()

            if cuenta_texto not in self.cuentas:
                messagebox.showerror("Error", "Seleccione una cuenta válida del catálogo")
                return

            if debe > 0 and haber > 0:
                messagebox.showerror("Error", "Una línea no puede tener Debe y Haber al mismo tiempo")
                return

            if debe == 0 and haber == 0:
                messagebox.showerror("Error", "Debe ingresar un valor en Debe o Haber")
                return

            linea = {
                "cuenta_texto": cuenta_texto,
                "id_cuenta": self.cuentas[cuenta_texto],
                "debe": debe,
                "haber": haber,
                "descripcion": descripcion,
            }

            self.detalles.append(linea)

            self.tabla.insert("", "end", values=(cuenta_texto, f"{debe:.2f}", f"{haber:.2f}", descripcion))

            self.debe.delete(0, "end")
            self.haber.delete(0, "end")
            self.descripcion.delete(0, "end")

            self.actualizar_totales()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_linea(self):
        seleccionado = self.tabla.selection()

        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccione una línea")
            return

        index = self.tabla.index(seleccionado[0])
        self.tabla.delete(seleccionado[0])
        self.detalles.pop(index)

        self.actualizar_totales()

    def actualizar_totales(self):
        total_debe = sum(x["debe"] for x in self.detalles)
        total_haber = sum(x["haber"] for x in self.detalles)
        diferencia = total_debe - total_haber

        self.lbl_debe.configure(text=f"Total debe: {total_debe:.2f}")
        self.lbl_haber.configure(text=f"Total haber: {total_haber:.2f}")
        self.lbl_diferencia.configure(text=f"Diferencia: {diferencia:.2f}")

    def guardar_partida(self):
        if self.concepto.get().strip() == "":
            messagebox.showerror("Datos incompletos", "Ingrese el concepto de la partida")
            return

        if len(self.detalles) < 2:
            messagebox.showerror("Error", "La partida debe tener al menos dos líneas")
            return

        total_debe = sum(x["debe"] for x in self.detalles)
        total_haber = sum(x["haber"] for x in self.detalles)

        if round(total_debe, 2) != round(total_haber, 2):
            messagebox.showerror("Error", "La partida no cuadra. Debe y Haber deben ser iguales.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO Partidas (Fecha, Concepto, Usuario)
                OUTPUT INSERTED.IdPartida
                VALUES (?, ?, ?)
                """,
                (self.fecha.get(), self.concepto.get(), self.usuario),
            )

            id_partida = cursor.fetchone()[0]

            for linea in self.detalles:
                cursor.execute(
                    """
                    INSERT INTO PartidaDetalle
                    (IdPartida, IdCuenta, Debe, Haber, Descripcion)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        id_partida,
                        linea["id_cuenta"],
                        linea["debe"],
                        linea["haber"],
                        linea["descripcion"],
                    ),
                )

            conn.commit()
            conn.close()

            messagebox.showinfo("Correcto", f"Partida guardada No. {id_partida}")
            self.limpiar_todo()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def limpiar_todo(self):
        self.concepto.delete(0, "end")
        self.debe.delete(0, "end")
        self.haber.delete(0, "end")
        self.descripcion.delete(0, "end")
        self.detalles.clear()

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        self.actualizar_totales()
