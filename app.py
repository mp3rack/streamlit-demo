import streamlit as st
import mysql.connector
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import plotly.express as px




# 👤 Zugangsdaten festlegen
USERNAME = "admin"
PASSWORD = "RESUFED"

# Session-Authentifizierung
if "auth" not in st.session_state:
    st.session_state.auth = False

def login():
    st.title("🔐 Login erforderlich")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.auth = True
        else:
            st.error("Zugangsdaten falsch!")

# App-Inhalt nur anzeigen, wenn eingeloggt
if not st.session_state.auth:
    login()
else:

    st.set_page_config(layout="wide")
    st.title("📅 Track-Visualisierung mit Geschwindigkeit")

    # 🕛 Datumsauswahl
    selected_date = st.date_input("Wähle ein Datum", value=datetime.today().date())
    start_of_day = datetime.combine(selected_date, datetime.min.time())
    end_of_day = datetime.combine(selected_date, datetime.max.time())

    # 💡 Datenbankverbindung
    conn = mysql.connector.connect(
        host="192.168.56.101",
        user="DEFUSER",
        password="RESUFED",
        database="GPS2"
    )
    cursor = conn.cursor()

    # SQL-Abfrage mit Zeitfilter
    query = """
        SELECT latitude, longitude, time, speed
        FROM LOCATIONS
        WHERE time BETWEEN %s AND %s
        ORDER BY time ASC
    """
    cursor.execute(query, (start_of_day, end_of_day))
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    if not results:
        st.warning("Kein Track für das ausgewählte Datum gefunden.")
        st.stop()

    # 📊 Daten vorbereiten
    df = pd.DataFrame(results, columns=["latitude", "longitude", "time", "speed"])
    df["speed_kmh"] = df["speed"] * 3.6

    # 🕰️ Auswahlzeitpunkt per Slider
    timestamps = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()
    selected_time_str = st.select_slider("🕒 Zeitpunkt im Track auswählen", options=timestamps)
    selected_time = pd.to_datetime(selected_time_str)
    selected_row = df[df["time"] == selected_time].iloc[0]
    selected_coord = (selected_row["latitude"], selected_row["longitude"])

    # 📈 Geschwindigkeit mit Plotly visualisieren
    fig = px.line(df, x="time", y="speed_kmh", title="Geschwindigkeit über Zeit (km/h)", labels={"time": "Zeit", "speed_kmh": "Geschwindigkeit (km/h)"})
    fig.update_traces(line=dict(color="orange"))
    fig.add_scatter(x=[selected_time], y=[selected_row["speed_kmh"]], mode="markers", marker=dict(color="red", size=10), name="Ausgewählt")
    st.plotly_chart(fig, use_container_width=True)

    # 🌍 Karte mit Track & Marker erzeugen
    center_lat, center_lon = df.iloc[0]["latitude"], df.iloc[0]["longitude"]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14)
    track_coords = list(zip(df["latitude"], df["longitude"]))
    folium.PolyLine(track_coords, color="green", weight=4.5, opacity=0.8).add_to(m)

    # Start/Ende markieren
    folium.Marker(track_coords[0], tooltip="Start").add_to(m)
    folium.Marker(track_coords[-1], tooltip="Ende").add_to(m)

    # Ausgewählten Punkt markieren
    folium.Marker(
        location=selected_coord,
        popup=f"Ausgewählter Zeitpunkt\n{selected_time_str}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    st.subheader(f"🗺️ Karte vom {selected_date.strftime('%d.%m.%Y')}")
    st_folium(m, width=900, height=600)