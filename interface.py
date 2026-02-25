import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from predictor import extract_training_data, feature_engineering, train_model

st.set_page_config(page_title="Demand Intelligence Forecaster", layout="wide")

def load_analytics_engine():
    print("[LOG] Iniciando motor de analitica visual...")
    raw_data = extract_training_data()
    X_train, X_test, y_train, y_test = feature_engineering(raw_data)
    model = train_model(X_train, y_train)
    
    df_viz = raw_data.copy()
    df_viz['Fecha'] = pd.to_datetime(df_viz['Fecha'])
    df_viz = df_viz.sort_values('Fecha')
    
    df_features = pd.get_dummies(df_viz.drop(['Cantidad_Vendida', 'Fecha'], axis=1), columns=['Producto'], prefix='Prod')
    df_features = df_features.reindex(columns=X_train.columns, fill_value=0)
    
    df_viz['Prediccion'] = model.predict(df_features)
    print("[LOG] Pipeline de inferencia visual completado.")
    return df_viz

def annotate_plot(ax, df, column, color='black'):
    for i, row in enumerate(df.itertuples()):
        val = getattr(row, column)
        # FIX: 1 decimal para la IA, entero para la venta real
        texto = f'{val:.1f}' if column == 'Prediccion' else f'{int(val)}'
        
        # Le damos un margen dinámico para que no se pegue a la línea
        ax.text(row.Fecha, val + 1.5, texto, 
                ha='center', va='bottom', fontsize=10, 
                weight='bold', color=color)

def main():
    st.title("🔮 Demand Intelligence Forecaster")
    st.markdown("---")
    
    data = load_analytics_engine()
    
    st.sidebar.header("Filtros de Negocio")
    producto_sel = st.sidebar.selectbox("Producto:", data['Producto'].unique())
    
    data['Mes_Año'] = data['Fecha'].dt.strftime('%Y-%m')
    meses_disponibles = data['Mes_Año'].unique()
    meses_sel = st.sidebar.multiselect("Filtrar por Mes:", meses_disponibles, default=meses_disponibles[-1:])
    
    if len(meses_sel) == 0:
        st.warning("⚠️ Seleccione al menos un mes para visualizar las etiquetas de datos.")
        return
        
    df_filtered = data[(data['Producto'] == producto_sel) & (data['Mes_Año'].isin(meses_sel))]
    
    tab1, tab2 = st.tabs(["📊 Análisis Desglosado", "📈 Auditoría de Modelo (100% vs 80/20)"])
    
    with tab1:
        st.subheader(f"Ventas Reales Históricas: {producto_sel}")
        fig1, ax1 = plt.subplots(figsize=(14, 5))
        sns.lineplot(data=df_filtered, x='Fecha', y='Cantidad_Vendida', marker='o', color='tab:blue', ax=ax1)
        annotate_plot(ax1, df_filtered, 'Cantidad_Vendida', color='tab:blue')
        plt.xticks(rotation=45)
        st.pyplot(fig1)
        
        st.subheader(f"Predicción del Modelo IA: {producto_sel}")
        fig2, ax2 = plt.subplots(figsize=(14, 5))
        sns.lineplot(data=df_filtered, x='Fecha', y='Prediccion', linestyle='--', marker='x', color='tab:orange', ax=ax2)
        annotate_plot(ax2, df_filtered, 'Prediccion', color='tab:orange')
        plt.xticks(rotation=45)
        st.pyplot(fig2)
        
    with tab2:
        st.subheader("Visión General del Periodo (100%)")
        fig3, ax3 = plt.subplots(figsize=(14, 5))
        sns.lineplot(data=df_filtered, x='Fecha', y='Cantidad_Vendida', color='gray', ax=ax3, label='Data Histórica')
        annotate_plot(ax3, df_filtered, 'Cantidad_Vendida', color='dimgray')
        plt.xticks(rotation=45)
        st.pyplot(fig3)
        
        st.subheader("División de Entrenamiento (80%) vs Validación (20%)")
        corte_idx = int(len(df_filtered) * 0.8)
        df_train = df_filtered.iloc[:corte_idx]
        df_test = df_filtered.iloc[corte_idx:]
        
        fig4, ax4 = plt.subplots(figsize=(14, 5))
        sns.lineplot(data=df_train, x='Fecha', y='Cantidad_Vendida', label='Entrenamiento (80%)', color='gray', ax=ax4)
        annotate_plot(ax4, df_train, 'Cantidad_Vendida', color='dimgray')
        
        if not df_test.empty:
            sns.lineplot(data=df_test, x='Fecha', y='Prediccion', label='Predicción Futura (20%)', color='orange', linewidth=2.5, ax=ax4)
            plt.axvline(x=df_test['Fecha'].iloc[0], color='red', linestyle=':', label='Corte IA')
            annotate_plot(ax4, df_test, 'Prediccion', color='darkorange')
            
        plt.xticks(rotation=45)
        st.pyplot(fig4)

    st.sidebar.markdown("---")
    error_avg = abs(df_filtered['Cantidad_Vendida'] - df_filtered['Prediccion']).mean()
    st.sidebar.metric("Error Promedio del Filtro", f"{error_avg:.2f}")

if __name__ == "__main__":
    main()