import speech_recognition as sr
import wikipedia as wp
import requests
from bs4 import BeautifulSoup
import pyttsx3
import keyboard
import spacy

nlp = spacy.load(r'C:\en_core_web_md-3.7.1\en_core_web_md\en_core_web_md-3.7.1')
nlp.max_length = 1500000

engine = pyttsx3.init()
r = sr.Recognizer()



def get_content(l):
    resp = requests.get(l)
    soup = BeautifulSoup(resp.text, features="lxml")      
    body_container = soup.find("div", attrs={'id': 'mw-content-text'})        
    body = body_container.find("div", attrs={'class': 'mw-parser-output'})

    return body.get_text()




def find_similarity(page1, link_topic):
    page1 = nlp(page1[:min(len(page1), 10000)])

    page = wp.page(link_topic, auto_suggest=False)
    wiki_link = f'https://en.wikipedia.org/wiki/{page.title}'
    page2 = (get_content(wiki_link))
    page2 = nlp(page2[:min(len(page2), 10000)])

    return page1.similarity(page2)




def outputTable(element):
    caption = element.find("caption")
    caption_text = caption.get_text()

    engine.say("Here are the contents of a table describing" + caption_text)
    engine.runAndWait()

    body = element.find("tbody")
    for row in body.find_all(recursive=False):
        style_attribute = row.get('style', '')
        if 'display: none' in style_attribute or 'display:none' in style_attribute:
            continue

        print(row.get_text())

        onlyHeadings = True
        headingCount = 0
        for content in row.find_all(recursive = False):
            if content.name != "th":
                onlyHeadings = False
                break
            else:
                headingCount += 1

        iter = 0 
        print(onlyHeadings, headingCount)
        for content in row.find_all(recursive = False):
            if onlyHeadings:
                if headingCount == 1:
                    engine.say(content.get_text() + " is the section heading")
                    engine.runAndWait()

                else:
                    if iter == 0:
                        engine.say("Following are the column headings")
                        engine.runAndWait()
                    engine.say(content.get_text())
                    engine.runAndWait()
                    iter += 1

            else:
                if (content.name == "td") and ("infobox-image" in content.get("class", [])):
                    if content.find("div", attrs={'class': 'infobox-caption'}):
                        cap = content.find("div", attrs={'class': 'infobox-caption'})
                        engine.say("An image with the caption" + cap.get_text())
                        engine.runAndWait()
                elif (content.name == "td" and ("infobox-data" in content.get("class", []) or not content.get('class'))) or content.name == "th":
                    data = content.get_text()
                    engine.say(data)
                    engine.runAndWait()




def outputImg(element, body):
    caption = (element.find("figcaption"))
    engine.say("An image with the caption ")
    engine.runAndWait()
    return outputP(caption, body)




def CheckSubEle(element):
    SubEle = element.find_all(recursive=False)

    if SubEle:
        if len(SubEle) == 1 and SubEle[0].name == 'span' and SubEle[0].get_text() == ' ':
            return False
        else:
            return True
    else:
        return False




def outputP(para, body):
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
                                                                                                                                        
            if 'reference' not in elements[0].parent.get('class', []):
                if elements[0].name == 'a':
                    engine.setProperty('volume', 0.6)
                else:
                    engine.setProperty('volume', 1)
                engine.say(e)
                engine.runAndWait()
                print(elements[0])

                if elements[0].name == 'a' and find_similarity(body.get_text(), e) >= 0.9:
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

        if 'reference' not in elements[0].parent.get('class', []):
            if elements[0].name == 'a':
                engine.setProperty('volume', 0.6)
            else:
                engine.setProperty('volume', 1)
            engine.say(e)
            engine.runAndWait()
            print(elements[0])

            if elements[0].name == 'a' and find_similarity(body.get_text(), e) >= 0.9:
                if keyboard.read_key() == 'enter':
                    search(e)
                elif keyboard.read_key() == 'backspace':
                    return True

        elements.pop(0)
        allText = allText[len(e):]
    
    return False




def output(body):
    end = False
    engine.setProperty('rate', 300)        
    engine.setProperty('volume', 1.0)    

    for tag in body.find_all(recursive=False):
        if end:
            return
        else:
            if tag.name == 'p':
                end = outputP(tag, body)
            elif tag.name == 'figure':
                end = outputImg(tag, body)
            elif tag.name == 'table':
                outputTable(tag)




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