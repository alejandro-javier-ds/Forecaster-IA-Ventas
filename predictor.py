import pandas as pd
import pyodbc
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

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

def extract_training_data():
    driver = get_sql_driver()
    conn_str = f'DRIVER={{{driver}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};Trusted_Connection=yes;'
    if '18' in driver:
        conn_str += 'TrustServerCertificate=yes;'
    
    query = "SELECT Fecha, Producto, Cantidad_Vendida, Festivo FROM dbo.Ventas_Forecast"
    
    with pyodbc.connect(conn_str) as conn:
        dataset = pd.read_sql(query, conn)
    
    print(f"[LOG] Dataset cargado: {len(dataset)} registros obtenidos de SQL.")
    return dataset

def feature_engineering(df):
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Mes'] = df['Fecha'].dt.month
    df['Dia_Semana'] = df['Fecha'].dt.dayofweek
    df['Es_Fin_Semana'] = df['Dia_Semana'].apply(lambda x: 1 if x >= 5 else 0)
    
    df = pd.get_dummies(df, columns=['Producto'], prefix='Prod')
    
    features = df.drop(['Fecha', 'Cantidad_Vendida'], axis=1)
    target = df['Cantidad_Vendida']
    
    print("[LOG] Caracteristicas temporales y categoricas generadas.")
    return train_test_split(features, target, test_size=0.2, random_state=42)

def train_model(x_train, y_train):
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(x_train, y_train)
    print("[LOG] Entrenamiento de Random Forest completado satisfactoriamente.")
    return regressor

def run_evaluation(model, x_test, y_test):
    predictions = model.predict(x_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    
    print(f"[LOG] Metricas de Precision: MAE = {mae:.2f} | RMSE = {rmse:.2f}")

if __name__ == "__main__":
    data = extract_training_data()
    X_train, X_test, y_train, y_test = feature_engineering(data)
    trained_model = train_model(X_train, y_train)
    run_evaluation(trained_model, X_test, y_test)