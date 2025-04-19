import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from io import BytesIO

st.set_page_config(page_title="Organisationsdiagnostik nach Meihei", layout="wide")

# Lade Datenstruktur
with open("wesenselemente.json", "r", encoding="utf-8") as f:
    wesenselemente = json.load(f)

st.title("🧭 Organisationsdiagnostik nach Meihei")
st.markdown("Gib für jedes Unterkapitel den **SOLL**- und **IST**-Wert ein (Skala 0–10).")

data = []

# Eingabeformular
with st.form("diagnose_form"):
    for element, inhalt in wesenselemente.items():
        st.subheader(f"{element} – {inhalt['Kernziel']}")
        for punkt in inhalt["Unterkapitel"]:
            tooltip = punkt["Beschreibung"]
            col1, col2 = st.columns(2)
            with col1:
                soll = st.slider(f"SOLL – {punkt['Titel']}", 0, 10, 7, key=f"{element}_{punkt['Titel']}_soll", help=tooltip)
            with col2:
                ist = st.slider(f"IST – {punkt['Titel']}", 0, 10, 5, key=f"{element}_{punkt['Titel']}_ist", help=tooltip)
            data.append({
                "Wesenselement": element,
                "Unterkapitel": punkt["Titel"],
                "SOLL": soll,
                "IST": ist,
                "Abweichung": soll - ist
            })
    submitted = st.form_submit_button("Auswertung anzeigen")

if submitted:
    df = pd.DataFrame(data)

    st.success("✅ Daten erfasst – hier ist deine Auswertung!")

    # Anzeige der Tabelle
    st.dataframe(df, use_container_width=True)

    # Gesamtabweichung je Element
    summary = df.groupby("Wesenselement")[["SOLL", "IST", "Abweichung"]].sum().reset_index()
    max_diff_element = summary.loc[summary["Abweichung"].idxmax()]

    st.subheader("📊 Übersicht nach Wesenselementen")
    st.dataframe(summary, use_container_width=True)

    st.markdown(f"""
    ### 🎯 Schwerpunkt der Entwicklung
    **{max_diff_element['Wesenselement']}** mit einer Gesamtabweichung von **{int(max_diff_element['Abweichung'])}** Punkten.
    """)

    # Spider Chart
    st.subheader("📈 Visualisierung (SOLL vs IST je Element)")
    categories = summary["Wesenselement"].tolist()
    values_soll = summary["SOLL"].tolist()
    values_ist = summary["IST"].tolist()

    categories += [categories[0]]
    values_soll += [values_soll[0]]
    values_ist += [values_ist[0]]

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values_soll, linewidth=2, linestyle='solid', label='SOLL')
    ax.plot(angles, values_ist, linewidth=2, linestyle='dashed', label='IST')
    ax.fill(angles, values_ist, color='orange', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_yticklabels([])
    ax.set_title("Radar Chart – Organisationsdiagnostik", size=14)
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    st.pyplot(fig)

    # Excel-Export
    st.subheader("⬇️ Exportiere deine Ergebnisse")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Detaildaten', index=False)
        summary.to_excel(writer, sheet_name='Übersicht', index=False)
    st.download_button(
        label="📥 Excel-Datei herunterladen",
        data=output.getvalue(),
        file_name="organisationsdiagnostik_meihei.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
