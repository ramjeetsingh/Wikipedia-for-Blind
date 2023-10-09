import speech_recognition as sr

r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak Anything:")
    r.adjust_for_ambient_noise(source, duration=1)
    audio = r.listen(source)

    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Could not recognize your voice")
    except sr.RequestError:
        print("hbefjnek")