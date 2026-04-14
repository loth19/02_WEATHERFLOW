import os
from pathlib import Path

import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

st.set_page_config(
    page_title="WeatherFlow",
    page_icon="🌤️",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "src" / "df.csv"

load_dotenv(PROJECT_ROOT / ".env")

villes = {
    "Paris": "Paris,FR",
    "Londres": "London,GB",
    "Rome": "Rome,IT",
    "Madrid": "Madrid,ES",
    "Berlin": "Berlin,DE",
}


def meteo_emoji(description: str) -> str:
    desc = (description or "").lower()
    if "pluie" in desc or "rain" in desc:
        return "☔"
    if "neige" in desc or "snow" in desc:
        return "❄️"
    if "orage" in desc or "storm" in desc:
        return "⛈️"
    if "nuage" in desc or "cloud" in desc:
        return "☁️"
    return "🌤️"


def indice_confort(row: pd.Series) -> float:
    score = 10.0
    t = pd.to_numeric(row.get("temperature"), errors="coerce")
    h = pd.to_numeric(row.get("humidite"), errors="coerce")
    w = pd.to_numeric(row.get("vitesse_vent"), errors="coerce")

    if pd.isna(t) or pd.isna(h) or pd.isna(w):
        return 0.0

    if t < 10 or t > 32:
        score -= 4
    elif 10 <= t < 18 or 24 < t <= 32:
        score -= 2

    if h < 30 or h > 80:
        score -= 3
    elif 30 <= h < 40 or 60 < h <= 80:
        score -= 1.5

    if w > 12:
        score -= 2
    elif w > 8:
        score -= 1

    return round(max(0.0, min(10.0, score)), 1)


def normaliser_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    colonnes_attendues = [
        "ville",
        "temperature",
        "ressenti",
        "humidite",
        "vitesse_vent",
        "description_meteo",
    ]

    for col in colonnes_attendues:
        if col not in df.columns:
            df[col] = None

    df = df[colonnes_attendues].copy()
    df["indice_confort"] = df.apply(indice_confort, axis=1)
    df["emoji"] = df["description_meteo"].fillna("").apply(meteo_emoji)
    return df


@st.cache_data(ttl=1800)
def charger_donnees_api(api_key: str) -> pd.DataFrame:
    url = "https://api.openweathermap.org/data/2.5/weather"
    resultats = []

    for ville, query in villes.items():
        param = {
            "q": query,
            "appid": api_key,
            "units": "metric",
            "lang": "fr",
        }
        try:
            response = requests.get(url, params=param, timeout=20)
            data = response.json()
        except requests.RequestException as exc:
            resultats.append(
                {
                    "ville": ville,
                    "temperature": None,
                    "ressenti": None,
                    "humidite": None,
                    "vitesse_vent": None,
                    "description_meteo": f"Erreur reseau: {exc}",
                }
            )
            continue

        if data.get("cod") != 200:
            resultats.append(
                {
                    "ville": ville,
                    "temperature": None,
                    "ressenti": None,
                    "humidite": None,
                    "vitesse_vent": None,
                    "description_meteo": f"Erreur API: {data.get('message', 'inconnue')}",
                }
            )
            continue

        resultats.append(
            {
                "ville": data.get("name", ville),
                "temperature": data.get("main", {}).get("temp"),
                "ressenti": data.get("main", {}).get("feels_like"),
                "humidite": data.get("main", {}).get("humidity"),
                "vitesse_vent": data.get("wind", {}).get("speed"),
                "description_meteo": (data.get("weather") or [{}])[0].get("description", ""),
            }
        )

    return normaliser_dataframe(pd.DataFrame(resultats))


@st.cache_data(ttl=1800)
def charger_donnees_pipeline() -> pd.DataFrame:
    if not DATA_PATH.exists():
        return pd.DataFrame()
    return normaliser_dataframe(pd.read_csv(DATA_PATH))


# Section 1 — En-tete
st.title("🌤️ WeatherFlow — Dashboard Meteo")
st.markdown("Donnees meteo en direct via OpenWeather pour 5 villes europeennes.")

api_key = os.getenv("OPENWEATHER_API_KEY")

if st.button("Rafraichir les donnees"):
    if not api_key:
        st.error("OPENWEATHER_API_KEY manquante: impossible de rafraichir via API.")
    else:
        charger_donnees_api.clear()
        df_live = charger_donnees_api(api_key)
        if not df_live.empty:
            df_live.drop(columns=["emoji"], errors="ignore").to_csv(DATA_PATH, index=False)
            st.success("Donnees rafraichies depuis l'API.")
        else:
            st.warning("Rafraichissement API echoue, conservation des donnees existantes.")
    st.rerun()

st.divider()

# Section 2 — Vue globale
df = charger_donnees_pipeline()
source = "CSV transforme"

if df.empty and api_key:
    df = charger_donnees_api(api_key)
    source = "API en direct"

if df.empty:
    st.error("Aucune donnee disponible. Lance d'abord le pipeline fetch/transform ou configure la cle API.")
    st.stop()

st.caption(f"Source des donnees: {source}")

st.dataframe(
    df[["ville", "temperature", "ressenti", "humidite", "vitesse_vent", "description_meteo", "indice_confort"]],
    width="stretch",
)

fig = px.bar(
    df,
    x="ville",
    y="temperature",
    color="temperature",
    color_continuous_scale="RdYlBu_r",
    title="Temperatures par ville",
)
st.plotly_chart(fig, width="stretch")

# Section 3 — Detail par ville
ville_choisie = st.selectbox("Choisir une ville", sorted(df["ville"].dropna().unique().tolist()))
ligne = df.loc[df["ville"] == ville_choisie].iloc[0]

if pd.isna(ligne["temperature"]):
    st.error(f"Donnees indisponibles pour {ville_choisie}: {ligne['description_meteo']}")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Temperature", f"{float(ligne['temperature']):.1f} C")
with col2:
    st.metric("Ressenti", f"{float(ligne['ressenti']):.1f} C")
with col3:
    st.metric("Humidite", f"{int(ligne['humidite'])}%")

col4, col5 = st.columns(2)
with col4:
    st.metric("Vent", f"{float(ligne['vitesse_vent']) * 3.6:.1f} km/h")
with col5:
    st.metric("Indice confort", f"{float(ligne['indice_confort']):.1f}/10")

st.markdown(f"### {ligne['emoji']} {ligne['description_meteo']}")

# Section 4 — Recommandation IA
best = df.sort_values("indice_confort", ascending=False).iloc[0]
reco = (
    f"Meilleure destination ce week-end : {best['ville']} "
    f"avec {float(best['temperature']):.1f} C et {best['description_meteo']}."
)

st.success(reco)
st.caption("Recommandation generee automatiquement a partir des donnees meteo du moment.")
