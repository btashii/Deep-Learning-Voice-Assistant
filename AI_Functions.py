import wikipedia
import geocoder
import os
import wolframalpha
from __future__ import print_function
from datetime import datetime
from requests import get
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from gnews import GNews
from googletrans import Translator



'''

Name: Brandon
Project Name: LAMBDA
File Description: Stores additional functions that the AI can utilize in the mainframe.
Notes: All functions written must have one variable to pass values through, or else the AI_Core will not execute them.
Last Date Modified: 7/13/2021

'''

## Function Set Up

## Set up for IBM Watson TTS (10,000 characters per month!) (Update 7/16/2021: $0.02 per 1000 words translated)
apikey = 'yourKey' #remember to get rid of APIkey when uploading to GitHUB
url = 'yourURL'
authenticator = IAMAuthenticator(apikey)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url)

## Grabs IP & Latitude and Longitude
try:
    ip = get('https://api.ipify.org').text
    g = geocoder.ip(ip)
except:
    None

## Voice Synthesizer
def TTS(phrase):
    with open('speech.wav', 'wb') as audio_file:
        res = tts.synthesize(phrase, accept='audio/wav', voice='en-US_AllisonV3Voice').get_result()
        audio_file.write(res.content)
    try:
        os.system("python AI_AudioAnalyze.py")
    except:
        print("Audio visualization failed; is the audio visualizer launched?")

    os.remove("speech.wav")
        #Playsound and os.remove() hashed out as it is already done in shape.py

## Work in progress translator

'''def translatorTTS(phrase, voice):
    with open('speech.wav', 'wb') as audio_file:
        res = tts.synthesize(phrase, accept='audio/wav', voice=voice).get_result()
        audio_file.write(res.content)
    try:
        os.system("python AI_AudioAnalyze.py")
    except:
        print("Audio visualization failed; is the audio visualizer launched?")

    os.remove("speech.wav")'''

## IP Address

def IP(phrase):
    print("Your IP Address is: " + aiFunc.ip)
    TTS("Your IP Address is: " + aiFunc.ip)

## Wikipedia Search
def wikipediaSearch(phrase):
    query = phrase
    stopwords = ['wikipedia']
    querywords = query.split()

    resultwords  = [word for word in querywords if word.lower() not in stopwords]
    result = ' '.join(resultwords)
    print(result)
    #how many sentences the wikipedia entry should have?
    sentences = 3
    try:
        print(wikipedia.summary(result, 3))
        TTS(wikipedia.summary(result, 3))
    except:
        print("Sorry, I couldn't find your answer in the wikipedia database.")

## Check time
def time(phrase):
    now = datetime.now()
    currentTime = now.strftime("%H:%M")
    print("The current time is " + currentTime + ".")
    TTS("The current time is " + currentTime + ".")

## Check time of day
def timeGreet(phrase):
    timeStatus = None
    currentTime = datetime.now()
    if currentTime.hour < 12:
        TTS("Good morning!")
        timeStatus = "morning"
    elif 12 <= currentTime.hour < 18:
        TTS("Good afternoon!")
        timeStatus = "afternoon"
    else:
        TTS("Good evening!")
        timeStatus = "evening"
    return timeStatus

## Time Reminder (does not work, needs a thread)
def timeReminder(phrase):
    TTS("Got it!")
    while True:
        now = datetime.now()
        currentTime = now.strftime("%M")
        if int(currentTime) == 0:
            print("The time is: " + now.strftime("%H:%M"))
            aifunc.TTS("The time is: " + now.strftime("%H:%M"))
            aifunc.time()
            time.sleep(3590)

## IP based weather
def weather(phrase):
    api_key = "yourKey"
    base_url = "yourURL"
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

## Google Calender API

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def googleCalendar(phrase):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    TTS("Here are your upcoming events.")
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=5, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        TTS('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        TTS(event['summary'] + "at" + start)

## News (work on getting through this data)
def news(phrase):
    news = GNews()
    google_news = GNews()
    json_resp = google_news.get_news(phrase)
    print("Here's some news about your topic.")
    TTS("Here's some news about your topic.")
    for x in range(3):
            jsonStructure = json_resp[x]
            print(str(x) + ": " + jsonStructure["title"])
            TTS(str(x) + ": " + jsonStructure["title"])

## Language translator (WIP)
'''def googleTranslate(phrase):
    trans = Translator()
    t = trans.translate(phase, src = "en", dest = languageDestination)
    if languageDestination == "es":
        translatorTTS(t.phrase, "es-LA_SofiaV3Voice")
    elif languageDestination == "pt":
        translatorTTS(t.phrase, "pt-BR_IsabelaV3Voice")
    elif languageDestination == "ja":
        translatorTTS(t.phrase, "ja-JP_EmiV3Voice")
    elif languageDestination == "ko":
        translatorTTS(t.phrase, "ko-KR_HyunjunVoice")
    elif languageDestination == "it":
        translatorTTS(t.phrase, "it-IT_FrancescaV3Voice")
    elif languageDestination == "fr":
        translatorTTS(t.phrase, "fr-FR_ReneeV3Voice")
    elif languageDestination == "de":
        translatorTTS(t.phrase, "de-DE_ErikaV3Voice")
    elif languageDestination == "nl":
        translatorTTS(t.phrase, "nl-NL_EmmaVoice")'''

## Calculator
def calculator(phrase):
    # write your wolframalpha app_id here
        app_id = "yourAppID"
        client = wolframalpha.Client(app_id)
        res = client.query(phrase)
        answer = next(res.results).text
        print("The answer is: " + answer)
        TTS("The answer is " + answer)
