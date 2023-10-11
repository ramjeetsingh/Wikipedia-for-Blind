import speech_recognition as sr
import wikipedia as wp
import requests
from bs4 import BeautifulSoup
import pyttsx3


r = sr.Recognizer()

def CheckSubEle(element):
    SubEle = element.find_all(recursive=False)

    if SubEle:
        return True
    else:
        return False



def output(body):
    engine = pyttsx3.init()
    engine.setProperty('rate', 250)         # Speed of speech (words per minute)
    engine.setProperty('volume', 1.0)       # Volume (0.0 to 1.0)

    for para in body.find_all('p'):
        first_child = para.contents[0] if para.contents else None

        plain_texts = [element for element in para.find_all(string=True, recursive=False) if element.strip()]

        elements = []
        
        for e in para.find_all():
            if e.name != "style" and (not CheckSubEle(e)):
                if e.name == 'span':
                    if e.get_text() != ' ':
                        elements.append(e)
                else:
                    elements.append(e)

        # if first_child.name is None:
        #     print("plaintext")
        # else:
        #     print(first_child.name) 
        # print(plain_texts)
        # print()
        # print(elements)
        # print()
        # print()
        # print()

        
        if first_child.name is None:            #para starts with a plain text
            i = 0
            while (len(plain_texts) > 0 or len(elements) > 0):
                if (i%2 == 0):                  #do plain text
                    print(plain_texts[0])

                    engine.setProperty('volume', 1.0)
                    engine.say(plain_texts[0])
                    engine.runAndWait()
                    plain_texts.pop(0)
                    i += 1
                else:                           #do elements
                    print(elements[0].get_text())

                    if elements[0].name == 'a':
                        engine.setProperty('volume', 0.4)
                    engine.say(elements[0].get_text())
                    engine.runAndWait()
                    elements.pop(0)
                    i += 1

        else:                                  #para starts with an element
            i = 0
            while (len(plain_texts) > 0 or len(elements) > 0):
                if (i%2 == 0):                  #do elements
                    print(elements[0].get_text())

                    if elements[0].name == 'a':
                        engine.setProperty('volume', 0.4)
                    engine.say(elements[0].get_text())
                    engine.runAndWait()
                    elements.pop(0)
                    i += 1
                else:                           #do plain text
                    print(plain_texts[0])

                    engine.setProperty('volume', 1.0)
                    engine.say(plain_texts[0])
                    engine.runAndWait()
                    plain_texts.pop(0)
                    i += 1


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


#some anchor tags webpage mein saath saath hote hai, but pane algo ke output mein unke beech mein koi plain text add ho jata hai