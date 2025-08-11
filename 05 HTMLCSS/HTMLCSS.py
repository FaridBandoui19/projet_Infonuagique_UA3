from flask import Flask, render_template, request, jsonify
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
import os # Importation du module os pour de meilleures pratiques de chemin

# 🎯 Étape cruciale : Assurez-vous que 'pdf_text.txt' est le fichier que vous lisez.
# Ce fichier contient tout le contenu de votre Landon-Hotel.pdf extrait.
# Il est recommandé de s'assurer que le chemin est correct, potentiellement en utilisant un chemin absolu
# ou en s'assurant que pdf_text.txt est dans le même répertoire que ce script.
try:
    prompt = open('pdf_text.txt', 'r', encoding='utf-8').read()
except FileNotFoundError:
    print("Erreur : Le fichier 'pdf_text.txt' n'a pas été trouvé.")
    print("Veuillez vous assurer que 'pdf_text.txt' est dans le même dossier que ce script, ou fournissez le chemin complet.")
    # Vous pouvez choisir de quitter l'application ou de gérer cette erreur différemment
    exit() 


# Définition du template pour le prompt. C'est ici que la "personnalité" du chatbot est définie
# et que le contenu de votre PDF est injecté comme base de connaissances.
hotel_assistant_template = prompt + """
You are the hotel manager of Landon Hotel, named "Mr. Landon". 
Your expertise is exclusively in providing information and advice about anything related to Landon Hotel. 
This includes any general Landon Hotel related queries. 
You do not provide information outside of this scope. 
If a question is not about Landon Hotel, respond with, "I can't assist you with that, sorry!" 
Question: {question} 
Answer: 
"""

# Création de l'objet PromptTemplate de LangChain.
# Il indique que 'question' est la seule variable d'entrée que le template attend.
hotel_assistant_prompt_template = PromptTemplate( 
    input_variables=["question"], 
    template=hotel_assistant_template 
) 

# Initialisation du modèle OpenAI.
# 🚀 Changement du modèle vers 'gpt-4o-mini' comme convenu.
# temperature=0 est maintenue pour des réponses précises et factuelles, non créatives.
llm = OpenAI(model='gpt-4o-mini', temperature=0) 

# Création de la chaîne LangChain (LLMChain).
# Le pipe '|' envoie la sortie du prompt formaté directement au modèle de langage.
llm_chain = hotel_assistant_prompt_template | llm 

# Fonction utilitaire pour interroger le modèle LLM avec une question donnée.
def query_llm(question): 
    # La méthode 'invoke' de la chaîne LangChain exécute l'ensemble du processus
    # (préparation du prompt + appel au LLM).
    response = llm_chain.invoke({'question': question}) 
    return response # Retourne la réponse brute du LLM.

# Initialisation de l'application Flask.
app = Flask(__name__) 

# Définition de la route racine ('/') qui sert la page HTML principale du chatbot.
@app.route("/") 
def index(): 
    # Flask cherche 'index.html' dans le dossier 'templates'.
    # Assurez-vous que le dossier 'templates' existe à la racine de votre projet
    # et que 'index.html' s'y trouve.
    return render_template("index.html") 

# Définition de la route '/chatbot' qui gère les requêtes POST du frontend JavaScript.
@app.route("/chatbot", methods=["POST"]) 
def chatbot(): 
    # Récupération des données JSON envoyées par le frontend.
    data = request.get_json() 
    # Extraction de la question de l'utilisateur.
    question = data["question"] 
    # Appel à la fonction qui interroge le chatbot (via LangChain et OpenAI).
    response = query_llm(question) 
    # Renvoi de la réponse du chatbot au frontend au format JSON.
    return jsonify({"response": response}) 

# Point d'entrée de l'application.
# Lance le serveur Flask. 'debug=True' est utile pour le développement
# car il redémarre le serveur automatiquement en cas de modification du code.
if __name__ == "__main__": 
    app.run(debug=True)


































# from flask import Flask, render_template, request, jsonify
# from langchain_openai import OpenAI
# from langchain.prompts import PromptTemplate

# prompt = open('website_text.txt', 'r').read()

# hotel_assistant_template = prompt + """
# You are the hotel manager of Landon Hotel, named "Mr. Landon". 
# Your expertise is exclusively in providing information and advice about anything related to Landon Hotel. 
# This includes any general Landon Hotel related queries. 
# You do not provide information outside of this scope. 
# If a question is not about Landon Hotel, respond with, "I can't assist you with that, sorry!" 
# Question: {question} 
# Answer: 
# """

# hotel_assistant_prompt_template = PromptTemplate( 
#     input_variables=["question"], 
#     template=hotel_assistant_template 
#     ) 

# llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0) 

# llm_chain = hotel_assistant_prompt_template | llm 

# def query_llm(question): 
#     response = llm_chain.invoke({'question': question}) 
#     return response 

# app = Flask(__name__) 

# @app.route("/") 
# def index(): 
#     return render_template("index.html") 

# @app.route("/chatbot", methods=["POST"]) 
# def chatbot(): 
#     data = request.get_json() 
#     question = data["question"] 
#     response = query_llm(question) 
#     return jsonify({"response": response}) 

# if __name__ == "__main__": 
#     app.run(debug=True)