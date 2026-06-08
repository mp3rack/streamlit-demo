import streamlit as st

import mysql.connector
import pandas as pd

import folium
from streamlit_folium import st_folium

import plotly.express as px

from datetime import datetime

st.set_page_config(layout="wide")

# Perform Login
def login():
    st.title("🔐 Please login")
    username = st.text_input("User")
    password = st.text_input("Pass", type="password")
    
    if st.button("Login"):
        if username == "admin" and password == "RESUFED":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Invalid credentials!")

def run():
    st.title("📅 Track and Speed")

    selected_start_date = st.date_input("Select start", value=datetime.today().date())
    selected_end_date = st.date_input("Select ebd", value=datetime.today().date())
    
    start_of_day = datetime.combine(selected_start_date, datetime.min.time())
    end_of_day = datetime.combine(selected_end_date, datetime.max.time())

    with mysql.connector.connect(
        host="192.168.56.101",
        user="DEFUSER",
        password="RESUFED",
        database="GPS2"
    ) as conn:
        with conn.cursor() as cursor:

            query = """
                SELECT latitude, longitude, time, speed
                FROM LOCATIONS
                WHERE time BETWEEN %s AND %s
                ORDER BY time ASC
            """

            cursor.execute(query, (start_of_day, end_of_day))
            results = cursor.fetchall()
        conn.close()

    if not results:
        st.warning("No track for selected date.")
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

    st_folium(m, use_container_width=True, height=400)

    # 📈 Geschwindigkeit mit Plotly visualisieren
    fig = px.line(df, x="time", y="speed_kmh", title="Geschwindigkeit über Zeit (km/h)", labels={"time": "Zeit", "speed_kmh": "Geschwindigkeit (km/h)"})
    fig.update_traces(line=dict(color="orange"))
    fig.add_scatter(x=[selected_time], y=[selected_row["speed_kmh"]], mode="markers", marker=dict(color="red", size=10), name="Ausgewählt")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

# App-Inhalt nur anzeigen, wenn eingeloggt
if not st.session_state.auth:
    login()
else:
    run()
