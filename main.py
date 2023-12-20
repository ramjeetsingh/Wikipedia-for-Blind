import speech_recognition as sr
import wikipedia as wp
import requests
from bs4 import BeautifulSoup
import pyttsx3
import keyboard
import time

engine = pyttsx3.init()
r = sr.Recognizer()



def outputImg(element):
    caption = (element.find("figcaption"))
    return outputP(caption)



def CheckSubEle(element):
    SubEle = element.find_all(recursive=False)

    if SubEle:
        if len(SubEle) == 1 and SubEle[0].name == 'span' and SubEle[0].get_text() == ' ':
            return False
        else:
            return True
    else:
        return False

def outputP(para):
    allText = para.get_text()

    plain_texts = [element for element in para.find_all(string=True, recursive=False) if element.strip()]

    elements = []
    
    for e in para.find_all():
        if e.name != "style" and (not CheckSubEle(e)):
            if e.name == 'span':
                if e.get_text() != ' ':
                    elements.append(e)
            else:
                elements.append(e)


    while (len(plain_texts) > 0 and len(elements) > 0):
        pt = plain_texts[0]
        e = elements[0].get_text()

        if (allText[0:len(pt)] == pt):
            engine.setProperty('volume', 1.0)
            engine.say(pt)
            engine.runAndWait()
            plain_texts.pop(0)
            allText = allText[len(pt):]
        else:
            if allText[0] == ' ':
                allText = allText[1:]
                                                                                                                                        

            if elements[0].name == 'a':
                engine.setProperty('volume', 0.6)
            else:
                engine.setProperty('volume', 1)
            engine.say(e)
            engine.runAndWait()

            if elements[0].name == 'a':
                if keyboard.read_key() == 'enter':
                    search(e)
                elif keyboard.read_key() == 'backspace':
                    return True

            elements.pop(0)
            allText = allText[len(e):]  

    

    while (len(plain_texts)>0):
        pt = plain_texts[0]
        engine.setProperty('volume', 1)
        engine.say(pt)
        engine.runAndWait()
        plain_texts.pop(0)
        allText = allText[len(pt):]


    while (len(elements)>0):
        if allText[0] == ' ':
            allText = allText[1:]

        e = elements[0]
        if elements[0].name == 'a':
            engine.setProperty('volume', 0.6)
        else:
            engine.setProperty('volume', 1)
        engine.say(e)
        engine.runAndWait()

        if elements[0].name == 'a':
            if keyboard.read_key() == 'enter':
                search(e)
            elif keyboard.read_key() == 'backspace':
                return True

        elements.pop(0)
        allText = allText[len(e):]
    
    return False


def output(body):
    end = False
    engine.setProperty('rate', 200)        
    engine.setProperty('volume', 1.0)    

    for tag in body.find_all(recursive=False):
        if end:
            return
        else:
            if tag.name == 'p':
                end = outputP(tag)
            elif tag.name == 'figure':
                end = outputImg(tag)

            # if tag.name == 'figure':
            #     outputImg(tag)


def search(text):
    try:
        page = wp.page(text, auto_suggest=False)

        if page:
            wiki_link = f'https://en.wikipedia.org/wiki/{page.title}'
            print(f'Wikipedia link for "{text}": {wiki_link}')
        else:
            print(f'Page for "{text}" does not exist on Wikipedia.')

        resp = requests.get(wiki_link)
        
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, features="lxml")
            
            body_container = soup.find("div", attrs={'id': 'mw-content-text'})        
            body = body_container.find("div", attrs={'class': 'mw-parser-output'})       

            print(f"Returing audio output for {wiki_link}")
            output(body)

        else:
            print("Error in finding the webpage")
    except:
        print("Error in finding the webpage")


with sr.Microphone() as source:
    print("Speak Anything:")
    r.adjust_for_ambient_noise(source, duration=1)
    audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print(f"Searching for: {text}")

        search(text)

    except:
        print("Could not recognize your voice")