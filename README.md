# Panel interactivo de vehículos usados — Sprint 7

## Descripción

Desarrollamos una aplicación web para explorar anuncios de vehículos usados en Estados Unidos.
Utilizamos Python, pandas, Plotly y Streamlit para mostrar estadísticas y visualizaciones interactivas.
El enfoque del proyecto es crear y desplegar una aplicación web reproducible.

## Funcionalidades

- Consultamos el número de anuncios y los valores medianos de precio y kilometraje.
- Filtramos por tipo, estado y año del modelo.
- Visualizamos un histograma del kilometraje con Plotly.
- Comparamos precio y kilometraje con un gráfico de dispersión interactivo.
- Elegimos qué visualizaciones mostrar mediante casillas de verificación.
- Podemos explorar una muestra de los registros originales.

## Aplicación desplegada

[Abrir el panel interactivo en Render](https://sprint-7-dashboard-vehiculos.onrender.com/)

## Estructura del proyecto

```text
.
├── app.py
├── vehicles_us.csv
├── notebooks/
│   └── EDA.ipynb
├── requirements.txt
├── .python-version
├── .streamlit/
│   └── config.toml
├── .gitignore
└── README.md
```

El archivo original `vehicles_us.csv`, proporcionado por TripleTen, está en la raíz del proyecto junto a `app.py`. Debe incluirse en el repositorio que utilizará Render.

## Preparación local en Windows

Con Python 3.12, ejecutamos desde la carpeta que contiene `app.py`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Si utilizamos PyCharm, seleccionamos el intérprete `.venv\Scripts\python.exe`.
La aplicación se abre habitualmente en `http://localhost:8501`.

## Notebook de análisis

Con el mismo entorno virtual activo, instalamos el entorno de Jupyter y abrimos el cuaderno.

```powershell
python -m pip install jupyterlab nbformat
python -m jupyterlab notebooks/EDA.ipynb
```

En JupyterLab, ejecutamos todas las celdas de `notebooks/EDA.ipynb` con el kernel de ese entorno. Las dependencias de Jupyter solo son necesarias para el análisis local.

## Publicación en Render

1. Creamos un repositorio público de GitHub y subimos el contenido de esta carpeta como raíz del repositorio, incluidos el CSV, el notebook y los archivos de configuración.
2. Conectamos ese repositorio a un nuevo servicio **Web Service** de Render con entorno Python. Dejamos vacío **Root Directory**. Render toma la versión de Python de `.python-version`.
3. Establecemos el comando de compilación.

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Establecemos el comando de inicio.

   ```bash
   python -m streamlit run app.py --server.address 0.0.0.0 --server.port "$PORT"
   ```

5. Configuramos `/_stcore/health` como ruta de comprobación de salud. Tras desplegar, abrimos la URL pública y comprobamos que aparecen los dos gráficos y responden los filtros.
6. Copiamos esa URL real en la sección "Aplicación desplegada" de este README.
7. Actualizamos el repositorio público con el README y entregamos su enlace a TripleTen.

[Configuración de la versión de Python en Render](https://render.com/docs/python-version) · [Servicios web y puerto en Render](https://render.com/docs/web-services)

## Datos y limitaciones

Trabajamos con los anuncios originales del archivo CSV. Las conversiones numéricas
no alteran los valores originales del archivo. No imputamos información faltante.
Por defecto se excluyen los precios superiores al percentil 99. El rango completo de años conserva los anuncios sin año. Al acotar ese rango, solo se incluyen anuncios con un año conocido dentro de la selección.
Cada gráfico usa los registros con valores válidos para sus ejes. Para la dispersión, usamos una muestra reproducible cuando hay más de 12 000 anuncios disponibles.
