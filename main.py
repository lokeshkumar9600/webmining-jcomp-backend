from fastapi import FastAPI
from newspaper import Article
from fastapi.middleware.cors import CORSMiddleware
import random
import string
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import warnings
import requests
warnings.filterwarnings('ignore')
nltk.download('punkt', quiet=True)


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sentence_list = []

@app.get("/")
async def root():
    return {"message" : "hello world"}


@app.get("/query/{question}")
async def returnSimilarity(question):
    return {"query" :question}
    


@app.get("/buildx")
async def getData():
    searchList =  ["https://en.wikipedia.org/wiki/Indian_Premier_League","https://en.wikipedia.org/wiki/Chennai_Super_Kings","https://en.wikipedia.org/wiki/Delhi_Capitals","https://en.wikipedia.org/wiki/Gujarat_Titans","https://en.wikipedia.org/wiki/Kolkata_Knight_Riders","https://en.wikipedia.org/wiki/Lucknow_Super_Giants","https://en.wikipedia.org/wiki/Mumbai_Indians","https://en.wikipedia.org/wiki/Punjab_Kings","https://en.wikipedia.org/wiki/Rajasthan_Royals","https://en.wikipedia.org/wiki/Royal_Challengers_Bangalore","https://en.wikipedia.org/wiki/Sunrisers_Hyderabad","https://en.wikipedia.org/wiki/M._A._Chidambaram_Stadium"]
    for x in searchList:
        article = Article(x)
        article.download()
        article.parse()
        article.nlp()
        corpus = article.text
        text = corpus
        newSentence = nltk.sent_tokenize(text)
        print("processed data @" + x)
        sentence_list.extend(newSentence)
    return{"list" : sentence_list}

@app.get("/getanswer/{question}")
async def getAnswer(question):
    print(question)
    def greeting(text):
             text = text.lower()
             bot_greetings = ['how do you do', 'Hi', 'Hey', 'Hey there!']
             user_greetings = ['hi', 'hey', 'Hello', 'hola', 'whats up']

             for word in text.split():
                    if word in user_greetings:
                        return random.choice(bot_greetings)
                    
    def index_sort(list_var):
        length = len(list_var)
        list_index = list(range(0, length))

        x = list_var
        for i in range(length):
                for j in range(length):
                     if x[list_index[i]] > x[list_index[j]]:
                            temp = list_index[i]
                            list_index[i] = list_index[j]
                            list_index[j] = temp
        
        return list_index
    
    def bot_response(user_input):
       user_input = user_input.lower()
       sentence_list.append(user_input)

       bot_response = ''
       cm = CountVectorizer().fit_transform(sentence_list)
       sim_score = cosine_similarity(cm[-1], cm)
       similarity_score_list = sim_score.flatten()
       index = index_sort(similarity_score_list)
       index = index[1:]
       response_flag = 0

       j = 0
       for i in range(len(index)):
                if similarity_score_list[index[i]] > 0.0:
                        bot_response = bot_response + ' ' + sentence_list[index[i]]
                        response_flag = 1
                        j = j+1
                if j > 2:
                     break
                 
       if response_flag == 0:
                     bot_response = bot_response + ' ' + 'I dont get it!'
                     sentence_list.remove(user_input)

       return bot_response
    print('I am a ipl Bot')
    exit_list = ['exit', 'see you', 'bye']
    if question.lower() in exit_list:
             return {"data" : "bye bye"}
             
    else:
            if greeting(question) != None:
                          return{greeting(question)}
            else:
                          return{bot_response(question)}



@app.get("/testroute")
async def testing():
       data = requests.get("http://127.0.0.1:8000/buildx")
       return {"data" : data.json()}



