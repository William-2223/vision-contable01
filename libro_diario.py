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
        self.geometry("1240x760")
        self.minsize(1160, 700)
        self._construir_ui()
        self.generar()

    def _construir_ui(self):
        ctk.CTkLabel(self, text="Libro Diario", font=("Arial", 26, "bold")).pack(pady=(16, 4))
        ctk.CTkLabel(self, text="Detalle cronológico de partidas", font=("Arial", 13)).pack(pady=(0, 10))
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
        self.tabla = ttk.Treeview(tabla_frame, columns=("Fecha", "Partida", "Concepto", "Cuenta", "Debe", "Haber", "Descripcion", "Usuario"), show="headings")
        columnas = {"Fecha": 110, "Partida": 90, "Concepto": 250, "Cuenta": 260, "Debe": 110, "Haber": 110, "Descripcion": 250, "Usuario": 120}
        for col, ancho in columnas.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        sb_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        sb_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.tabla.pack(side="top", fill="both", expand=True, padx=8, pady=(8, 0))
        sb_x.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        sb_y.pack(side="right", fill="y", padx=(0, 8), pady=8)

        totales = ctk.CTkFrame(contenedor)
        totales.pack(padx=16, pady=(8, 14), fill="x")
        self.lbl_debe = ctk.CTkLabel(totales, text="Total debe: 0.00", font=("Arial", 15, "bold")); self.lbl_debe.pack(side="left", padx=16)
        self.lbl_haber = ctk.CTkLabel(totales, text="Total haber: 0.00", font=("Arial", 15, "bold")); self.lbl_haber.pack(side="left", padx=16)
        self.lbl_diferencia = ctk.CTkLabel(totales, text="Diferencia: 0.00", font=("Arial", 15, "bold")); self.lbl_diferencia.pack(side="left", padx=16)

    def generar(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        try:
            conn = conectar(); cursor = conn.cursor()
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
                query += " AND P.Fecha >= ?"; parametros.append(self.fecha_inicio.get().strip())
            if self.fecha_fin.get().strip():
                query += " AND P.Fecha <= ?"; parametros.append(self.fecha_fin.get().strip())
            query += """
                ORDER BY P.Fecha, P.IdPartida, D.IdDetalle
            """
            cursor.execute(query, parametros)
            total_debe = total_haber = 0
            for fecha, partida, concepto, cuenta, debe, haber, descripcion, usuario in cursor.fetchall():
                debe = float(debe or 0); haber = float(haber or 0)
                total_debe += debe; total_haber += haber
                self.tabla.insert("", "end", values=(fecha, partida, concepto, cuenta, f"{debe:.2f}", f"{haber:.2f}", descripcion, usuario))
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
