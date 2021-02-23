# deep-learning-voice-assistant
import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import os
import wikipedia
import speech_recognition as sr
import time
import geocoder
from requests import get
from datetime import datetime
from playsound import playsound
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# # # All Initial Setups for Libraries # # #

#LancasterStemmer
stemmer = LancasterStemmer()

#Set up for IBM Watson TTS (10,000 characters per month!)
apikey = 'Mj28UncAcGQJ77c0Yoh7hNygQrgKUfQm3G_RSWHHKzCE'
url = 'https://api.us-east.text-to-speech.watson.cloud.ibm.com/instances/75bbecd0-25d5-485e-9d3d-6db3d9748baa'
authenticator = IAMAuthenticator(apikey)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url)

#Permission for JSON file
with open("intents.json") as file:
    data = json.load(file)

#Latitude and Longitude
try:
    ip = get('https://api.ipify.org').text
    g = geocoder.ip(ip)
except:
    None

# # # Initial Setup Ends Here # # #

#Start of Neural Network

try:
    print("Initializing Neural Network...")
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    print("Training Neural Network...")
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])


            #stem the words first
    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []
    #create an array of 0's for the range of total stemmed words
    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):

        #bag is a vector
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)


    training = numpy.array(training)
    output = numpy.array(output)

tensorflow.reset_default_graph()


net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 60)
net = tflearn.fully_connected(net, 60)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

#try:
    #model.load("model.tflearn")
#except:
model.fit(training, output, n_epoch=1000, batch_size=60, show_metric=True)
model.save("model.tflearn")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
    return numpy.array(bag)


def search(query):
    print("Note: Internet is required")
    query = query.split(' ')
    query = " ".join(query[0:])
    #how many sentences the wikipedia entry should have?
    x_amount_of_sentences = 3
    try:
        print(wikipedia.summary(query, sentences = x_amount_of_sentences))
        TTS(wikipedia.summary(query, sentences = x_amount_of_sentences-2))
    except:
        print("Sorry, I couldn't find your answer in the wikipedia database.")


def time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("The current time is " + current_time + ".")
    TTS("The current time is " + current_time + ".")

def weather():
    api_key = "24beaaa11a9ae3d1af5b88eea0882954"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    #Add speech to text here
    #city_name = input("What's your city?: ")
    complete_url = base_url + "lat=" + str(g.lat) + "&lon=" + str(g.lng) + "&appid=" + api_key
    response = get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        current_pressure = y["pressure"]
        current_humidity = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        #converting kelvin to fahrenheit
        x = current_temperature
        kelvin_minus = x - 273.15
        current_temperature_fahrenheit_unrounded = (kelvin_minus * 9)/5 + 32
        current_temperature_fahrenheit = round(current_temperature_fahrenheit_unrounded, 4)
        if current_temperature_fahrenheit < 50:
            print("It's pretty cold outside. The temperature is " + str(current_temperature_fahrenheit) + " fahrenheit.")
            TTS("It's pretty cold outside. The temperature is " + str(current_temperature_fahrenheit) + " fahrenheit.")
        elif current_temperature_fahrenheit > 80:
            print("It's pretty hot outside. The temperature is " + str(current_temperature_fahrenheit) + " fahrenheit.")
            TTS("It's pretty hot outside. The temperature is " + str(current_temperature_fahrenheit) + " fahrenheit.")
        else:
            print("The temperature is okay, around " + str(current_temperature_fahrenheit) + " fahrenheit.")
            TTS("The temperature is okay, around " + str(current_temperature_fahrenheit) + " fahrenheit.")
        if current_humidity > 60:
            print("It's also quite damp. The humidity is around " + str(current_humidity) + " percent.")
            TTS("It's also quite damp. The humidity is around " + str(current_humidity) + " percent.")
        else:
            print("The humidity is around " + str(current_humidity) + " percent.")
            TTS("The humidity is around " + str(current_humidity) + " percent.")
        print("We are looking at some " + weather_description + " as well as an atmospheric pressure of " + str(current_pressure) + ".")
    else:
        print("I'm sorry, I couldn't seem to find your city.")
    return

#for stuff inside intent, if tag no exist, then append new JSON structure + new tag into intent array in JSON file
template_json = {
              "tag": None,
              "patterns": [],
              "responses": [],
              "context_set": ""
                }

#Voice Synthesizer
def TTS(phrase):
    try:
        with open('speech.mp3', 'wb') as audio_file:
            res = tts.synthesize(phrase, accept='audio/mp3', voice='en-US_AllisonV3Voice').get_result()
            audio_file.write(res.content)
        playsound('speech.mp3')
        os.remove('speech.mp3')
    except:
        print("IBM Watson's TTS is not working. Perhaps you hit the 10,000 word count?")

#Function to chat without voice
def chat_without_voice():
    while True:
        inp = input("Input: ")
        if inp.lower() == "quit":
            print("You've exited voice mode.")
            break
        results = model.predict([bag_of_words(inp, words)]).squeeze()
        results_index = numpy.argmax(results)
        tag = labels[results_index]
#last left off on finding a solution to an indexing problem of results[results_index]
#the solution to literally all of this: results = model.predict([bag_of_words(inp, words)]).squeeze() . The squeeze removes an extra empty dimension in the numpy array, which is the cause for the out of bounds error
        if results[results_index] > 0.7:
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']
                    TTS(random.choice(responses))
                    print("Lambda: " + random.choice(responses))
            if tag == "query":
                query_input = input("Query: ")
                search(query_input)
            if tag == "time":
                time()
            if tag == "commandWeather":
                try:
                    weather()
                except:
                    print("I couldn't retrieve the weather.")
        else:
            inp2 = input("I'm sorry, I don't understand. What would I classify your response as? [Example: 'Sarcasm'] (Type Exit to leave): ")
            if inp2.lower() == "exit":
                break
            with open("tempintents.json") as file2:
                data2 = json.load(file2)
                for someintent in data2["intents"]:
                    if inp2.lower() == someintent["tag"]:
                        print("Tag " + inp2 + " already exists!")
                        break
                    else:
                        print("Tag registered.")
                        template_json["tag"] = str(inp2)
                        template_json["patterns"].append(inp)
                        config2 = json.loads(open('tempintents.json').read())
                        config2["intents"].append(template_json)
                        with open('tempintents.json','w') as f:
                            f.write(json.dumps(config2))
                            template_json["tag"] = None
                            template_json["patterns"] = [None]
                            break



def chat_with_voice(speech):
        inp = speech
        print("Input: " + speech)
        results = model.predict([bag_of_words(inp, words)]).squeeze()
        results_index = numpy.argmax(results)
        tag = labels[results_index]
#last left off on finding a solution to an indexing problem of results[results_index]
#the solution to literally all of this: results = model.predict([bag_of_words(inp, words)]).squeeze() . The squeeze removes an extra empty dimension in the numpy array, which is the cause for the out of bounds error
        if results[results_index] > 0.7:
            for tg in data["intents"]:
                if tg['tag'] == tag:
                    responses = tg['responses']
                    TTS(random.choice(responses))
                    print(random.choice(responses))
                if tag == "query":
                    query_input = input("Query: ")
                    search(query_input)
                    break
                if tag == "time":
                    time()
                    break
                if tag == "commandWeather":
                    weather()
                    break
                if tag == "error":
                    listen()
                    break
        else:
            print("I'm sorry, I don't understand.")

def listen():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as s:
            r.adjust_for_ambient_noise(s)
            audio = r.listen(s)
            speech = r.recognize_google(audio, language = 'en-EN')
            return speech.lower()
    except:
        None
    #replace listen() with the wake up listen function()

def listen2():
    try:
        r = sr.Recognizer()
        with sr.Microphone() as s:
            r.adjust_for_ambient_noise(s)
            audio = r.listen(s)
            speech = r.recognize_google(audio, language = 'en-EN')
            chat_with_voice(speech)
            return speech.lower()
    except:
        None


def speech_to_text():

    print("Some functions, such as voice mode, may not work without internet.")
    print("Welcome, user. I am Lambda. How can I help?")

    while True:
        initial_input = input("Input: ")
        if initial_input.lower() == "":
            listen()
        else:
            print("Text mode activated.")
            chat_without_voice()



wakephrase = "hey george"

#Idea
'''something like if for a certain amount of time the mic doesn't receive info, program goes to sleep and
can wake up again?'''

while True:
    text = listen()
    try:
        if text.count(wakephrase) > 0:
            print("Ready!")
            text = listen2()
    except:
        print("Please make sure you are connected to the internet.")

#speech_to_text() //Overrides wake phrases. 
