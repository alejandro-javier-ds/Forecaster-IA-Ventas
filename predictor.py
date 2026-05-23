import logging
import pandas as pd
import pyodbc
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import Tuple, Optional, Any
import config

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

def get_sql_driver() -> Optional[str]:
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

def extract_training_data() -> pd.DataFrame:
    driver = get_sql_driver()
    conn_str = f'DRIVER={{{driver}}};SERVER={config.SERVER_NAME};DATABASE={config.DATABASE_NAME};Trusted_Connection=yes;'
    if driver and '18' in driver:
        conn_str += 'TrustServerCertificate=yes;'
    
    query = "SELECT Date, Product, Units_Sold, Is_Holiday FROM dbo.Demand_Forecast"
    with pyodbc.connect(conn_str) as conn:
        dataset = pd.read_sql(query, conn)
    return dataset

def feature_engineering(df: pd.DataFrame) -> Tuple[Any, Any, Any, Any, pd.DataFrame]:
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(['Product', 'Date'])
    
    df['Lag_1'] = df.groupby('Product')['Units_Sold'].shift(1)
    df['Lag_7'] = df.groupby('Product')['Units_Sold'].shift(7)
    df['Lag_15'] = df.groupby('Product')['Units_Sold'].shift(15)
    df['Rolling_Mean_15'] = df.groupby('Product')['Units_Sold'].shift(1).rolling(window=15).mean()
    
    df = df.dropna()
    
    df['Month'] = df['Date'].dt.month
    df['Day_Of_Week'] = df['Date'].dt.dayofweek
    df['Is_Weekend'] = df['Day_Of_Week'].apply(lambda x: 1 if x >= 5 else 0)
    
    df_dummies = pd.get_dummies(df, columns=['Product'], prefix='Prod')
    
    features = df_dummies.drop(['Date', 'Units_Sold'], axis=1)
    target = df_dummies['Units_Sold']
    
    X_train, X_test, y_train, y_test, _, df_test = train_test_split(
        features, target, df, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, df_test

def train_model(x_train: pd.DataFrame, y_train: pd.Series) -> RandomForestRegressor:
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(x_train, y_train)
    return regressor

def save_predictions_to_sql(df_results: pd.DataFrame) -> None:
    driver = get_sql_driver()
    conn_str = f'DRIVER={{{driver}}};SERVER={config.SERVER_NAME};DATABASE={config.DATABASE_NAME};Trusted_Connection=yes;'
    if driver and '18' in driver:
        conn_str += 'TrustServerCertificate=yes;'
        
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE dbo.Demand_Predictions")
            insert_query = "INSERT INTO dbo.Demand_Predictions (Date, Product, Predicted_Units) VALUES (?, ?, ?)"
            records = [(row['Date'], row['Product'], row['Predicted_Units']) for _, row in df_results.iterrows()]
            cursor.executemany(insert_query, records)
            conn.commit()
    except Exception as e:
        logging.error(f"SQL_ERROR: {str(e)}")

def run_evaluation(model: RandomForestRegressor, x_test: pd.DataFrame, y_test: pd.Series, df_test_original: pd.DataFrame) -> None:
    predictions = model.predict(x_test)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    logging.info(f"MAE: {mae:.2f} | RMSE: {rmse:.2f}")
    
    df_results = pd.DataFrame({
        'Date': df_test_original['Date'],
        'Product': df_test_original['Product'],
        'Predicted_Units': predictions.astype(int)
    })
    
    save_predictions_to_sql(df_results)

if __name__ == "__main__":
    data = extract_training_data()
    X_train, X_test, y_train, y_test, df_test_original = feature_engineering(data)
    trained_model = train_model(X_train, y_train)
    run_evaluation(trained_model, X_test, y_test, df_test_original)