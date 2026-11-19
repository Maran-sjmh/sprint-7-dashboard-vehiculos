"""Panel interactivo de anuncios de vehículos usados (Sprint 7)."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path(__file__).resolve().parent / "vehicles_us.csv"
REQUIRED_COLUMNS = {"price", "odometer", "model_year", "type", "condition"}

st.set_page_config(
    page_title="Vehículos usados | Panel interactivo",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Carga los anuncios sin reemplazar valores faltantes artificialmente."""
    dataframe = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing_columns:
        columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"Faltan columnas necesarias: {columns}")

    for column in ("price", "odometer", "model_year"):
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    return dataframe


st.title("🚗 Mercado de vehículos usados en Estados Unidos")
st.write(
    "Exploramos anuncios de vehículos mediante filtros y gráficos interactivos. "
    "Los datos provienen del archivo vehicles_us.csv utilizado en el Sprint 7 de TripleTen."
)

if not DATA_PATH.is_file():
    st.error(
        "No se encontró vehicles_us.csv. Descarga el conjunto de datos "
        "de TripleTen y colócalo en la misma carpeta que app.py."
    )
    st.stop()

try:
    cars = load_data(str(DATA_PATH))
except (OSError, ValueError, pd.errors.ParserError) as exc:
    st.error(f"No fue posible cargar el conjunto de datos: {exc}")
    st.stop()

st.sidebar.header("Filtros de anuncios")
all_types = sorted(cars["type"].dropna().astype(str).unique().tolist())
all_conditions = sorted(cars["condition"].dropna().astype(str).unique().tolist())

selected_types = st.sidebar.multiselect(
    "Tipo de vehículo", all_types, default=all_types
)
selected_conditions = st.sidebar.multiselect(
    "Estado del vehículo", all_conditions, default=all_conditions
)
include_outliers = st.sidebar.checkbox(
    "Incluir precios superiores al percentil 99", value=False,
    help="Desmarcado, excluimos los precios superiores al percentil 99 para mejorar la visualización."
)

filtered = cars.loc[
    cars["type"].isin(selected_types)
    & cars["condition"].isin(selected_conditions)
].copy()

if not include_outliers and not cars["price"].dropna().empty:
    price_limit = float(cars["price"].quantile(0.99))
    filtered = filtered.loc[filtered["price"].le(price_limit) | filtered["price"].isna()]
else:
    price_limit = None

years = cars["model_year"].dropna()
if not years.empty:
    min_year, max_year = int(years.min()), int(years.max())
    if min_year < max_year:
        full_year_range = (min_year, max_year)
        chosen_years = st.sidebar.slider(
            "Año del modelo", min_value=min_year, max_value=max_year,
            value=full_year_range,
            help="El rango completo conserva los anuncios sin año. Un rango acotado los excluye.",
        )
        if chosen_years != full_year_range:
            filtered = filtered.loc[filtered["model_year"].between(*chosen_years)]

st.sidebar.caption(
    "Los filtros modifican las estadísticas y los gráficos. "
    "No sustituimos los valores faltantes por datos inventados."
)

if filtered.empty:
    st.warning("No hay anuncios para los filtros seleccionados.")
    st.stop()

left, middle, right = st.columns(3)
left.metric("Anuncios filtrados", str(len(filtered)))
middle.metric(
    "Precio mediano (USD)",
    f"${filtered['price'].median():.0f}" if filtered["price"].notna().any() else "Sin datos",
)
right.metric(
    "Odómetro mediano (millas)",
    f"{filtered['odometer'].median():.0f}"
    if filtered["odometer"].notna().any() else "Sin datos",
)

if price_limit is not None:
    st.caption(
        f"Se excluyen los anuncios con precios superiores a ${price_limit:,.0f} USD. "
        "Puedes incluirlos desde la barra lateral."
    )

st.divider()
histogram_on = st.checkbox("Mostrar histograma del kilometraje", value=True)
if histogram_on:
    histogram_data = filtered.dropna(subset=["odometer"])
    histogram_data = histogram_data.loc[histogram_data["odometer"] >= 0]
    if histogram_data.empty:
        st.info("No hay valores de odómetro válidos para este gráfico.")
    else:
        fig_hist = px.histogram(
            histogram_data,
            x="odometer",
            nbins=55,
            labels={"odometer": "Odómetro (millas)"},
            title="Distribución del kilometraje anunciado",
        )
        fig_hist.update_layout(
            yaxis_title="Número de anuncios", bargap=0.05,
            margin=dict(l=10, r=10, t=55, b=15),
        )
        st.plotly_chart(fig_hist, width="stretch")
        st.caption(
            "El histograma permite identificar dónde se concentran los kilometrajes "
            "y observar la dispersión de los anuncios."
        )

scatter_on = st.checkbox("Mostrar dispersión entre kilometraje y precio", value=True)
if scatter_on:
    scatter_data = filtered.dropna(subset=["price", "odometer"])
    scatter_data = scatter_data.loc[
        (scatter_data["price"] >= 0) & (scatter_data["odometer"] >= 0)
    ]
    if scatter_data.empty:
        st.info("No hay suficientes valores de precio y odómetro para este gráfico.")
    else:
        # Evita una interfaz lenta al mostrar demasiados puntos en una sesión gratuita.
        sample_size = 12000
        if len(scatter_data) > sample_size:
            scatter_data = scatter_data.sample(sample_size, random_state=42)
            st.caption(
                f"Mostramos una muestra reproducible de {sample_size} anuncios "
                "para mantener fluida la visualización."
            )

        fig_scatter = px.scatter(
            scatter_data,
            x="odometer", y="price", color="condition",
            title="Precio anunciado según el kilometraje",
            labels={
                "odometer": "Odómetro (millas)",
                "price": "Precio (USD)",
                "condition": "Estado",
            },
            opacity=0.52,
            render_mode="webgl",
            hover_data=["model_year", "type"],
        )
        fig_scatter.update_layout(margin=dict(l=10, r=10, t=55, b=15))
        st.plotly_chart(fig_scatter, width="stretch")
        st.caption(
            "Cada punto representa un anuncio. Observamos la relación entre precio "
            "y kilometraje, teniendo en cuenta el estado de los vehículos. "
            "La asociación visual no demuestra causalidad."
        )

if st.checkbox("Mostrar una muestra de los datos"):
    st.dataframe(filtered.head(50), width="stretch", hide_index=True)

st.divider()
st.caption(
    "Proyecto del Sprint 7 de TripleTen · Elaborado con Python, pandas, Plotly y Streamlit."
)
