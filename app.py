import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import io

# ==========================================
# 1. CONFIGURATION CLOUD (SUPABASE)
# ==========================================
# Vous devrez créer un compte gratuit sur supabase.com et mettre vos clés ici
# (En production, ces clés se mettent dans les "Secrets" de Streamlit)
SUPABASE_URL = "votre_url_supabase_ici"
SUPABASE_KEY = "votre_cle_api_supabase_ici"

# Initialisation de la connexion (désactivée le temps que vous mettiez vos clés)
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. SYSTÈME DE CONNEXION (LOGIN)
# ==========================================
st.set_page_config(page_title="GMAO SLT - Cloud", page_icon="🚦", layout="centered")

if 'utilisateur' not in st.session_state:
    st.session_state.utilisateur = None
    st.session_state.role = None

# Écran de connexion
if st.session_state.utilisateur is None:
    st.title("🔐 Connexion GMAO SLT")
    utilisateur = st.selectbox("Qui êtes-vous ?", ["Technicien 1 (Ali)", "Technicien 2 (Omar)", "Technicien 3 (Said)", "Superviseur (Vous)"])
    mot_de_passe = st.text_input("Mot de passe", type="password")
    
    if st.button("Se connecter"):
        # Mots de passe basiques pour l'exemple
        if "Technicien" in utilisateur and mot_de_passe == "tech123":
            st.session_state.utilisateur = utilisateur
            st.session_state.role = "Technicien"
            st.rerun()
        elif "Superviseur" in utilisateur and mot_de_passe == "admin123":
            st.session_state.utilisateur = utilisateur
            st.session_state.role = "Superviseur"
            st.rerun()
        else:
            st.error("Mot de passe incorrect.")
    st.stop() # Arrête le code ici si non connecté

# ==========================================
# 3. APPLICATION PRINCIPALE
# ==========================================
st.sidebar.success(f"👤 Connecté en tant que : {st.session_state.utilisateur}")
if st.sidebar.button("Déconnexion"):
    st.session_state.utilisateur = None
    st.session_state.role = None
    st.rerun()

# --- VUE TECHNICIEN : SAISIE ---
if st.session_state.role == "Technicien":
    st.header("🛠️ Nouvelle Intervention")
    
    with st.form("form_tech"):
        article = st.selectbox("Équipement", ["Armoire", "Feu de signalisation", "Câblage"])
        localisation = st.text_input("Localisation (Carrefour)")
        type_maint = st.radio("Type", ["Préventive", "Corrective"])
        
        st.write("📸 Preuves Visuelles")
        photo = st.camera_input("Prendre une photo (Obligatoire)")
        
        description = st.text_area("Travaux réalisés")
        etat = st.selectbox("État Final", ["Fonctionnel", "À surveiller", "Hors service"])
        
        if st.form_submit_button("Envoyer au Superviseur"):
            if photo and localisation:
                # LOGIQUE CLOUD À ACTIVER (Exemple) :
                # 1. Envoyer la photo dans le "Bucket" Supabase
                # file_path = f"photos/{datetime.now().timestamp()}.jpg"
                # supabase.storage.from_("photos").upload(file_path, photo.getvalue())
                
                # 2. Envoyer les données texte dans la Table "interventions"
                # data = {"technicien": st.session_state.utilisateur, "date": str(datetime.now()), "equipement": article, "photo_url": file_path, "etat": etat}
                # supabase.table("interventions").insert(data).execute()
                
                st.success("✅ Intervention envoyée et synchronisée en temps réel !")
            else:
                st.error("La photo et la localisation sont obligatoires.")

# --- VUE SUPERVISEUR : CONTRÔLE ET HISTORIQUE ---
elif st.session_state.role == "Superviseur":
    st.header("👑 Espace Superviseur - Contrôle en Temps Réel")
    
    st.info("Ici, vous voyez les interventions remonter en direct du terrain.")
    
    # LOGIQUE CLOUD À ACTIVER :
    # reponse = supabase.table("interventions").select("*").execute()
    # df = pd.DataFrame(reponse.data)
    
    # Données fictives pour vous montrer le rendu
    df_fictive = pd.DataFrame({
        "Date": ["2026-05-12 10:30", "2026-05-12 11:15"],
        "Technicien": ["Technicien 1 (Ali)", "Technicien 3 (Said)"],
        "Équipement": ["Feu de signalisation", "Armoire"],
        "Localisation": ["Avenue Hassan II", "Agdal"],
        "État": ["Fonctionnel", "À surveiller"]
    })
    
    st.dataframe(df_fictive, use_container_width=True)
    
    st.subheader("Détail et validation")
    ticket_selectionne = st.selectbox("Choisir une intervention à inspecter", df_fictive["Localisation"])
    if st.button("Voir les photos associées"):
        st.write("*(Ici s'affichera la photo téléchargée depuis le cloud par le technicien)*")
        st.image("https://via.placeholder.com/400x200.png?text=Photo+du+terrain", caption=f"Photo à {ticket_selectionne}")
