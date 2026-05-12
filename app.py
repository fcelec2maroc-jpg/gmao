import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURATION & BASE DE DONNÉES ---
DB_NAME = "gmao_slt.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interventions 
                 (id_ticket TEXT PRIMARY KEY, date_inter TEXT, equipement TEXT, 
                  type_maint TEXT, description TEXT, statut TEXT)''')
    conn.commit()
    conn.close()

def generate_ticket_id():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id_ticket FROM interventions", conn)
    conn.close()
    
    prefix = f"SLT-{datetime.now().year}-"
    if df.empty:
        return f"{prefix}001"
    else:
        # Extraction du numéro séquentiel et incrémentation
        last_id = df['id_ticket'].iloc[-1]
        last_num = int(last_id.split('-')[-1])
        return f"{prefix}{str(last_num + 1).zfill(3)}"

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="GMAO SLT", layout="wide")
init_db()

st.title("🚦 GMAO - Signalisation Lumineuse Tricolore")
st.sidebar.header("Navigation")
menu = st.sidebar.radio("Aller à :", ["Nouvelle Intervention", "Historique & Rapports"])

if menu == "Nouvelle Intervention":
    st.subheader("🛠️ Enregistrement d'une maintenance")
    
    # Génération automatique de l'ID
    ticket_id = generate_ticket_id()
    st.info(f"**N° de Ticket :** {ticket_id}")

    with st.form("maint_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date_j = st.date_input("Date d'intervention", datetime.now())
            equipement = st.selectbox("Équipement concerné", 
                                    ["Armoire de commande", "Mât tricolore", "Bouton piéton", "Répétiteur Velo"])
            type_maint = st.radio("Type de maintenance", ["Préventive", "Corrective", "Curative"])
        
        with col2:
            statut = st.select_slider("État final", options=["Hors service", "À surveiller", "Fonctionnel"])
            description = st.text_area("Description des travaux")

        # Gestion des photos
        st.write("---")
        c1, c2 = st.columns(2)
        photo_before = c1.camera_input("Photo AVANT")
        photo_after = c2.camera_input("Photo APRÈS")

        submit = st.form_submit_button("Enregistrer l'intervention")

    if submit:
        if description:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO interventions VALUES (?,?,?,?,?,?)", 
                      (ticket_id, str(date_j), equipement, type_maint, description, statut))
            conn.commit()
            conn.close()
            st.success(f"Ticket {ticket_id} enregistré avec succès !")
            # Note : Dans une version réelle, on sauvegarderait les photos dans un dossier 'media/'
        else:
            st.error("Veuillez remplir la description.")

elif menu == "Historique & Rapports":
    st.subheader("📂 Historique des interventions")
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM interventions ORDER BY id_ticket DESC", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Petit export CSV rapide
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger l'historique (CSV)", csv, "export_gmao.csv", "text/csv")
    else:
        st.warning("Aucune donnée enregistrée pour le moment.")