####
# code issu de l'auteur de la chaine youtube : The Decoder

import streamlit as st
import h5py
from sklearn.neighbors import NearestNeighbors
import spacy
from smolagents import CodeAgent, HfApiModel, tool
from huggingface_hub import login
from time import sleep
import random as random

login(token="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")

# from sentence_transformers import SentenceTransformer

k_neigh = 4

@tool
def question_type(qtype: str, from_article: str) -> str:
    """
    Generates a question based on the type provided.
    Args:
        qtype: The type of question to ask (either "mcq", "open", "exam" or "default").
        from_article: The content of the article to generate the question from. If from_article is "random", generate a question on a random subject.
    """
    if from_article == "random":
        from_article = st.session_state['document_contents'][random.randint(0, len(st.session_state['document_contents']))]
        
        
    if qtype == "open":
        return "Generate an open question, with potentially sub questions, based on the following article : " + from_article
    elif qtype == "exam":
        return "Generate multiple questions, mixing mcq and open questions, based on the following article : " + from_article
    else:
        return "Generate a multiple choice questions with 4 choices, based on the following article : " + from_article

@tool
def article(subject: str, nb_article: int) -> str:
    """
    Returns the most appropriate articles for the given subject. The content returned shall not be deformed or rephrased in any way.
    Args:
        subject: The subject to find articles related to.
        nb_article: The number of articles to return (between 1 and 4).
    """
    
    query_emb = st.session_state['model_emb'](subject).vector
    _, idx = st.session_state['document_neighbours'].kneighbors([query_emb])
    # print(idx[0], len(st.session_state['document_contents']))
    context = [st.session_state['document_contents'][i] for i in idx[0]]
    
    context = context[:nb_article]
    
    return "The following articles are relevant to the question : " + "\n".join(context)


# SYSTEM_PROMPT = """
# If you ever need information about European patent law, ALWAYS and ONLY refer to the \"article\" tool.
# You have TWO main tasks.
# Task 1 : You need to generate questions about European patent law, but DO NOT answer them.
# Task 2 : When an answer to a patent-law-related question is given, you need to provide constructive and rigorous feedback text (with articles quotes to support your claim).
# After each query, you need to figure out which task is beeing asked of you. ONLY ONE is beeing asked per query.
# If none of the two tasks matches the query, explain your role.
# """

SYSTEM_PROMPT = """
You are responsible for writing questions to test students on European patent law.
Students will ask you for questions. If a specific topic is mentionned, ask them about it, otherwise, select at random.
You are not responsible for answering questions, only for asking them.
When receiving a USER's answer, you will evaluate it and provide feedback.
Your knowledge about European patent law is limited to what you can get from the tool [article].
"""
st.title("Lawris")

if "model_emb" not in st.session_state:
    st.session_state['model_emb'] = spacy.load('en_core_web_md')


if "question_embedding" not in st.session_state:
    with h5py.File("../bin/question_embeddings.h5", 'r') as h5file:
        st.session_state['question_embedding'] = h5file['vectors'][:]
        st.session_state['question_contents'] = h5file['text'][:]
        st.session_state['question_contents'] = [s.decode('utf-8') for s in st.session_state['question_contents']]
    st.session_state['question_neighbours'] = NearestNeighbors(n_neighbors=k_neigh, algorithm='auto').fit(st.session_state['question_embedding'])

if "document_embedding" not in st.session_state:
    with h5py.File("../bin/article_embeddings.h5", 'r') as h5file:
        st.session_state['document_embedding'] = h5file['vectors'][:]
        st.session_state['document_contents'] = h5file['text'][:]
        st.session_state['document_contents'] = [s.decode('utf-8') for s in st.session_state['document_contents']]
    print(st.session_state['document_contents'])
    st.session_state['document_neighbours'] = NearestNeighbors(n_neighbors=k_neigh, algorithm='auto').fit(st.session_state['document_embedding'])

# initialize history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{'role': 'system', 'content' : ""}]

# init models
if "model" not in st.session_state:
    question_generator = CodeAgent(tools=[question_type, article], model=HfApiModel(), max_steps=5, name="question_generator", description="Generates a question based on articles.")
    answer_generator = CodeAgent(tools=[article], model=HfApiModel(), max_steps=5, name="answer_generator", description="Generates a very detailed answer to a patent law question with relevant quotes with their sources.")
    answer_comparator = CodeAgent(tools=[], model=HfApiModel(), max_steps=5, name="answer_comparator", description="Compares the answer generator's response to the user's to a question and provide feedback.", managed_agents=[answer_generator])
    st.session_state["main_agent"] = CodeAgent(tools=[article], model=HfApiModel(), max_steps = 5, managed_agents=[question_generator, answer_comparator])

def model_res_generator():
    for message in st.session_state['messages']:
        if message['role'] != 'system':
            continue
        message['content'] = SYSTEM_PROMPT
    final_message = ""
    for message in st.session_state["messages"]:
        final_message += message["role"] + ": " + message["content"] + "\n"
    results = st.session_state["main_agent"].run(final_message)
    # for word in results.split(' '):
    #     sleep(0.05)
    yield results

# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to know?"):
    # add latest message to history in format {role, content}
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message = st.write_stream(model_res_generator())
        # pour gérer la mémoire, ajouter ici le contenu du message de l'assistant avec le bon role
        st.session_state["messages"].append({'role': 'assistant', 'content': message})