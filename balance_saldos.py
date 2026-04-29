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
        self.geometry("1120x700")
        self.minsize(1040, 660)

        self._construir_ui()
        self.generar()

    def _construir_ui(self):
        ctk.CTkLabel(self, text="Balance de saldos", font=("Arial", 26, "bold")).pack(pady=(16, 4))
        ctk.CTkLabel(self, text="Consulta acumulada por cuenta", font=("Arial", 13)).pack(pady=(0, 10))

        contenedor = ctk.CTkFrame(self, corner_radius=14)
        contenedor.pack(padx=20, pady=(0, 16), fill="both", expand=True)

        filtros = ctk.CTkFrame(contenedor)
        filtros.pack(padx=16, pady=(14, 8), fill="x")

        ctk.CTkLabel(filtros, text="Filtros", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(8, 2))
        self.fecha_inicio = ctk.CTkEntry(filtros, placeholder_text="Fecha inicio YYYY-MM-DD", width=200)
        self.fecha_inicio.grid(row=1, column=0, padx=10, pady=10)
        self.fecha_fin = ctk.CTkEntry(filtros, placeholder_text="Fecha fin YYYY-MM-DD", width=200)
        self.fecha_fin.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(filtros, text="Generar", width=120, command=self.generar).grid(row=1, column=2, padx=10, pady=10)

        tabla_frame = ctk.CTkFrame(contenedor)
        tabla_frame.pack(padx=16, pady=8, fill="both", expand=True)

        self.tabla = ttk.Treeview(self, columns=("Codigo", "Cuenta", "Tipo", "Debe", "Haber", "SaldoDeudor", "SaldoAcreedor"), show="headings")
        columnas = {"Codigo": 100, "Cuenta": 280, "Tipo": 130, "Debe": 130, "Haber": 130, "SaldoDeudor": 150, "SaldoAcreedor": 150}
        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")

        scrollbar_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        scrollbar_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.tabla.pack(in_=tabla_frame, side="top", fill="both", expand=True, padx=8, pady=(8, 0))
        scrollbar_x.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        scrollbar_y.pack(side="right", fill="y", padx=(0, 8), pady=8)

        totales = ctk.CTkFrame(contenedor)
        totales.pack(padx=16, pady=(8, 14), fill="x")
        self.lbl_debe = ctk.CTkLabel(totales, text="Total debe: 0.00", font=("Arial", 15, "bold"))
        self.lbl_debe.pack(side="left", padx=16)
        self.lbl_haber = ctk.CTkLabel(totales, text="Total haber: 0.00", font=("Arial", 15, "bold"))
        self.lbl_haber.pack(side="left", padx=16)
        self.lbl_sd = ctk.CTkLabel(totales, text="Saldo deudor: 0.00", font=("Arial", 15, "bold"))
        self.lbl_sd.pack(side="left", padx=16)
        self.lbl_sa = ctk.CTkLabel(totales, text="Saldo acreedor: 0.00", font=("Arial", 15, "bold"))
        self.lbl_sa.pack(side="left", padx=16)

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

            total_debe = total_haber = total_sd = total_sa = 0
            for fila in cursor.fetchall():
                codigo, nombre, tipo, debe, haber, sd, sa = fila
                debe = float(debe or 0); haber = float(haber or 0); sd = float(sd or 0); sa = float(sa or 0)
                total_debe += debe; total_haber += haber; total_sd += sd; total_sa += sa
                self.tabla.insert("", "end", values=(codigo, nombre, tipo, f"{debe:.2f}", f"{haber:.2f}", f"{sd:.2f}", f"{sa:.2f}"))

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
