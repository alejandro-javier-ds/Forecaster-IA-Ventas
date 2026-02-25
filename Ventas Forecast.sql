USE PortafolioDB;
GO

-- Creamos la tabla independiente para el Proyecto 2
IF OBJECT_ID('dbo.Ventas_Forecast', 'U') IS NOT NULL
    DROP TABLE dbo.Ventas_Forecast;

CREATE TABLE dbo.Ventas_Forecast (
    ID_Registro INT PRIMARY KEY IDENTITY(1,1),
    Fecha DATE NOT NULL,
    Producto VARCHAR(50),
    Cantidad_Vendida INT,
    Precio_Unitario DECIMAL(10,2),
    Festivo INT
);
GO