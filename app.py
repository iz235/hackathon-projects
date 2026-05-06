import streamlit as st
import os
import time
import uuid
import json
import speech_recognition as sr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# =========================================================
# 1. CONFIGURATION ET STYLES
# =========================================================
st.set_page_config(page_title="AgoraGen", page_icon="💙", layout="wide")
load_dotenv()

# CSS pour le design
st.markdown("""
<style>
    .stApp { background-color: #f4f6f7; }
    .chat-bubble {
        background-color: white; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-left: 5px solid #3498db;
    }
    .id-card {
        background-color: #e8f8f5; border: 2px dashed #27ae60;
        padding: 15px; border-radius: 10px; text-align: center;
        font-size: 24px; font-weight: bold; color: #27ae60;
        margin: 10px 0;
    }
    .role-badge { 
        padding: 5px 10px; border-radius: 5px; font-weight: bold; color: white;
        display: inline-block; margin-bottom: 10px;
    }
    .nav-btn { width: 100%; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. GESTION BASE DE DONNÉES (JSON)
# =========================================================
DB_FILE = "users_db.json"

def charger_donnees():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

def sauvegarder_donnees(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

# Initialisation Session
if 'user_status' not in st.session_state: st.session_state['user_status'] = None
if 'current_user_id' not in st.session_state: st.session_state['current_user_id'] = None
if 'user_type' not in st.session_state: st.session_state['user_type'] = None
if 'transcript_temp' not in st.session_state: st.session_state['transcript_temp'] = ""
if 'page_active' not in st.session_state: st.session_state['page_active'] = "profil" # profil, mentorat, certification

# =========================================================
# 3. FONCTIONS IA & AUDIO
# =========================================================

def ecouter_micro():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        placeholder = st.empty()
        placeholder.info("🎙️ J'écoute... Parlez maintenant !")
        try:
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=8, phrase_time_limit=10)
            placeholder.success("✅ Reçu !")
            texte = r.recognize_google(audio, language="fr-FR")
            time.sleep(1)
            placeholder.empty()
            return texte
        except:
            placeholder.warning("Je n'ai rien entendu.")
            return None

def analyser_profil_senior(texte):
    """Analyse pour Senior"""
    if not os.getenv("OPENAI_API_KEY"): return "⚠️ Clé API manquante."
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    prompt = ChatPromptTemplate.from_template("""
    Tu es l'IA d'AgoraGen. Analyse ce récit de senior : "{recit}"
    Extrais 3 Compétences Clés (Savoir-faire ou Soft Skills).
    Réponds en HTML simple.
    """)
    return (prompt | llm | StrOutputParser()).invoke({"recit": texte})

def analyser_profil_jeune(texte):
    """Analyse pour Jeune (Nouveau !)"""
    if not os.getenv("OPENAI_API_KEY"): return "⚠️ Clé API manquante."
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    prompt = ChatPromptTemplate.from_template("""
    Tu es l'IA d'AgoraGen. Analyse ce récit d'un jeune : "{recit}"
    
    Tâche :
    1. Détermine sa CATÉGORIE (Étudiant, Entrepreneur, Chercheur d'emploi).
    2. Identifie ses BESOINS principaux (ex: Gestion stress, Aide projet, Mathématiques).
    3. Résume son profil en 2 lignes.
    
    Réponds en HTML simple avec des <b> pour les titres.
    """)
    return (prompt | llm | StrOutputParser()).invoke({"recit": texte})

# =========================================================
# 4. PAGE D'ACCUEIL (INSCRIPTION / CONNEXION)
# =========================================================
db_users = charger_donnees()

if st.session_state['user_status'] is None:
    st.markdown("<h1 style='text-align: center; color: #2C3E50;'>Bienvenue sur AgoraGen 💙</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📝 Inscription")
        role = st.selectbox("Je suis...", ["Choisir...", "Senior (60+)", "Jeune / Étudiant", "Entreprise"])
        if st.button("CRÉER MON COMPTE", type="primary"):
            if role != "Choisir...":
                uid = f"{role[:3].upper()}-{str(uuid.uuid4().hex)[:4].upper()}"
                db_users[uid] = {'role': role, 'profil_ia': None}
                sauvegarder_donnees(db_users)
                st.success(f"Compte créé ! ID : {uid}")
                st.info("Notez bien cet identifiant.")
    
    with c2:
        st.subheader("🔐 Connexion")
        uid_input = st.text_input("Votre Identifiant :")
        if st.button("SE CONNECTER"):
            db_users = charger_donnees() # Rafraichir
            if uid_input.strip() in db_users:
                st.session_state['user_status'] = 'connecte'
                st.session_state['current_user_id'] = uid_input.strip()
                st.session_state['user_type'] = db_users[uid_input.strip()]['role']
                st.rerun()
            else:
                st.error("Identifiant inconnu.")

# =========================================================
# 5. ESPACE CONNECTÉ
# =========================================================
elif st.session_state['user_status'] == 'connecte':
    uid = st.session_state['current_user_id']
    user_data = db_users.get(uid)
    role = user_data['role']
    
    # --- BARRE DE NAVIGATION (SIDEBAR) ---
    with st.sidebar:
        st.title("💙 Menu")
        st.markdown(f"**ID:** `{uid}`")
        color = "#2ecc71" if "Senior" in role else "#3498db" if "Jeune" in role else "#e67e22"
        st.markdown(f'<span class="role-badge" style="background-color:{color}">{role}</span>', unsafe_allow_html=True)
        st.markdown("---")
        
        # MENU NAVIGATION JEUNE
        if "Jeune" in role:
            if st.button("👤 Mon Profil", use_container_width=True): st.session_state['page_active'] = "profil"
            if st.button("🤝 Mentorat", use_container_width=True): st.session_state['page_active'] = "mentorat"
            if st.button("📜 Certification", use_container_width=True): st.session_state['page_active'] = "certification"
        
        # MENU SENIOR (Simple pour l'instant)
        elif "Senior" in role:
             if st.button("👤 Mon Profil", use_container_width=True): st.session_state['page_active'] = "profil"

        st.markdown("---")
        if st.button("🔒 Déconnexion"):
            st.session_state['user_status'] = None
            st.rerun()

    # --- CONTENU PRINCIPAL ---
    
    # =====================================================
    # ONGLET 1 : MON PROFIL (Commun à tous, mais adapté)
    # =====================================================
    if st.session_state['page_active'] == "profil":
        st.header(f"👤 Mon Profil ({role})")
        
        # Si profil vide -> On lance le remplissage IA
        if user_data.get('profil_ia') is None:
            st.info("⚠️ Votre profil est vide. Discutons pour le remplir !")
            
            if st.button("🤖 PARLER À L'IA (Remplir profil)", use_container_width=True):
                st.session_state['mode_ecoute'] = True

            if st.session_state.get('mode_ecoute'):
                st.markdown('<div class="chat-bubble"><b>🤖 IA :</b> Racontez-moi votre situation (Études, Projets, Besoins...).</div>', unsafe_allow_html=True)
                
                c1, c2 = st.columns([1,3])
                with c1:
                    if st.button("🎙️ MICRO"):
                        txt = ecouter_micro()
                        if txt: st.session_state['transcript_temp'] = txt
                        st.rerun()
                with c2:
                    if st.session_state['transcript_temp']:
                        st.text_area("Entendu :", st.session_state['transcript_temp'])
                        if st.button("✨ Valider et Analyser"):
                            with st.spinner("Analyse..."):
                                # CHOIX DE L'IA SELON LE ROLE
                                if "Senior" in role:
                                    res = analyser_profil_senior(st.session_state['transcript_temp'])
                                else:
                                    res = analyser_profil_jeune(st.session_state['transcript_temp'])
                                
                                db_users[uid]['profil_ia'] = res
                                sauvegarder_donnees(db_users)
                                st.session_state['mode_ecoute'] = False
                                st.session_state['transcript_temp'] = ""
                                st.rerun()

        # Si profil rempli -> On affiche
        else:
            st.success("✅ Profil complet")
            st.markdown(f'<div class="chat-bubble" style="border-left: 5px solid {color};">{user_data["profil_ia"]}</div>', unsafe_allow_html=True)
            if st.button("🗑️ Effacer mon profil pour recommencer"):
                db_users[uid]['profil_ia'] = None
                sauvegarder_donnees(db_users)
                st.rerun()

    # =====================================================
    # ONGLET 2 : MENTORAT (Uniquement pour Jeunes)
    # =====================================================
    elif st.session_state['page_active'] == "mentorat":
        st.header("🤝 Mentorat & Mise en relation")
        
        # Vérification : Le jeune a-t-il rempli son profil ?
        if user_data.get('profil_ia') is None:
            st.warning("⛔ Vous devez d'abord remplir votre profil (Onglet 'Mon Profil') pour que l'IA puisse trouver le bon mentor.")
        else:
            st.markdown("### 🔍 Mentors recommandés pour vous")
            
            found_mentor = False
            for u_id, u_data in db_users.items():
                # On cherche des seniors avec un profil rempli
                if "Senior" in u_data['role'] and u_data.get('profil_ia'):
                    found_mentor = True
                    st.markdown(f"""
                    <div class="chat-bubble" style="border-left: 5px solid #2ecc71;">
                        <h4>👴 Senior ID: {u_id}</h4>
                        {u_data['profil_ia']}
                        <hr>
                        <button style="background:#2ecc71;color:white;border:none;padding:5px;border-radius:5px;">📞 Contacter pour Mentorat</button>
                    </div>
                    """, unsafe_allow_html=True)
            
            if not found_mentor:
                st.info("🕵️ Aucun mentor senior disponible pour l'instant. Revenez plus tard !")

    # =====================================================
    # ONGLET 3 : CERTIFICATION (Uniquement pour Jeunes)
    # =====================================================
    elif st.session_state['page_active'] == "certification":
        st.header("📜 Certification par des Experts")
        st.write("Obtenez une validation de vos compétences par nos seniors experts.")
        
        # Logique demandée : Vérifier s'il y a des experts certifiés (Vide pour l'instant)
        experts_dispo = False # À changer plus tard quand on codera la partie expert
        
        if not experts_dispo:
            st.warning("⚠️ Aucun Expert Certifié disponible pour valider vos compétences pour l'instant.")
            st.info("Cette fonctionnalité sera bientôt activée une fois les premiers seniors validés.")
        else:
            st.success("Voici les experts disponibles...")