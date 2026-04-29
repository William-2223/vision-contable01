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

class BalanceSaldos(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Balance de saldos")
        self.geometry("1000x600")

        ctk.CTkLabel(
            self,
            text="Balance de saldos",
            font=("Arial", 24, "bold")
        ).pack(pady=15)

        filtros = ctk.CTkFrame(self)
        filtros.pack(padx=20, pady=10, fill="x")

        self.fecha_inicio = ctk.CTkEntry(filtros, placeholder_text="Fecha inicio YYYY-MM-DD", width=180)
        self.fecha_inicio.grid(row=0, column=0, padx=10, pady=10)

        self.fecha_fin = ctk.CTkEntry(filtros, placeholder_text="Fecha fin YYYY-MM-DD", width=180)
        self.fecha_fin.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(filtros, text="Generar", command=self.generar).grid(row=0, column=2, padx=10)

        self.tabla = ttk.Treeview(
            self,
            columns=("Codigo", "Cuenta", "Tipo", "Debe", "Haber", "SaldoDeudor", "SaldoAcreedor"),
            show="headings"
        )

        columnas = {
            "Codigo": 90,
            "Cuenta": 250,
            "Tipo": 120,
            "Debe": 120,
            "Haber": 120,
            "SaldoDeudor": 140,
            "SaldoAcreedor": 140
        }

        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho)

        self.tabla.pack(padx=20, pady=15, fill="both", expand=True)

        totales = ctk.CTkFrame(self)
        totales.pack(padx=20, pady=10, fill="x")

        self.lbl_debe = ctk.CTkLabel(totales, text="Total debe: 0.00", font=("Arial", 15, "bold"))
        self.lbl_debe.pack(side="left", padx=20)

        self.lbl_haber = ctk.CTkLabel(totales, text="Total haber: 0.00", font=("Arial", 15, "bold"))
        self.lbl_haber.pack(side="left", padx=20)

        self.lbl_sd = ctk.CTkLabel(totales, text="Saldo deudor: 0.00", font=("Arial", 15, "bold"))
        self.lbl_sd.pack(side="left", padx=20)

        self.lbl_sa = ctk.CTkLabel(totales, text="Saldo acreedor: 0.00", font=("Arial", 15, "bold"))
        self.lbl_sa.pack(side="left", padx=20)

        self.generar()

    def generar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            conn = conectar()
            cursor = conn.cursor()

            query = """
                SELECT 
                    c.Codigo,
                    c.Nombre,
                    c.Tipo,
                    SUM(d.Debe) AS TotalDebe,
                    SUM(d.Haber) AS TotalHaber,
                    CASE 
                        WHEN SUM(d.Debe) - SUM(d.Haber) > 0 
                        THEN SUM(d.Debe) - SUM(d.Haber) 
                        ELSE 0 
                    END AS SaldoDeudor,
                    CASE 
                        WHEN SUM(d.Haber) - SUM(d.Debe) > 0 
                        THEN SUM(d.Haber) - SUM(d.Debe) 
                        ELSE 0 
                    END AS SaldoAcreedor
                FROM PartidaDetalle d
                INNER JOIN Partidas p ON p.IdPartida = d.IdPartida
                INNER JOIN CatalogoCuentas c ON c.IdCuenta = d.IdCuenta
                WHERE c.Activa = 1
            """

            parametros = []

            if self.fecha_inicio.get().strip():
                query += " AND p.Fecha >= ?"
                parametros.append(self.fecha_inicio.get().strip())

            if self.fecha_fin.get().strip():
                query += " AND p.Fecha <= ?"
                parametros.append(self.fecha_fin.get().strip())

            query += """
                GROUP BY c.Codigo, c.Nombre, c.Tipo
                ORDER BY c.Codigo
            """

            cursor.execute(query, parametros)

            total_debe = 0
            total_haber = 0
            total_sd = 0
            total_sa = 0

            for fila in cursor.fetchall():
                codigo, nombre, tipo, debe, haber, sd, sa = fila

                debe = float(debe or 0)
                haber = float(haber or 0)
                sd = float(sd or 0)
                sa = float(sa or 0)

                total_debe += debe
                total_haber += haber
                total_sd += sd
                total_sa += sa

                self.tabla.insert("", "end", values=(
                    codigo,
                    nombre,
                    tipo,
                    f"{debe:.2f}",
                    f"{haber:.2f}",
                    f"{sd:.2f}",
                    f"{sa:.2f}"
                ))

            self.lbl_debe.configure(text=f"Total debe: {total_debe:.2f}")
            self.lbl_haber.configure(text=f"Total haber: {total_haber:.2f}")
            self.lbl_sd.configure(text=f"Saldo deudor: {total_sd:.2f}")
            self.lbl_sa.configure(text=f"Saldo acreedor: {total_sa:.2f}")

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))
if __name__ == "__main__":
    app = BalanceSaldos()
    app.mainloop()