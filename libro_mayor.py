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
        self.geometry("1180x740")
        self.minsize(1100, 680)
        self.cuentas = {}
        self._construir_ui()
        self.cargar_cuentas()

    def _construir_ui(self):
        ctk.CTkLabel(self, text="Libro Mayor", font=("Arial", 26, "bold")).pack(pady=(16, 4))
        ctk.CTkLabel(self, text="Movimientos por cuenta contable", font=("Arial", 13)).pack(pady=(0, 10))
        contenedor = ctk.CTkFrame(self, corner_radius=14)
        contenedor.pack(padx=20, pady=(0, 16), fill="both", expand=True)

        filtro = ctk.CTkFrame(contenedor)
        filtro.pack(padx=16, pady=(14, 8), fill="x")
        ctk.CTkLabel(filtro, text="Filtro de cuenta", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(8, 2))
        self.combo = ctk.CTkComboBox(filtro, width=460)
        self.combo.grid(row=1, column=0, padx=10, pady=10)
        ctk.CTkButton(filtro, text="Cargar", width=120, command=self.generar).grid(row=1, column=1, padx=10, pady=10)

        tabla_frame = ctk.CTkFrame(contenedor)
        tabla_frame.pack(padx=16, pady=8, fill="both", expand=True)
        self.tabla = ttk.Treeview(tabla_frame, columns=("Fecha", "Partida", "Concepto", "Debe", "Haber", "Saldo"), show="headings")
        for col, ancho in {"Fecha": 120, "Partida": 90, "Concepto": 350, "Debe": 130, "Haber": 130, "Saldo": 160}.items():
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        sb_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        sb_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.tabla.pack(side="top", fill="both", expand=True, padx=8, pady=(8, 0))
        sb_x.pack(side="bottom", fill="x", padx=8, pady=(0, 8))
        sb_y.pack(side="right", fill="y", padx=(0, 8), pady=8)

        self.lbl_saldo = ctk.CTkLabel(contenedor, text="Saldo final: 0.00", font=("Arial", 16, "bold"))
        self.lbl_saldo.pack(pady=(6, 14))

    def cargar_cuentas(self):
        conn = conectar(); cursor = conn.cursor()
        cursor.execute("""
            SELECT IdCuenta, Codigo, Nombre, Tipo
            FROM CatalogoCuentas
            WHERE Activa = 1
            ORDER BY Codigo
        """)
        valores = []
        for id_cuenta, codigo, nombre, tipo in cursor.fetchall():
            texto = f"{codigo} - {nombre}"; self.cuentas[texto] = (id_cuenta, tipo); valores.append(texto)
        self.combo.configure(values=valores)
        if valores:
            self.combo.set(valores[0])
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
            conn = conectar(); cursor = conn.cursor()
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
            for fecha, partida, concepto, debe, haber in cursor.fetchall():
                debe = float(debe or 0); haber = float(haber or 0)
                if tipo == "ACTIVO" or tipo == "GASTO" or tipo == "COSTO": saldo += (debe - haber)
                else: saldo += (haber - debe)
                self.tabla.insert("", "end", values=(fecha, partida, concepto, f"{debe:.2f}", f"{haber:.2f}", f"{saldo:.2f}"))
            self.lbl_saldo.configure(text=f"Saldo final: {saldo:.2f}")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = LibroMayor()
    app.mainloop()
