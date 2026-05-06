import streamlit as st
import os
import tempfile
import base64
import time
import speech_recognition as sr
from dotenv import load_dotenv
from PIL import Image
from openai import OpenAI

# --- IMPORTS LANGCHAIN ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnablePassthrough

# 1. Charger la clé API
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Clé API manquante ! Vérifiez votre fichier .env")
    st.stop()

# --- INITIALISATION MEMOIRE ---
if 'calendrier' not in st.session_state:
    st.session_state['calendrier'] = []
if 'maison' not in st.session_state:
    st.session_state['maison'] = {"lumiere": "Éteinte", "volets": "Ouverts", "temp": 21, "porte": "Verrouillée"}
if 'constantes' not in st.session_state:
    st.session_state['constantes'] = {"coeur": 72, "mouvement": "Normal", "alerte": False}

# --- FONCTIONS AUDIO ---
def text_to_speech(text):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.audio.speech.create(
            model="tts-1", voice="nova", input=text, speed=1.0
        )
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(audio_path.name)
        return audio_path.name
    except:
        return None

def ecouter_micro():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner("👂 J'écoute..."):
            try:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5)
                texte = r.recognize_google(audio, language="fr-FR")
                return texte
            except:
                return None

# --- CERVEAU AGENT ---
def traiter_commande(texte):
    """Analyse si c'est une commande maison ou une question santé"""
    texte = texte.lower()
    reponse = ""
    action = False

    # Scénarios Domotiques (Smart Home)
    if "lumière" in texte:
        etat = "Allumée" if "allume" in texte else "Éteinte"
        st.session_state['maison']['lumiere'] = etat
        reponse = f"C'est fait, la lumière est {etat}."
        action = True
    elif "volet" in texte:
        etat = "Fermés" if "ferme" in texte else "Ouverts"
        st.session_state['maison']['volets'] = etat
        reponse = f"J'ai {etat.lower()} les volets."
        action = True
    elif "température" in texte or "chauffage" in texte:
        st.session_state['maison']['temp'] = 22
        reponse = "J'ai réglé le chauffage sur 22 degrés pour votre confort."
        action = True
    
    return reponse, action

# --- FONCTIONS ANALYSE DOCUMENT (Votre code existant) ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_image(image_file, question):
    base64_image = encode_image(image_file)
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.3)
    message = HumanMessage(content=[
        {"type": "text", "text": f"Tu es un robot assistant médical. Analyse ce document. Question: {question}"},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
    ])
    return llm.invoke([message]).content

# --- INTERFACE ROBOT ---
st.set_page_config(page_title="Buddy-Bot", page_icon="🤖", layout="wide")

# CSS pour simuler l'écran du robot
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    .robot-screen { border-radius: 25px; background: white; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .metric-card { background: #e3f2fd; border-radius: 10px; padding: 15px; text-align: center; }
    .alert-card { background: #ffebee; border-radius: 10px; padding: 15px; text-align: center; color: red; }
</style>
""", unsafe_allow_html=True)

# BARRE LATÉRALE : TÉLÉSURVEILLANCE & MAISON
with st.sidebar:
    st.image("robot_face.png", caption="Buddy Connecté", use_container_width=True) # Mettez votre image ici
    
    st.header("🏠 Maison Intelligente")
    c1, c2 = st.columns(2)
    c1.metric("🌡️ Temp", f"{st.session_state['maison']['temp']}°C")
    c2.metric("💡 Lumière", st.session_state['maison']['lumiere'])
    st.info(f"Volets : {st.session_state['maison']['volets']}")
    st.info(f"Porte : {st.session_state['maison']['porte']}")

    st.divider()
    
    st.header("❤️ Télésurveillance")
    # Simulation de capteurs
    if st.session_state['constantes']['coeur'] > 100:
        st.markdown('<div class="alert-card">⚠️ RYTHME CARDIAQUE ÉLEVÉ</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card">✅ Constantes Normales</div>', unsafe_allow_html=True)
    
    st.write(f"💓 Pouls : {st.session_state['constantes']['coeur']} bpm")
    st.write(f"🏃 Mouvement : {st.session_state['constantes']['mouvement']}")

# PAGE PRINCIPALE
st.title("🤖 Interface Robot Assistant")

# ONGLETS POUR LES FONCTIONS DU ROBOT
tab1, tab2, tab3 = st.tabs(["🗣️ Discussion & Commandes", "📄 Analyse Médicale", "🚨 Urgence & Rappels"])

with tab1:
    st.markdown("### Je suis à votre écoute")
    col_visage, col_chat = st.columns([1, 2])
    
    with col_visage:
        # Affichage du visage (Image fixe ou animation si on avait des gifs)
        try:
            st.image("robot_face.jpg", use_container_width=True)
        except:
            st.markdown("🤖")
    
    with col_chat:
        st.info("💡 **Essayez de dire :** 'Allume la lumière', 'Ferme les volets' ou 'J'ai mal à la tête'.")
        
        if st.button("🎤 Parler au Robot"):
            commande = ecouter_micro()
            if commande:
                st.success(f"Entendu : {commande}")
                
                # 1. Vérifier si c'est une commande Maison
                rep_domotique, action_faite = traiter_commande(commande)
                
                if action_faite:
                    st.write(rep_domotique)
                    audio = text_to_speech(rep_domotique)
                    st.audio(audio, format="audio/mp3", autoplay=True)
                    time.sleep(1)
                    st.rerun() # Rafraîchir pour voir les changements maison
                else:
                    # 2. Sinon, c'est une conversation (IA)
                    llm = ChatOpenAI(model_name="gpt-3.5-turbo")
                    rep_ia = llm.invoke(f"Tu es un robot compagnon gentil. L'utilisateur dit: {commande}. Réponds courtement.").content
                    st.write(rep_ia)
                    audio = text_to_speech(rep_ia)
                    st.audio(audio, format="audio/mp3", autoplay=True)

with tab2:
    st.markdown("### 🩺 Scanner un document")
    uploaded_file = st.file_uploader("Ordonnance ou Compte-rendu", type=["jpg", "png", "pdf"])
    
    if uploaded_file and st.button("Analyser"):
        with st.spinner("Analyse en cours..."):
            # Ici on reprend votre logique d'analyse d'image précédente
            if uploaded_file.type.startswith('image'):
                reponse = analyze_image(uploaded_file, "Quelles sont les actions ?")
                st.write(reponse)
                # Extraction automatique de RDV (Simulation)
                if "rendez-vous" in reponse.lower():
                    st.toast("📅 Nouveau RDV détecté et ajouté !", icon="✅")
                    st.session_state['calendrier'].append({"date": "15 Mars", "motif": "Cardiologue"})

with tab3:
    st.markdown("### 🛡️ Sécurité & Rappels")
    
    col_rappel, col_urgence = st.columns(2)
    
    with col_rappel:
        st.subheader("💊 Rappels Médicaments")
        st.checkbox("Matin : Doliprane (Pris)", value=True, disabled=True)
        st.checkbox("Midi : Kardégic (À prendre)")
        st.checkbox("Soir : Bisoprolol (À prendre)")
    
    with col_urgence:
        st.subheader("🆘 Alerte Chute / Malaise")
        st.markdown("Les capteurs analysent votre activité...")
        if st.button("SIMULER UNE CHUTE"):
            st.error("🚨 CHUTE DÉTECTÉE !")
            st.write("📞 Appel des urgences et de la famille en cours...")
            audio = text_to_speech("Alerte, chute détectée. Je contacte les secours.")
            st.audio(audio, format="audio/mp3", autoplay=True)