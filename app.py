import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURATION ET BASE DE DONNÉES
# ==========================================
DB_NAME = "gmao_signalisation.db"

def init_db():
    """Initialise la base de données SQLite selon le CDC"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interventions (
            id_intervention TEXT PRIMARY KEY,
            date_heure TEXT,
            article_nom TEXT,
            localisation TEXT,
            type_maint TEXT,
            mesure_securite TEXT,
            description TEXT,
            etat_final TEXT
            -- Note: Pour un prototype simple, nous ne stockons pas les BLOB des images, 
            -- mais on pourrait stocker leurs chemins d'accès locaux.
        )
    ''')
    conn.commit()
    conn.close()

def generate_id():
    """Génère un ID unique basé sur la date et l'heure"""
    return f"TKT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# ==========================================
# 2. INTERFACE UTILISATEUR (STREAMLIT)
# ==========================================
st.set_page_config(page_title="GMAO Signalisation", page_icon="🚦", layout="centered")

init_db()

# Barre de navigation latérale
st.sidebar.title("🚦 GMAO SLT")
menu = st.sidebar.radio("Navigation", ["Nouvelle Intervention", "Tableau de Bord / Historique"])

# --- ONGLET 1 : MODULE DE MAINTENANCE (Saisie) ---
if menu == "Nouvelle Intervention":
    st.header("🛠️ Saisie d'une Intervention")
    
    # ID généré automatiquement
    ticket_id = generate_id()
    st.info(f"**ID d'intervention :** {ticket_id}")
    
    with st.form("form_intervention", clear_on_submit=True):
        st.subheader("A. Fiche d'identité de l'équipement")
        col1, col2 = st.columns(2)
        with col1:
            article = st.selectbox("Type d'article", 
                                   ["Armoire de commande", "Feu de signalisation", "Câblage", "Capteur", "Poste HTA"])
        with col2:
            localisation = st.text_input("Localisation (ex: Carrefour X, Coordonnées GPS)")
            
        st.subheader("B. Détails de la Maintenance")
        type_maint = st.radio("Type de Maintenance", ["Préventive", "Corrective", "Curative"], horizontal=True)
        
        # Champ de sécurité spécifique à l'électricité
        securite = st.radio("⚠️ Mesure de sécurité : Consignation électrique effectuée ?", ["OUI", "NON", "Non Applicable"], horizontal=True)
        
        st.write("📸 **Documentation Visuelle**")
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            photo_avant = st.file_uploader("Photo AVANT (Obligatoire)", type=["jpg", "png", "jpeg"])
        with col_img2:
            photo_apres = st.file_uploader("Photo APRÈS", type=["jpg", "png", "jpeg"])
            
        description = st.text_area("Description de l'action menée", placeholder="Ex: Remplacement du relais thermique, Serrage des borniers...")
        etat_final = st.selectbox("État Final de l'équipement", ["Fonctionnel", "À surveiller", "Hors service"])
        
        # Bouton de soumission
        submitted = st.form_submit_button("Enregistrer l'intervention")
        
        if submitted:
            if not localisation:
                st.error("Veuillez renseigner la localisation.")
            elif not photo_avant:
                st.warning("⚠️ La photo 'AVANT' est obligatoire selon le cahier des charges.")
            elif securite == "NON" and type_maint != "Préventive":
                st.error("🛑 Intervention bloquée : La consignation électrique est obligatoire pour les actions correctives/curatives.")
            else:
                # Sauvegarde dans la base de données
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute('''
                    INSERT INTO interventions 
                    (id_intervention, date_heure, article_nom, localisation, type_maint, mesure_securite, description, etat_final)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (ticket_id, date_actuelle, article, localisation, type_maint, securite, description, etat_final))
                conn.commit()
                conn.close()
                st.success(f"✅ L'intervention {ticket_id} a été enregistrée avec succès !")

# --- ONGLET 2 : TABLEAU DE BORD ET HISTORIQUE ---
elif menu == "Tableau de Bord / Historique":
    st.header("📊 Historique des Interventions")
    
    # Lecture des données depuis SQLite
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM interventions ORDER BY date_heure DESC", conn)
    conn.close()
    
    if df.empty:
        st.info("Aucune intervention enregistrée pour le moment.")
    else:
        # Métriques rapides
        st.subheader("Vue d'ensemble")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Interventions", len(df))
        col_m2.metric("En état 'Hors service'", len(df[df['etat_final'] == 'Hors service']))
        col_m3.metric("Interventions Curatives", len(df[df['type_maint'] == 'Curative']))
        
        # Affichage du tableau de données
        st.dataframe(df, use_container_width=True)
        
        # Bouton d'export CSV (Alternative rapide à l'export PDF pour un prototype)
        st.download_button(
            label="📥 Exporter l'historique en CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='historique_gmao_slt.csv',
            mime='text/csv',
        )