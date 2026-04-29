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

class BalanceGeneral(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Balance General")
        self.geometry("950x600")

        ctk.CTkLabel(
            self,
            text="Balance General",
            font=("Arial", 24, "bold")
        ).pack(pady=15)

        self.tabla = ttk.Treeview(
            self,
            columns=("Tipo", "Codigo", "Cuenta", "Saldo"),
            show="headings"
        )

        for col in ("Tipo", "Codigo", "Cuenta", "Saldo"):
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=200)

        self.tabla.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_total = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 17, "bold")
        )
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
                    CASE 
                        WHEN C.Tipo = 'ACTIVO'
                            THEN SUM(D.Debe) - SUM(D.Haber)
                        WHEN C.Tipo IN ('PASIVO', 'PATRIMONIO')
                            THEN SUM(D.Haber) - SUM(D.Debe)
                        ELSE 0
                    END AS Saldo
                FROM PartidaDetalle D
                INNER JOIN Partidas P ON P.IdPartida = D.IdPartida
                INNER JOIN CatalogoCuentas C ON C.IdCuenta = D.IdCuenta
                WHERE C.Tipo IN ('ACTIVO', 'PASIVO', 'PATRIMONIO')
                GROUP BY C.Tipo, C.Codigo, C.Nombre
                ORDER BY 
                    CASE 
                        WHEN C.Tipo = 'ACTIVO' THEN 1
                        WHEN C.Tipo = 'PASIVO' THEN 2
                        WHEN C.Tipo = 'PATRIMONIO' THEN 3
                    END,
                    C.Codigo
            """

            cursor.execute(query)

            total_activo = 0
            total_pasivo = 0
            total_patrimonio = 0

            for fila in cursor.fetchall():
                tipo, codigo, nombre, saldo = fila
                saldo = float(saldo or 0)

                self.tabla.insert("", "end", values=(
                    tipo,
                    codigo,
                    nombre,
                    f"{saldo:.2f}"
                ))

                if tipo == "ACTIVO":
                    total_activo += saldo
                elif tipo == "PASIVO":
                    total_pasivo += saldo
                elif tipo == "PATRIMONIO":
                    total_patrimonio += saldo

            diferencia = total_activo - (total_pasivo + total_patrimonio)

            self.lbl_total.configure(
                text=(
                    f"Activo: {total_activo:.2f} | "
                    f"Pasivo: {total_pasivo:.2f} | "
                    f"Patrimonio: {total_patrimonio:.2f} | "
                    f"Diferencia: {diferencia:.2f}"
                )
            )

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = BalanceGeneral()
    app.mainloop()