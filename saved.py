import streamlit as st
import mysql.connector
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

selected_date = st.date_input("Wähle ein Datum", value=datetime.today().date())

start_of_day = datetime.combine(selected_date, datetime.min.time())
end_of_day = datetime.combine(selected_date, datetime.max.time())


# Datenbankverbindung herstellen
conn = mysql.connector.connect(
    host="192.168.56.101",
    user="DEFUSER",
    password="RESUFED",
    database="GPS2"
)
cursor = conn.cursor()


query = """
    SELECT Latitude, Longitude, Time, Speed
    FROM LOCATIONS
    WHERE Time BETWEEN %s AND %s 
    ORDER BY Time ASC
"""

cursor.execute(query, (start_of_day, end_of_day))
results = cursor.fetchall()

# Verbindung schließen
cursor.close()
conn.close()

import pandas as pd
import altair as alt

# Ergebnisse in DataFrame umwandeln
df = pd.DataFrame(results, columns=["Latitude", "Longitude", "Time", "Speed"])

# Geschwindigkeit in km/h umrechnen
df["speed_kmh"] = df["Speed"] * 3.6

# Diagramm erstellen
st.subheader("📈 Geschwindigkeit über Zeit (km/h)")

chart = alt.Chart(df).mark_line(color="orange").encode(
    x=alt.X("Time:T", title="Zeit"),
    y=alt.Y("speed_kmh:Q", title="Geschwindigkeit (km/h)")
).properties(
    width=900,
    height=300
).interactive()

st.altair_chart(chart, use_container_width=True)

# Check: Hat die Abfrage Ergebnisse?
if not results:
    st.warning("Kein Track gefunden.")
else:
    # Karte zentrieren
    center_lat, center_lon,_,_ = results[0]
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # Trackpunkte zu einer Linie verbinden
    coordinates = [(lat, lon) for lat, lon,x,y in results]
    folium.PolyLine(coordinates, color="blue", weight=4.5, opacity=0.8).add_to(m)

    # Anzeige in Streamlit
    st_folium(m, width=900, height=600)
