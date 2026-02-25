import pandas as pd
import numpy as np
import pyodbc
from datetime import datetime, timedelta

# --- CONFIGURACIÓN IDÉNTICA AL PROYECTO 1 ---
SERVER_NAME = r'(localdb)\MSSQLLocalDB'
DATABASE_NAME = 'PortafolioDB'

def get_sql_driver():
    available_drivers = pyodbc.drivers()
    target_drivers = [
        'ODBC Driver 18 for SQL Server',
        'ODBC Driver 17 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server'
    ]
    for driver in target_drivers:
        if driver in available_drivers:
            return driver
    return None

def generate_training_data():
    print("[INFO] Generando 2 años de historia en memoria...")
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(730)]
    
    data = []
    productos = ['Laptop HP', 'Monitor Dell', 'Mouse Logitech', 'Teclado Razer']
    
    for date in dates:
        for prod in productos:
            base_demand = np.random.randint(10, 30)
            if date.weekday() >= 5: base_demand += 15 
            
            data.append({
                'Fecha': date.strftime('%Y-%m-%d'),
                'Producto': prod,
                'Cantidad_Vendida': base_demand,
                'Precio_Unitario': np.random.uniform(100, 2000),
                'Festivo': 1 if (date.month == 12 and date.day == 25) else 0
            })
    return pd.DataFrame(data)

def upload_to_sql(df):
    driver = get_sql_driver()
    if not driver:
        print("[ERROR] No se encontro un driver ODBC compatible.")
        return

    conn_str = f'DRIVER={{{driver}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'
    
    try:
        # Si usas ODBC Driver 18, a veces pide TrustServerCertificate
        if '18' in driver:
            conn_str += 'TrustServerCertificate=yes;'
            
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            print(f"[INFO] Conectado usando: {driver}")
            print("[INFO] Limpiando tabla Ventas_Forecast...")
            cursor.execute("TRUNCATE TABLE dbo.Ventas_Forecast")
            
            print("[INFO] Insertando registros de entrenamiento (Esto tomara unos segundos)...")
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO dbo.Ventas_Forecast (Fecha, Producto, Cantidad_Vendida, Precio_Unitario, Festivo)
                    VALUES (?, ?, ?, ?, ?)
                """, row['Fecha'], row['Producto'], row['Cantidad_Vendida'], row['Precio_Unitario'], row['Festivo'])
            conn.commit()
            print(f"[SUCCESS] {len(df)} filas cargadas en PortafolioDB.")
    except Exception as e:
        print(f"[ERROR] Fallo critico en la carga: {str(e)}")

if __name__ == "__main__":
    df_train = generate_training_data()
    upload_to_sql(df_train)