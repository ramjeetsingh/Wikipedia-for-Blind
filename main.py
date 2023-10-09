import speech_recognition as sr
import wikipedia as wp
import requests
from bs4 import BeautifulSoup 
import pyttsx3


r = sr.Recognizer()


def output(body):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)         # Speed of speech (words per minute)
    engine.setProperty('volume', 1.0)       # Volume (0.0 to 1.0)

    for p in body.find_all("p"):
        print(p.get_text())
        engine.say(p.get_text())
        engine.runAndWait()


def search(wiki_link):
    resp = requests.get(wiki_link)
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, features="lxml")

        body_container = soup.find("div", attrs={'id': 'mw-content-text'})        
        body = body_container.find("div", attrs={'class': 'mw-parser-output'})        #return the main div object

        output(body)

    else:
        print("Error in finding the webpage")


with sr.Microphone() as source:
    print("Speak Anything:")
    r.adjust_for_ambient_noise(source, duration=1)
    audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print(f"Searching for: {text}")

        page = wp.page(text)

        if page:
            wikipedia_link = f'https://en.wikipedia.org/wiki/{page.title}'
            print(f'Wikipedia link for "{text}": {wikipedia_link}')
            search(wikipedia_link)
        else:
            print(f'Page for "{text}" does not exist on Wikipedia.')

    except:
        print("Could not recognize your voice")