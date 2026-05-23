import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pyodbc
import config

st.set_page_config(page_title="Demand Analytics", layout="wide")

def get_data() -> pd.DataFrame:
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.SERVER_NAME};DATABASE={config.DATABASE_NAME};Trusted_Connection=yes;'
    
    query = """
        SELECT 
            f.Date, 
            f.Product, 
            f.Units_Sold AS Actual, 
            p.Predicted_Units AS Forecast
        FROM dbo.Demand_Forecast f
        LEFT JOIN dbo.Demand_Predictions p ON f.Date = p.Date AND f.Product = p.Product
    """
    
    with pyodbc.connect(conn_str) as conn:
        df = pd.read_sql(query, conn)
    
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month_Year'] = df['Date'].dt.strftime('%Y-%m')
    return df

def annotate_plot(ax, df: pd.DataFrame, column: str, color: str) -> None:
    for _, row in enumerate(df.itertuples()):
        val = getattr(row, column)
        if pd.notna(val):
            label = f'{val:.1f}' if isinstance(val, float) else f'{int(val)}'
            ax.text(row.Date, val + 1.5, label, ha='center', va='bottom', fontsize=10, weight='bold', color=color)

def main():
    st.title("Demand Analytics Engine")
    st.markdown("---")
    
    data = get_data()
    
    st.sidebar.header("Filters")
    product_sel = st.sidebar.selectbox("Product:", data['Product'].unique())
    months = sorted(data['Month_Year'].unique())
    months_sel = st.sidebar.multiselect("Month:", months, default=months[-1:])
    
    if not months_sel:
        st.warning("Select at least one month.")
        return
        
    df_filtered = data[(data['Product'] == product_sel) & (data['Month_Year'].isin(months_sel))].sort_values('Date')
    
    tab1, tab2 = st.tabs(["Performance", "Model Audit"])
    
    with tab1:
        fig1, ax1 = plt.subplots(figsize=(14, 5))
        sns.lineplot(data=df_filtered, x='Date', y='Actual', marker='o', color='tab:blue', ax=ax1, label='Actual')
        sns.lineplot(data=df_filtered, x='Date', y='Forecast', linestyle='--', marker='x', color='tab:orange', ax=ax1, label='Forecast')
        plt.xticks(rotation=45)
        st.pyplot(fig1)
        
    with tab2:
        cut_idx = int(len(df_filtered) * 0.8)
        df_train = df_filtered.iloc[:cut_idx]
        df_test = df_filtered.iloc[cut_idx:]
        
        fig2, ax2 = plt.subplots(figsize=(14, 5))
        sns.lineplot(data=df_train, x='Date', y='Actual', color='gray', ax=ax2, label='Training')
        if not df_test.empty:
            sns.lineplot(data=df_test, x='Date', y='Forecast', color='orange', ax=ax2, label='Validation')
            plt.axvline(x=df_test['Date'].iloc[0], color='red', linestyle=':')
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    st.sidebar.markdown("---")
    mae = abs(df_filtered['Actual'] - df_filtered['Forecast']).mean()
    st.sidebar.metric("Mean Absolute Error", f"{mae:.2f}")

if __name__ == "__main__":
    main()