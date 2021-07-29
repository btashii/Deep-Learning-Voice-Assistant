#!/usr/bin/python
# -*- coding: utf-8 -*-
# Core Libs

import nltk
import numpy
import tflearn
import tensorflow
import random
import json
import pickle
import sys
import speech_recognition as sr
import nltk
import AI_Functions as aiFunc
from nltk.stem.lancaster import LancasterStemmer
from requests import get
from playsound import playsound
from threading import Thread
from datetime import datetime


# All Initial Setups for Libraries

# LancasterStemmer

stemmer = LancasterStemmer()

# Permission for JSON file

with open('neuralnetworktrainingdata.json') as file:
    data = json.load(file)

# Initial Setup Ends Here

# Start of Neural Network

try:
    print('Initializing Neural Network...')
    with open('data.pickle', 'rb') as f:
        (words, labels, training, output) = pickle.load(f)
except:
    print('Training Neural Network...')
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent['tag'])

        if intent['tag'] not in labels:
            labels.append(intent['tag'])

            # stem the words first

    words = [stemmer.stem(w.lower()) for w in words if w != '?']
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    # create an array of 0's for the range of total stemmed words

    out_empty = [0 for _ in range(len(labels))]

    for (x, doc) in enumerate(docs_x):

        # bag is a vector

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

tensorflow.compat.v1.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 60)
net = tflearn.fully_connected(net, 60)
net = tflearn.fully_connected(net, 60)
net = tflearn.fully_connected(net, len(output[0]), activation='softmax')
net = tflearn.regression(net)

model = tflearn.DNN(net)

''' Enable "model.load" for instant boot '''
# try:
    # model.load("model.tflearn")
# except:

model.fit(training, output, n_epoch=550, batch_size = 60, show_metric=True)
model.save('model.tflearn')


def bag_of_words(s, words):

    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for (i, w) in enumerate(words):
            if w == se:
                bag[i] = 1
    return numpy.array(bag)


# for stuff inside intent, if tag no exist, then append new JSON structure + new tag into intent array in JSON file

template_json = {
    'tag': None,
    'patterns': [],
    'responses': [],
    'context_set': '',
    }


##AI Listening Functions
# Function to chat without voice

def chat_without_voice():

    while True:
        inp = input('Input: ')
        if inp.lower() == 'quit':
            print("You've exited voice mode.")
            break
        results = model.predict([bag_of_words(inp, words)]).squeeze()
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        # last left off on finding a solution to an indexing problem of results[results_index]
        # the solution to literally all of this: results = model.predict([bag_of_words(inp, words)]).squeeze() . The squeeze removes an extra empty dimension in the numpy array, which is the cause for the out of bounds error

        if results[results_index] > 0.7:
            for tg in data['intents']:
                if tg['tag'] == tag:
                    responses = tg['responses']
                    #TTS(random.choice(responses))
                    print("Lambda: " + random.choice(responses))
            if tag == 'query':
                query_input = input('Query: ')
                search(query_input)
            if tag == 'time':
                aiFunc.time()
            if tag == 'commandWeather':
                try:
                    aiFunc.weather()
                except:
                    print("I couldn't retrieve the weather.")
            if tag == 'shutdown':
                print("Shutting down...")
                sys.exit()
        else:
            inp2 = \
                input("I'm sorry, I don't understand. What would I classify your response as? [Example: 'Sarcasm'] (Type Exit to leave): "
                      )
            if inp2.lower() == 'exit':
                break
            with open('tempintents.json') as file2:
                data2 = json.load(file2)
                for someintent in data2['intents']:
                    if inp2.lower() == someintent['tag']:
                        print('Tag ' + inp2 + ' already exists!')
                        break
                    else:
                        print('Tag registered.')
                        template_json['tag'] = str(inp2)
                        template_json['patterns'].append(inp)
                        config2 = json.loads(open('tempintents.json'
                                ).read())
                        config2['intents'].append(template_json)
                        with open('tempintents.json', 'w') as f:
                            f.write(json.dumps(config2))
                            template_json['tag'] = None
                            template_json['patterns'] = [None]
                            break


commands = {
  'wikipediaSearch' : aiFunc.wikipedia,
  'time' : aiFunc.time,
  'enableTimeRemind' : aiFunc.timeReminder,
  'commandWeather': aiFunc.weather,
  'calendar': aiFunc.googleCalendar,
  'calculator' : aiFunc.calculator,
  'news' : aiFunc.news,
  'IP' : aiFunc.IP,
  'exit': None,
  }


def chat_with_voice(speech):

    inp = speech

        # print("Input: " + speech)

    results = model.predict([bag_of_words(inp, words)]).squeeze()
    results_index = numpy.argmax(results)
    tag = labels[results_index]

        # last left off on finding a solution to an indexing problem of results[results_index]
        # the solution to literally all of this: results = model.predict([bag_of_words(inp, words)]).squeeze() . The squeeze removes an extra empty dimension in the numpy array, which is the cause for the out of bounds error

    if results[results_index] > 0.7:
        for tg in data['intents']:
            tg['tag'] == tag
            if tag in commands:
              commands[tag](speech)
              break
            else:
                responses = tg['responses']
                print(random.choice(responses))
                aiFunc.TTS(random.choice(responses))
                break

    else:

        print("I'm sorry, could you please repeat that?")
        aiFunc.TTS("I'm sorry, could you please repeat that?")


def primaryListen():

    try:
        with sr.Microphone() as source:
            r = sr.Recognizer()
            r.pause_threshold = 0.5
            audio = r.listen(source, timeout=1, phrase_time_limit=1)
            speech = r.recognize_google(audio, language='en-US')
            return speech.lower()
    except:
        None

def secondaryListen():

    try:
        with sr.Microphone() as source:
            r = sr.Recognizer()
            playsound('promptopen.mp3')
            audio = r.listen(source, timeout=10, phrase_time_limit=3)
            speech = r.recognize_google(audio, language='en-US')
            print('Input: ' + speech)
            parsedPhrases = speech.split(" and ")
            print(parsedPhrases)
            for phrase in parsedPhrases:
                chat_with_voice(phrase)
            return speech.lower()
    except:
        playsound('promptclose.mp3')

#Used for asking again when executing additional AI functions
def universalListen():
    try:
        with sr.Microphone() as source:
            r = sr.Recognizer()
            playsound('promptopen.mp3')
            audio = r.listen(source, timeout=10, phrase_time_limit=3)
            speech = r.recognize_google(audio, language='en-US')
            print('Input: ' + speech)
            return speech.lower()
    except:
        playsound('promptclose.mp3')
        return None


def speech_to_text():
    while True:
        initialInput = input('Input: ')
        if initialInput.lower() == '':
            listen()
        else:
            print('Text mode activated.')
            chat_without_voice()


# Wakephrases for the AI; should be all lowercase
wakephrases = ['hello', 'hey', 'yo', 'hi', 'you there']

# Initialize Speech Recognition
aiFunc.timeGreet(x)
print('Say "Hello" or "Hey" to wake me up.')

def bootup():
    while True:
        text = primaryListen()
        try:
            for phrase in wakephrases:
                if text.count(phrase) > 0 :
                    text = secondaryListen()
        except:
            pass

# Enable speech_to_text() for the voice to text
# speech_to_text()
bootup()
