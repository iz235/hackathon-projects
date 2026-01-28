import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
from openai import OpenAI

# --- IMPORTS CORRIGÉS ET VALIDÉS ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage

# 1. Charger la clé API depuis le fichier .env
load_dotenv()

# Vérification de sécurité
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Clé API manquante ! Vérifiez votre fichier .env")
    st.stop()

# --- FONCTION DE SYNTHÈSE VOCALE ---
def text_to_speech(text):
    """Convertit le texte en audio avec OpenAI TTS"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Voix féminine douce et chaleureuse
            input=text,
            speed=0.95  # Légèrement plus lent pour une meilleure compréhension
        )
        
        # Sauvegarder temporairement l'audio
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(audio_path.name)
        
        return audio_path.name
    except Exception as e:
        st.error(f"Erreur lors de la génération audio : {e}")
        return None

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Assistant Aidant IA", page_icon="💙")

st.title("💙 Assistant Intelligent pour Aidants")
st.markdown("""
**Objectif :** Soulager votre charge mentale. Déposez un document médical (PDF, image d'ordonnance ou compte-rendu), 
et je vous aide à comprendre et à organiser les prochaines étapes.
""")

# --- BARRE LATÉRALE (Configuration) ---
with st.sidebar:
    st.header("1. Importez le document")
    uploaded_file = st.file_uploader(
        "Choisissez un fichier", 
        type=["pdf", "png", "jpg", "jpeg"]
    )
    
    st.markdown("---")
    st.markdown("**🔊 Lecture vocale**")
    st.info("Après chaque réponse, vous pourrez écouter l'audio généré automatiquement.")
    
    st.markdown("---")
    st.markdown("**Confidentialité :**")
    st.info("Les données sont traitées temporairement et ne sont pas conservées. (Privacy by Design)")

# --- FONCTION POUR ANALYSER LES IMAGES ---
def encode_image(image_file):
    """Encode l'image en base64 pour l'API OpenAI Vision"""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def analyze_image_document(image_file, question):
    """Analyse un document médical via image avec GPT-4 Vision"""
    base64_image = encode_image(image_file)
    
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0, max_tokens=2000)
    
    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"""Tu es un assistant médical spécialisé dans l'aide aux aidants familiaux.
Analyse attentivement ce document médical (ordonnance, compte-rendu, radiologie, etc.).

RÈGLES IMPORTANTES :
1. LIS TRÈS ATTENTIVEMENT tous les détails du document (diagnostic, résultats, prescriptions)
2. Utilise un ton empathique et rassurant
3. Explique les termes médicaux complexes entre parenthèses
4. Si tu vois des médicaments, rendez-vous ou examens prescrits, liste-les clairement
5. Base-toi UNIQUEMENT sur ce qui est écrit dans le document - ne devine JAMAIS
6. Si le document mentionne des résultats anormaux, explique-les simplement sans alarmer

Question de l'aidant : {question}

Réponds de manière structurée et claire."""
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ]
    )
    
    response = llm.invoke([message])
    return response.content

# --- FONCTIONNEL ---

if uploaded_file is not None:
    file_type = uploaded_file.type
    
    # Détection du type de fichier
    is_image = file_type.startswith('image/')
    is_pdf = file_type == 'application/pdf'
    
    if is_image:
        # Afficher l'image uploadée
        st.success("✅ Image analysée avec succès !")
        image = Image.open(uploaded_file)
        st.image(image, caption="Document uploadé", use_container_width=True)
        
        # Interface de Chat pour images
        st.divider()
        st.subheader("💬 Posez vos questions sur ce document")
        
        # Boutons rapides
        col1, col2 = st.columns(2)
        if col1.button("Que dois-je faire maintenant ?"):
            user_question = "Analyse ce document médical et dis-moi : quelles sont les actions prioritaires ? Y a-t-il des médicaments à prendre, des examens à faire, ou des rendez-vous à prévoir ?"
            with st.spinner("Analyse en cours..."):
                try:
                    # Reset file pointer
                    uploaded_file.seek(0)
                    reponse = analyze_image_document(uploaded_file, user_question)
                    st.write(reponse)
                    
                    # Lecture vocale
                    with st.spinner("🔊 Génération de l'audio..."):
                        audio_file = text_to_speech(reponse)
                        if audio_file:
                            st.audio(audio_file, format='audio/mp3')
                            st.success("✅ Vous pouvez écouter la réponse ci-dessus")
                except Exception as e:
                    st.error(f"Erreur : {e}")
        
        if col2.button("Explique-moi ce document simplement"):
            user_question = "Explique-moi ce document médical de façon simple et rassurante. Qu'est-ce que ça dit exactement ? Quels sont les résultats et que signifient-ils ?"
            with st.spinner("Traduction en langage simple..."):
                try:
                    uploaded_file.seek(0)
                    reponse = analyze_image_document(uploaded_file, user_question)
                    st.write(reponse)
                    
                    # Lecture vocale
                    with st.spinner("🔊 Génération de l'audio..."):
                        audio_file = text_to_speech(reponse)
                        if audio_file:
                            st.audio(audio_file, format='audio/mp3')
                            st.success("✅ Vous pouvez écouter la réponse ci-dessus")
                except Exception as e:
                    st.error(f"Erreur : {e}")
        
        # Zone de texte libre
        user_input = st.text_input("Ou écrivez votre question ici :")
        if user_input:
            with st.spinner("Réflexion de l'assistant..."):
                try:
                    uploaded_file.seek(0)
                    reponse = analyze_image_document(uploaded_file, user_input)
                    st.markdown(reponse)
                    
                    # Lecture vocale
                    with st.spinner("🔊 Génération de l'audio..."):
                        audio_file = text_to_speech(reponse)
                        if audio_file:
                            st.audio(audio_file, format='audio/mp3')
                            st.success("✅ Vous pouvez écouter la réponse ci-dessus")
                except Exception as e:
                    st.error(f"Erreur : {e}")
    
    elif is_pdf:
        # 1. Sauvegarde temporaire du fichier pour que LangChain puisse le lire
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        # 2. Chargement et lecture du PDF
        st.success("✅ Document PDF analysé avec succès !")
        loader = PyPDFLoader(tmp_file_path)
        pages = loader.load_and_split()

        # 3. Initialisation de l'IA (Le Cerveau)
        try:
            llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=2000)
        except Exception as e:
            st.error(f"Erreur de connexion OpenAI : {e}")
            st.stop()

        # 4. Le PROMPT amélioré
        template_perso = """Tu es un assistant médical spécialisé dans l'aide aux aidants familiaux et aux personnes âgées.
Ta mission est d'analyser ce document médical et de l'expliquer simplement.

RÈGLES IMPORTANTES :
1. LIS ATTENTIVEMENT le document - base-toi sur les informations RÉELLES qu'il contient
2. Si c'est un compte-rendu radiologique ou d'imagerie : explique les résultats trouvés (ex: syndrome alvéolaire, épanchement, etc.)
3. Si c'est une ordonnance : liste les médicaments prescrits
4. Utilise un ton empathique, rassurant et respectueux
5. Explique les termes médicaux complexes entre parenthèses avec des mots simples
6. Si tu vois des rendez-vous ou examens à faire, liste-les clairement
7. NE DEVINE JAMAIS - réponds uniquement basé sur le document

Contexte du document :
{context}

Question de l'aidant : {question}

Réponse structurée et précise :"""
        
        PROMPT = ChatPromptTemplate.from_template(template_perso)
        
        # Créer la chaîne avec LCEL
        def format_docs(docs):
            return "\n\n".join([doc.page_content for doc in docs])
        
        from langchain_core.runnables import RunnablePassthrough
        chain = (
            {"context": lambda x: format_docs(pages), "question": RunnablePassthrough()}
            | PROMPT
            | llm
            | StrOutputParser()
        )

        # Fonction helper pour exécuter la chaîne
        def ask_question(question):
            return chain.invoke(question)

        # 5. Interface de Chat
        st.divider()
        st.subheader("💬 Posez vos questions sur ce document")
        
        # Boutons rapides
        col1, col2 = st.columns(2)
        if col1.button("Que dois-je faire maintenant ?"):
            user_question = "Analyse ce document et dis-moi : quelles sont les actions prioritaires ? Y a-t-il des médicaments à prendre, des examens à faire, ou des rendez-vous à prévoir ?"
            with st.spinner("Analyse en cours..."):
                try:
                    reponse = ask_question(user_question)
                    st.write(reponse)
                    
                    # Lecture vocale
                    with st.spinner("🔊 Génération de l'audio..."):
                        audio_file = text_to_speech(reponse)
                        if audio_file:
                            st.audio(audio_file, format='audio/mp3')
                            st.success("✅ Vous pouvez écouter la réponse ci-dessus")
                except Exception as e:
                    st.error(f"Erreur : {e}")

        if col2.button("Explique-moi ce document simplement"):
            user_question = "Explique-moi ce document médical de façon simple et rassurante. Qu'est-ce que ça dit exactement ? Quels sont les résultats et que signifient-ils ?"
            with st.spinner("Traduction en langage simple..."):
                try:
                    reponse = ask_question(user_question)
                    st.write(reponse)
                    
                    # Lecture vocale
                    with st.spinner("🔊 Génération de l'audio..."):
                        audio_file = text_to_speech(reponse)
                        if audio_file:
                            st.audio(audio_file, format='audio/mp3')
                            st.success("✅ Vous pouvez écouter la réponse ci-dessus")
                except Exception as e:
                    st.error(f"Erreur : {e}")

        # Zone de texte libre
        user_input = st.text_input("Ou écrivez votre question ici :")
        if user_input:
            with st.spinner("Réflexion de l'assistant..."):
                try:
                    reponse = ask_question(user_input)
                    st.markdown(reponse)
                    
                    # Lecture vocale
                    with st.spinner("🔊 Génération de l'audio..."):
                        audio_file = text_to_speech(reponse)
                        if audio_file:
                            st.audio(audio_file, format='audio/mp3')
                            st.success("✅ Vous pouvez écouter la réponse ci-dessus")
                except Exception as e:
                    st.error(f"Erreur : {e}")

        # Nettoyage
        try:
            os.unlink(tmp_file_path)
        except:
            pass

else:
    st.info("👈 Veuillez commencer par charger un document (PDF ou image) dans le menu de gauche.")