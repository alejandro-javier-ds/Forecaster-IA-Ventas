import logging
import pandas as pd
import numpy as np
import pyodbc
from datetime import datetime, timedelta
import config

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

def get_sql_driver() -> str:
    available_drivers = [
        'ODBC Driver 18 for SQL Server',
        'ODBC Driver 17 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server'
    ]
    for driver in available_drivers:
        if driver in pyodbc.drivers():
            return driver
    return 'SQL Server'

def generate_training_data() -> pd.DataFrame:
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(730)]
    
    data = []
    products = ['HP Laptop', 'Dell Monitor', 'Logitech Mouse', 'Razer Keyboard']
    
    for date in dates:
        day_of_year = date.timetuple().tm_yday
        trend = day_of_year * 0.05
        
        for prod in products:
            base_demand = 20 + trend
            
            if date.weekday() >= 5:
                base_demand += 15
            
            is_holiday = 1 if (date.month == 12 and date.day == 25) else 0
            if is_holiday:
                base_demand += 20
            
            final_demand = int(base_demand + np.random.normal(0, 2))
            
            data.append({
                'Date': date.strftime('%Y-%m-%d'),
                'Product': prod,
                'Units_Sold': max(1, final_demand),
                'Unit_Price': np.random.uniform(100, 2000),
                'Is_Holiday': is_holiday
            })
    return pd.DataFrame(data)

def upload_to_sql(df: pd.DataFrame) -> None:
    driver = get_sql_driver()
    conn_str = f'DRIVER={{{driver}}};SERVER={config.SERVER_NAME};DATABASE={config.DATABASE_NAME};Trusted_Connection=yes;'
    
    if '18' in driver:
        conn_str += 'TrustServerCertificate=yes;'
            
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE dbo.Demand_Forecast")
            
            insert_query = """
                INSERT INTO dbo.Demand_Forecast (Date, Product, Units_Sold, Unit_Price, Is_Holiday)
                VALUES (?, ?, ?, ?, ?)
            """
            
            records_to_insert = [
                (row['Date'], row['Product'], row['Units_Sold'], row['Unit_Price'], row['Is_Holiday'])
                for _, row in df.iterrows()
            ]
            
            cursor.executemany(insert_query, records_to_insert)
            conn.commit()
            logging.info(f"Successfully loaded {len(df)} rows into PortfolioDB.")
            
    except Exception as e:
        logging.error(f"SQL_ERROR: {str(e)}")

if __name__ == "__main__":
    df_train = generate_training_data()
    upload_to_sql(df_train)