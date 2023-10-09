import speech_recognition as sr
import wikipedia as wp
import requests
from bs4 import BeautifulSoup 

r = sr.Recognizer()


def search(wiki_link):
    resp = requests.get(wiki_link)
    
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text,features="html.parser")

        body_container = soup.find("div", attrs={'id': 'mw-content-text'})        
        body = body_container.find("div", attrs={'class': 'mw-parser-output'})        #return the main div object

        for p in body.find_all("p"):
            print(p.get_text())

    else:
        print("Error in finding the webpage")


with sr.Microphone() as source:
    print("Speak Anything:")
    r.adjust_for_ambient_noise(source, duration=1)
    audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print(f"Searching for: {text}")

        page = wp.page(text)                                              #Returns the web page as an object
        wikipedia_link = f'https://en.wikipedia.org/wiki/{page.title}'    #page link
        search(wikipedia_link)

    except:
        print("Could not recognize your voice")