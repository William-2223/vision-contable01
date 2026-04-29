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

class LibroDiario(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Libro Diario")
        self.geometry("1150x650")

        ctk.CTkLabel(
            self,
            text="Libro Diario",
            font=("Arial", 24, "bold")
        ).pack(pady=15)

        filtros = ctk.CTkFrame(self)
        filtros.pack(padx=20, pady=10, fill="x")

        self.fecha_inicio = ctk.CTkEntry(
            filtros,
            placeholder_text="Fecha inicio YYYY-MM-DD",
            width=180
        )
        self.fecha_inicio.grid(row=0, column=0, padx=10, pady=10)

        self.fecha_fin = ctk.CTkEntry(
            filtros,
            placeholder_text="Fecha fin YYYY-MM-DD",
            width=180
        )
        self.fecha_fin.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(
            filtros,
            text="Generar",
            command=self.generar
        ).grid(row=0, column=2, padx=10)

        self.tabla = ttk.Treeview(
            self,
            columns=("Fecha", "Partida", "Concepto", "Cuenta", "Debe", "Haber", "Descripcion", "Usuario"),
            show="headings"
        )

        columnas = {
            "Fecha": 100,
            "Partida": 80,
            "Concepto": 230,
            "Cuenta": 220,
            "Debe": 100,
            "Haber": 100,
            "Descripcion": 220,
            "Usuario": 120
        }

        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho)

        self.tabla.pack(padx=20, pady=15, fill="both", expand=True)

        totales = ctk.CTkFrame(self)
        totales.pack(padx=20, pady=10, fill="x")

        self.lbl_debe = ctk.CTkLabel(
            totales,
            text="Total debe: 0.00",
            font=("Arial", 15, "bold")
        )
        self.lbl_debe.pack(side="left", padx=20)

        self.lbl_haber = ctk.CTkLabel(
            totales,
            text="Total haber: 0.00",
            font=("Arial", 15, "bold")
        )
        self.lbl_haber.pack(side="left", padx=20)

        self.lbl_diferencia = ctk.CTkLabel(
            totales,
            text="Diferencia: 0.00",
            font=("Arial", 15, "bold")
        )
        self.lbl_diferencia.pack(side="left", padx=20)

        self.generar()

    def generar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conn = conectar()
            cursor = conn.cursor()

            query = """
                SELECT
                    P.Fecha,
                    P.IdPartida,
                    P.Concepto,
                    C.Codigo + ' - ' + C.Nombre AS Cuenta,
                    D.Debe,
                    D.Haber,
                    ISNULL(D.Descripcion, '') AS Descripcion,
                    P.Usuario
                FROM Partidas P
                INNER JOIN PartidaDetalle D ON D.IdPartida = P.IdPartida
                INNER JOIN CatalogoCuentas C ON C.IdCuenta = D.IdCuenta
                WHERE 1 = 1
            """

            parametros = []

            if self.fecha_inicio.get().strip():
                query += " AND P.Fecha >= ?"
                parametros.append(self.fecha_inicio.get().strip())

            if self.fecha_fin.get().strip():
                query += " AND P.Fecha <= ?"
                parametros.append(self.fecha_fin.get().strip())

            query += """
                ORDER BY P.Fecha, P.IdPartida, D.IdDetalle
            """

            cursor.execute(query, parametros)

            total_debe = 0
            total_haber = 0

            for fila in cursor.fetchall():
                fecha, partida, concepto, cuenta, debe, haber, descripcion, usuario = fila

                debe = float(debe or 0)
                haber = float(haber or 0)

                total_debe += debe
                total_haber += haber

                self.tabla.insert("", "end", values=(
                    fecha,
                    partida,
                    concepto,
                    cuenta,
                    f"{debe:.2f}",
                    f"{haber:.2f}",
                    descripcion,
                    usuario
                ))

            diferencia = total_debe - total_haber

            self.lbl_debe.configure(text=f"Total debe: {total_debe:.2f}")
            self.lbl_haber.configure(text=f"Total haber: {total_haber:.2f}")
            self.lbl_diferencia.configure(text=f"Diferencia: {diferencia:.2f}")

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = LibroDiario()
    app.mainloop()