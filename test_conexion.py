import pyodbc

conexion = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\SQLEXPRESS;"
    "DATABASE=VisionContable;"
    "Trusted_Connection=yes;"
)

cursor = conexion.cursor()
cursor.execute("SELECT Usuario, Nombre, Rol FROM Usuarios")

for fila in cursor.fetchall():
    print(fila)

conexion.close()