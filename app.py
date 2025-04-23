import streamlit as st
import pandas as pd
import numpy as np

st.title("📈 Interaktive Datenvisualisierung mit Streamlit")

# Anzahl der Datenpunkte auswählen
anzahl = st.slider("Wie viele Datenpunkte willst du sehen?", 10, 1000, 100)

# Zufallsdaten generieren
daten = pd.DataFrame({
    "x": np.arange(anzahl),
    "y": np.random.randn(anzahl).cumsum()
})

# Linie oder Punktdiagramm wählen
diagramm_typ = st.selectbox("Diagrammtyp auswählen", ["Linie", "Punkte"])

# Diagramm anzeigen
if diagramm_typ == "Linie":
    st.line_chart(daten.set_index("x"))
else:
    st.scatter_chart(daten)

# Optionale Zusatzinfo
if st.checkbox("Daten anzeigen"):
    st.dataframe(daten)
