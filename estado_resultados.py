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

class EstadoResultados(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Estado de Resultados")
        self.geometry("900x600")

        ctk.CTkLabel(self, text="Estado de Resultados", font=("Arial", 24, "bold")).pack(pady=15)

        self.tabla = ttk.Treeview(
            self,
            columns=("Tipo", "Codigo", "Cuenta", "Saldo"),
            show="headings"
        )

        for col in ("Tipo", "Codigo", "Cuenta", "Saldo"):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=200)

        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_total = ctk.CTkLabel(self, text="", font=("Arial", 18, "bold"))
        self.lbl_total.pack(pady=10)

        self.generar()

    def generar(self):
        try:
            conn = conectar()
            cursor = conn.cursor()

            query = """
                SELECT 
                    C.Tipo,
                    C.Codigo,
                    C.Nombre,
                    SUM(D.Haber) - SUM(D.Debe) AS Saldo
                FROM PartidaDetalle D
                INNER JOIN Partidas P ON P.IdPartida = D.IdPartida
                INNER JOIN CatalogoCuentas C ON C.IdCuenta = D.IdCuenta
                WHERE C.Tipo IN ('INGRESO', 'COSTO', 'GASTO')
                GROUP BY C.Tipo, C.Codigo, C.Nombre
                ORDER BY C.Tipo, C.Codigo
            """

            cursor.execute(query)

            total_ingresos = 0
            total_costos = 0
            total_gastos = 0

            for fila in cursor.fetchall():
                tipo, codigo, nombre, saldo = fila
                saldo = float(saldo or 0)

                self.tabla.insert("", "end", values=(
                    tipo,
                    codigo,
                    nombre,
                    f"{saldo:.2f}"
                ))

                if tipo == "INGRESO":
                    total_ingresos += saldo
                elif tipo == "COSTO":
                    total_costos += saldo
                elif tipo == "GASTO":
                    total_gastos += saldo

            utilidad = total_ingresos - total_costos - total_gastos

            self.lbl_total.configure(
                text=f"Ingresos: {total_ingresos:.2f} | Costos: {total_costos:.2f} | Gastos: {total_gastos:.2f} | Utilidad: {utilidad:.2f}"
            )

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = EstadoResultados()
    app.mainloop()