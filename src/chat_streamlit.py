import streamlit as st
import h5py
from sklearn.neighbors import NearestNeighbors
from smolagents import CodeAgent, HfApiModel, tool
from huggingface_hub import login
import random
from sentence_transformers import SentenceTransformer

# ================
# 1) STYLES GLOBAUX
# ================
st.set_page_config(page_title="Lawris – Chatbot brevet", layout="centered")

# CSS personnalisé pour mettre en valeur le design
CUSTOM_CSS = """
<style>
/* Couleur de fond globale */
/* Fond global : passe d’un beige clair à un gris foncé */
body {
    background-color: #2A2A2A;
}

body, h1, span, div {
    color: #f8e5c4 !important;
}
p{
    color: white !important;
}

button {
    background-color: #cf892d !important;
    color: #ffffff !important;
    border: none;
    border-radius: 0.3rem;
    padding: 0.5rem 1rem;
}

/* Zone centrale */
.block-container {
    background-color: #3C3C3C;
    padding: 2rem;
    border-radius: 0.5rem;
    margin-top: 3rem;
}

/* Titre : garde ton accent original */
h1 {
    color: #f8e5c4 !important ;
    font-weight: 700;
    text-align: left;
    padding-left: 20% !important;
}

/* Bulles de chat : un fond plus sombre et un texte en beige */
div[data-testid="stChatMessage"] {
    background-color: #555555;
    color: #f9e5c2;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
}

/* Input utilisateur : texte sombre sur un fond accentué */
.css-1l02zno {
    background-color: #eca438 !important;
    color: #2A2A2A !important;
    font-size: 1rem !important;
}

/* Placeholder de l'input : beige pour la lisibilité */
.css-1l02zno::placeholder {
    color: #f8e5c4 !important;
}

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ================
# 2) PLACEHOLDERS DES IMAGES
# ================
# Mets ici le chemin vers tes images ou URLs
LAWRIS_IMAGES = {
    "normal":       "../doc/lawris_neutral_web.png",
    "happy":        "../doc/lawris_happy_web.png",
    "sad":          "../doc/lawris_sad_web.png",
    "impressed":    "../doc/lawris_star_web.png"
}

# ====================
# 3) Gestion de l'état du bot (logo) et du score
# ====================
# On stocke le nombre de bonnes réponses dans la session, et l'état actuel du logo
if "correct_answers_count" not in st.session_state:
    st.session_state["correct_answers_count"] = 0

if "lawris_state" not in st.session_state:
    st.session_state["lawris_state"] = "normal"  # peut être "normal", "happy", "sad", "impressed"

def update_lawris_state(correct: bool):
    """
    Met à jour l'état de Lawris (logo) selon la justesse de la réponse.
    - Si correct = True -> +1 dans correct_answers_count
    - Si correct = False -> reset à 0
    - Si on atteint 5 bonnes réponses d'affilée -> "impressed"
    - Sinon "happy" ou "sad"
    """
    if correct:
        st.session_state["correct_answers_count"] += 1
        if st.session_state["correct_answers_count"] >= 5:
            st.session_state["lawris_state"] = "impressed"
        else:
            st.session_state["lawris_state"] = "happy"
    else:
        st.session_state["correct_answers_count"] = 0
        st.session_state["lawris_state"] = "sad"

def reset_lawris_normal():
    """Force Lawris à revenir à l'état normal."""
    st.session_state["lawris_state"] = "normal"

# =============
# 4) HEADER ET LOGO
# =============
# On peut utiliser une colonne pour mettre le logo à gauche et le titre à droite
col1, col2 = st.columns([1,3])
with col1:
    st.image(LAWRIS_IMAGES[st.session_state["lawris_state"]], width=100)

with col2:
    st.title("LAWRIS")

st.write("Bienvenue sur **Lawris**, ton assistant pour réviser tes examens sur les brevets européens !")

# Pour réinitialiser l'état normal (petit bouton)
if st.button("Remettre Lawris à l'état normal"):
    reset_lawris_normal()

# =============
# 5) Code existant pour le RAG
# =============
login(token="******") # Enter your huggingface token

k_neigh = 15

@tool
def question_type(qtype: str, from_article: str) -> str:
    """
    Generates a question based on the type provided.
    Args:
        qtype: The type of question to ask (either "mcq", "open", "exam" or "default").
        from_article: The content of the article to generate the question from. 
                      If from_article is "random", generate a question on a random subject.
    """
    if from_article == "random":
        from_article = st.session_state['document_contents'][
            random.randint(0, len(st.session_state['document_contents']) - 1)
        ]
        
    if qtype == "open":
        return "Generate an open question, with potentially sub questions, based on the following article : " + from_article
    elif qtype == "exam":
        return "Generate multiple questions, mixing mcq and open questions, based on the following article : " + from_article
    else:
        return "Generate a multiple choice questions with 4 choices, based on the following article : " + from_article

@tool
def article(subject: str, nb_article: int) -> str:
    """
    Returns the most appropriate articles for the given subject. The content returned
    shall not be deformed or rephrased in any way.
    Args:
        subject: The subject to find articles related to.
        nb_article: The number of articles to return (between 1 and 15).
    """
    query_emb = st.session_state['model_emb'].encode([subject])
    _, idx = st.session_state['document_neighbours'].kneighbors(query_emb)
    context = [st.session_state['document_contents'][i] for i in idx[0]]
    
    context = context[:nb_article]
    
    return "The following articles are relevant to the question: (CONTEXT) " + "\n (CONTEXT) ".join(context)

SYSTEM_PROMPT = """
You are responsible for writing questions to test students on European patent law.
Students will ask you for questions. If a specific topic is mentionned, ask them about it, otherwise, select at random.
When creating a question, you are not responsible for answering questions, only for asking them.
When receiving a USER's answer, you will evaluate it and provide feedback.
If the student asks you for specifications about a specific topic, answer as detailly as possible, in multiple parts.
Your knowledge about European patent law is limited to what you can get from the tool [article], the articles and rules following (CONTEXT).
"""

if "model_emb" not in st.session_state:
    st.session_state['model_emb'] = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

if "document_embedding" not in st.session_state:
    with h5py.File("../bin/article_embeddings.h5", 'r') as h5file:
        st.session_state['document_embedding'] = h5file['vectors'][:]
        st.session_state['document_contents'] = h5file['text'][:]
        st.session_state['document_contents'] = [
            s.decode('utf-8') for s in st.session_state['document_contents']
        ]
    st.session_state['document_neighbours'] = NearestNeighbors(
        n_neighbors=k_neigh, algorithm='auto'
    ).fit(st.session_state['document_embedding'])

# initialize history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{'role': 'system', 'content': ""}]

# init models
if "model" not in st.session_state:
    from smolagents import CodeAgent, HfApiModel
    question_generator = CodeAgent(
        tools=[question_type, article],
        model=HfApiModel(),
        max_steps=1,
        name="question_generator",
        description="Generates a question based on articles."
    )
    answer_generator = CodeAgent(
        tools=[article],
        model=HfApiModel(),
        max_steps=1,
        name="answer_generator",
        description="Generates a very detailed answer to a patent law question with relevant quotes with their sources."
    )
    answer_comparator = CodeAgent(
        tools=[],
        model=HfApiModel(),
        max_steps=2,
        name="answer_comparator",
        description="Compares the answer generator's response to the user's to a question and provide feedback.",
        managed_agents=[answer_generator]
    )
    st.session_state["main_agent"] = CodeAgent(
        tools=[article],
        model=HfApiModel(),
        max_steps = 3,
        managed_agents=[question_generator, answer_comparator]
    )

def model_res_generator():
    # Force le system prompt
    for message in st.session_state['messages']:
        if message['role'] == 'system':
            message['content'] = SYSTEM_PROMPT

    final_message = ""
    for message in st.session_state["messages"]:
        final_message += message["role"] + ": " + message["content"] + "\n"

    results = st.session_state["main_agent"].run(final_message)
    yield results

# =========================
# 6) AFFICHAGE DES MESSAGES DE LA CONVERSATION
# =========================
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# 7) GESTION DE L'INPUT UTILISATEUR
# =========================
prompt = st.chat_input("Pose ta question sur le brevet, ou réponds à la question posée !")

if prompt:
    # Exemple BÊTA : détection random d'une "bonne" vs "mauvaise" réponse pour la démo
    # => à adapter en fonction de la logique d'évaluation de ton agent
    # Par exemple, si l'agent compare la réponse, tu peux parser la réponse et décider correct = True/False
    # Ici on fait un random pour la démo
    import random
    correct_answer = random.choice([True, False])
    
    # On met à jour l'humeur
    update_lawris_state(correct_answer)

    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message = st.write_stream(model_res_generator())
        st.session_state["messages"].append({'role': 'assistant', 'content': message})

# Pour mémoire: quand l'utilisateur reload la page, st.chat_message
# réaffichera tout l'historique
