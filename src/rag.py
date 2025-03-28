
import streamlit as st
import h5py
from sklearn.neighbors import NearestNeighbors
from huggingface_hub import login
from time import sleep
import random as random
from sentence_transformers import SentenceTransformer
import re
from ollama import chat, ChatResponse
from mistralai import Mistral
import os
from transformers import pipeline
import torch



class Model:
    def __init__(self, model_name="mistral-small-latest", temperature=0.7):
        self.client = Mistral(api_key="yxSHnTCv8xWT77A8Cv1OXvqkQT9DaKUX")
        self.model_name = model_name
        self.temperature = temperature

    def __call__(self, messages, stop_sequences=None, grammar=None):
        """Makes the model callable for smolagents using OpenAI's updated API."""
        
        response = self.client.chat.complete(
            model=self.model_name,
            messages=messages,  # Already in OpenAI format
            temperature=self.temperature,
            stop=stop_sequences,  # Handle stop sequences if provided
            tool_choice="none"
        )
        return response.choices[0].message.content  # New way to access content

model = Model()

# class Model:
#     def __init__(self, model_name="mistral-small-latest", temperature=0.7):
#         self.model_name = model_name
        
#         self.pipe = pipeline(
#             "image-text-to-text",
#             model=model_name,
#             device="cpu",
#             torch_dtype=torch.bfloat16
#         )
#         self.temperature = temperature

#     def __call__(self, messages, stop_sequences=None, grammar=None):
#         """Makes the model callable for smolagents using OpenAI's updated API."""
#         new_messages = []
#         for m in messages:
#             new_messages.append({
#                 "role": m["role"],
#                 "content": [
#                     {"type": "text", "text": m["content"]}
#                 ]
#             }
#         )
#         print(new_messages)
#         output = self.pipe(text=new_messages)
#         return output[0]["generated_text"][-1]["content"]


# model = Model(model_name="google/gemma-3-4b-it")




def retrival(subject: str, nb_article: int) -> str:
    """
    Returns the most appropriate articles for the given subject. The content returned shall not be deformed or rephrased in any way.
    Args:
        subject: The subject to find articles related to.
        nb_article: The number of articles to return.
    """
    query_emb = st.session_state['model_emb'].encode([subject])
    _, idx = st.session_state['document_neighbours'].kneighbors(query_emb)
    # print(idx[0], len(st.session_state['document_contents']))
    context = [st.session_state['document_contents'][i] for i in idx[0]]
    
    context = context[:nb_article]
    
    return "The following articles are relevant to the question: (CONTEXT) " + "\n (CONTEXT) ".join(context)



SYSTEM_PROMPT = """
Students will ask you questions about patent law.
Give a detailled anwser using only the context (CONTEXT) you get.
If the context is not relevant with the user answer, tell the user and don't answer.
If you can determine what the user want from the question, ask him to specifie the question.
"""

st.title("RAG patent law chatbot")

if "model_emb" not in st.session_state:
    st.session_state['model_emb'] = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    

if "document_embedding" not in st.session_state:
    k_neigh = 15
    with h5py.File("../bin/article_embeddings.h5", 'r') as h5file:
        st.session_state['document_embedding'] = h5file['vectors'][:]
        st.session_state['document_contents'] = h5file['text'][:]
        st.session_state['document_contents'] = [s.decode('utf-8') for s in st.session_state['document_contents']]
    st.session_state['document_neighbours'] = NearestNeighbors(n_neighbors=k_neigh, algorithm='auto').fit(st.session_state['document_embedding'])


# initialize history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{'role': 'system', 'content' : ""}]



def model_res_generator(context):
    for message in st.session_state['messages']:
        if message['role'] != 'system':
            continue
        message['content'] = SYSTEM_PROMPT
    l = st.session_state['messages']
    l[-1]["content"] += context
    results = model(st.session_state['messages'])
    
    yield results

# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What do you want to know?"):
    # add latest message to history in format {role, content}
    
    verif = f"""
    If a user ask : "{prompt}".
    he want to :
     - (INFORMATION) ask more information about an article
     - (QUESTION) get a question about a subject
     - (ANSWER) get an answer to a question he ask
    Give only the topic the user want (INFORMATION,QUESTION,ANSWER) or OTHER if it doesn't correspond to anything.
    If you choose INFORMATION, i also want between doubles quotes the subject of the information the user askes.
    If you choose QUESTION, i also want between doubles quotes the subject of the question the user askes.
    """
    
    choice = model([{"role": "system", "content": "When you are asked to answer only with some responses give only what you are asked to. In the smallest answer possible"},{"role": "user", "content": verif}])
    
    
    if "INFORMATION" in choice:
        print(choice)
        subject = re.findall("\"(.*)\"",choice,re.M|re.S)[0]
        
        ret = retrival(subject,10)
        
        context = "\n" + ret
    
    elif "QUESTION" in choice:
        print(choice)
        context = ""
    elif "ANSWER" in choice:
        context = ""
    elif "OTHER" in choice:
        context = ""
    
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message = st.write_stream(model_res_generator(context))
        # pour gérer la mémoire, ajouter ici le contenu du message de l'assistant avec le bon role
        st.session_state["messages"].append({'role': 'assistant', 'content': message})