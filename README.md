# Forecaster-IA-Ventas
Sistema de inteligencia artificial para la predicción de demanda (Forecasting) con persistencia en SQL Server y dashboard interactivo en Streamlit.

# Demand Intelligence Forecaster 🔮

Pipeline de Machine Learning diseñado para predecir la demanda de productos tecnológicos, integrando una arquitectura de datos profesional que conecta Python con SQL Server.

## 🚀 Impacto del Proyecto
Este sistema permite a una gerencia visualizar tendencias futuras de ventas basándose en patrones históricos, optimizando la toma de decisiones sobre inventarios y logística.

## 🛠️ Stack Tecnológico
* **Base de Datos:** SQL Server (Transact-SQL).
* **Lenguaje:** Python 3.14 (Nomenclatura industrial).
* **IA:** Scikit-Learn (Random Forest Regressor).
* **Interfaz:** Streamlit (Dashboard dinámico).

## 📊 Capacidades Técnicas
* **ETL e Ingesta:** Extracción directa de datos desde SQL Server mediante `pyodbc`.
* **Feature Engineering:** Generación automática de variables temporales (mes, día, fines de semana y festivos).
* **Evaluación de Modelo:** Precisión monitoreada mediante métricas MAE (~5.13) y RMSE (~6.10).
* **Visualización:** Gráficos desglosados con etiquetas de datos y división de entrenamiento/validación (80/20).

## ⚙️ Instalación y Uso
1. Configurar la base de datos ejecutando el script de SQL proporcionado.
2. Generar la data de entrenamiento con `python data_generator.py`.
3. Ejecutar el dashboard con `streamlit run interface.py`.