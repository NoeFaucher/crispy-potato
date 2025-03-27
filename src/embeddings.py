import spacy
import numpy as np
import h5py
import json
import re


model = spacy.load('en_core_web_md')


def compute_question_embeddings(questions_json, nlp):
    embeddings = []
    for question_data in questions_json["questions"]:
        question_text = "Question : " + question_data["question"] + " / Answers : "
        for answer in question_data["answer"]:
            question_text += answer["ID"] + " | " + answer["content"] + " | " + str(answer["correct"]) + " <> "
        question_text += " / Explanation : " + question_data["explanation"] + " / Legal Basis : "
        for lb in question_data["legalBasis"]:
            question_text += lb["name"] + " | " + lb["content"]
        doc = nlp(question_text)
        embeddings.append(doc.vector)
    return np.array(embeddings)

def compute_article_embeddings(article_json, nlp):
    embeddings = []
    for article_data in article_json:
        for content in article_data["content"]:
            article_text = re.sub(r'\[.*?\]', '', article_data['title']) + " | " + content["id"] + ": " + content["text"]
            doc = nlp(article_text)
            embeddings.append(doc.vector)
    print(len(embeddings))
    return np.array(embeddings)

def store_question_vectors_in_h5(filename, vectors, dataset_name='vectors'):
    vectors_array = np.array(vectors)
    contents_array = np.array([i['question'].encode('utf-8') for i in contents])

    # Create an .h5 file and store the vectors
    with h5py.File(filename, 'w') as h5file:
        h5file.create_dataset("text", data=contents_array)
        h5file.create_dataset(dataset_name, data=vectors_array)

    print(f"Vectors successfully stored in {filename}")
    
def store_article_vectors_in_h5(filename, vectors, dataset_name='vectors'):
    vectors_array = np.array(vectors)
    contents_array = np.array([(re.sub(r'\[.*?\]', '', i['title']) + " | " + j["id"]).encode("utf-8") for i in contents for j in i["content"]])
    
    # i = -1
    # for string in contents_array:
    #     i+=1
    #     new_string = re.sub(r'\[.*?\]', '', string)
    #     contents_array[i] = new_string.encode('utf-8')
    # Create an .h5 file and store the vectors
    with h5py.File(filename, 'w') as h5file:
        h5file.create_dataset("text", data=contents_array)
        h5file.create_dataset(dataset_name, data=vectors_array)

    print(f"Vectors successfully stored in {filename}")
    

embed = "articles"
if embed == "questions":
    with open('epc_questions.json', 'r') as file:
        questions_json = json.load(file)
        
    contents = questions_json["questions"]

    question_embeddings = compute_question_embeddings(questions_json, model)
    store_question_vectors_in_h5("question_embeddings.h5", question_embeddings)
elif embed == "articles":
    with open('formated/EPC/formated_articles.json', 'r') as file:
        articles_json = json.load(file)
        
    contents = articles_json
    article_embeddings = compute_article_embeddings(articles_json, model)
    store_article_vectors_in_h5("article_embeddings.h5", article_embeddings)
