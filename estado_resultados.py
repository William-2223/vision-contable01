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
        self.geometry("980x680")
        self.minsize(920, 620)
        self._construir_ui()
        self.generar()

    def _construir_ui(self):
        ctk.CTkLabel(self, text="Estado de Resultados", font=("Arial", 26, "bold")).pack(pady=(16, 4))
        ctk.CTkLabel(self, text="Resumen de ingresos, costos y gastos", font=("Arial", 13)).pack(pady=(0, 10))
        contenedor = ctk.CTkFrame(self, corner_radius=14)
        contenedor.pack(padx=20, pady=(0, 16), fill="both", expand=True)

        tabla_frame = ctk.CTkFrame(contenedor)
        tabla_frame.pack(padx=16, pady=(14, 8), fill="both", expand=True)
        self.tabla = ttk.Treeview(tabla_frame, columns=("Tipo", "Codigo", "Cuenta", "Saldo"), show="headings")
        for col, ancho in {"Tipo": 160, "Codigo": 140, "Cuenta": 420, "Saldo": 180}.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        sb_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        sb_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.tabla.pack(side="top", fill="both", expand=True, padx=8, pady=(8, 0))
        sb_x.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        sb_y.pack(side="right", fill="y", padx=(0, 8), pady=8)

        self.lbl_total = ctk.CTkLabel(contenedor, text="", font=("Arial", 17, "bold"))
        self.lbl_total.pack(pady=(6, 14))

    def generar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            conn = conectar(); cursor = conn.cursor()
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
            total_ingresos = total_costos = total_gastos = 0
            for tipo, codigo, nombre, saldo in cursor.fetchall():
                saldo = float(saldo or 0)
                self.tabla.insert("", "end", values=(tipo, codigo, nombre, f"{saldo:.2f}"))
                if tipo == "INGRESO": total_ingresos += saldo
                elif tipo == "COSTO": total_costos += saldo
                elif tipo == "GASTO": total_gastos += saldo
            utilidad = total_ingresos - total_costos - total_gastos
            self.lbl_total.configure(text=f"Ingresos: {total_ingresos:.2f} | Costos: {total_costos:.2f} | Gastos: {total_gastos:.2f} | Utilidad: {utilidad:.2f}")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = EstadoResultados()
    app.mainloop()
