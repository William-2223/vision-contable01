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

class LibroMayor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Libro Mayor")
        self.geometry("1100x650")

        ctk.CTkLabel(self, text="Libro Mayor", font=("Arial", 24, "bold")).pack(pady=15)

        filtro = ctk.CTkFrame(self)
        filtro.pack(padx=20, pady=10, fill="x")

        self.cuentas = {}
        self.combo = ctk.CTkComboBox(filtro, width=400)
        self.combo.grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkButton(filtro, text="Cargar", command=self.generar).grid(row=0, column=1, padx=10)

        self.tabla = ttk.Treeview(
            self,
            columns=("Fecha", "Partida", "Concepto", "Debe", "Haber", "Saldo"),
            show="headings"
        )

        columnas = {
            "Fecha": 100,
            "Partida": 80,
            "Concepto": 300,
            "Debe": 120,
            "Haber": 120,
            "Saldo": 140
        }

        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho)

        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_saldo = ctk.CTkLabel(self, text="Saldo final: 0.00", font=("Arial", 16, "bold"))
        self.lbl_saldo.pack(pady=10)

        self.cargar_cuentas()

    def cargar_cuentas(self):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT IdCuenta, Codigo, Nombre, Tipo
            FROM CatalogoCuentas
            WHERE Activa = 1
            ORDER BY Codigo
        """)

        valores = []

        for id_cuenta, codigo, nombre, tipo in cursor.fetchall():
            texto = f"{codigo} - {nombre}"
            self.cuentas[texto] = (id_cuenta, tipo)
            valores.append(texto)

        self.combo.configure(values=valores)

        conn.close()

    def generar(self):
        seleccion = self.combo.get()

        if seleccion not in self.cuentas:
            messagebox.showerror("Error", "Seleccione una cuenta válida")
            return

        id_cuenta, tipo = self.cuentas[seleccion]

        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    P.Fecha,
                    P.IdPartida,
                    P.Concepto,
                    D.Debe,
                    D.Haber
                FROM PartidaDetalle D
                INNER JOIN Partidas P ON P.IdPartida = D.IdPartida
                WHERE D.IdCuenta = ?
                ORDER BY P.Fecha, P.IdPartida, D.IdDetalle
            """, (id_cuenta,))

            saldo = 0

            for fila in cursor.fetchall():
                fecha, partida, concepto, debe, haber = fila

                debe = float(debe or 0)
                haber = float(haber or 0)

                if tipo == "ACTIVO" or tipo == "GASTO" or tipo == "COSTO":
                    saldo += (debe - haber)
                else:
                    saldo += (haber - debe)

                self.tabla.insert("", "end", values=(
                    fecha,
                    partida,
                    concepto,
                    f"{debe:.2f}",
                    f"{haber:.2f}",
                    f"{saldo:.2f}"
                ))

            self.lbl_saldo.configure(text=f"Saldo final: {saldo:.2f}")

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = LibroMayor()
    app.mainloop()