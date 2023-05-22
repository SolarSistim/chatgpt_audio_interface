import speech_recognition as sr
import os
import openai
import requests
import pyttsx3
import time
import pygame
import sys
import threading

openai.api_key = '<OPENAI API KEY HERE>'

engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

pygame.mixer.init()
start_processing_sound = "start_processing.mp3"
stop_processing_sound = "stop_processing.mp3"
ready_sound = "ready.mp3"
complete_sound = "complete.mp3"

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

def main():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source)
        play_audio(ready_sound)
        print("ChatGPT: Listening...")
        while True:
            try:
                audio = r.listen(source)
                text = 'In two or fewer sentences ' + r.recognize_google(audio)
                if text == 'In two or fewer sentences break' or text == 'In two or fewer sentences Break':
                    exit()
                else:
                    string_text = text.replace('In two or fewer sentences ', '')
                    string_text = 'User: ' + string_text
                    # Print user's question
                    for char in string_text:
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        time.sleep(.02)
                    play_audio(start_processing_sound)
                    print('\nChatGPT: Thinking...')
                    completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": text}
                        ]
                    )
                    print('ChatGPT: Speaking')

                    # Start a new thread to play ChatGPT audio
                    audio_thread = threading.Thread(target=play_audio, args=(complete_sound,))
                    audio_thread.start()

                    # Type ChatGPT response on screen
                    string_completion = str(completion.choices[0].message.content)
                    for char in string_completion:
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        time.sleep(.005)

                    # Wait for the audio thread to finish
                    audio_thread.join()

                    # Say ChatGPT response
                    engine.say(completion.choices[0].message.content)
                    engine.runAndWait()

                    play_audio(stop_processing_sound)

                    print('\nChatGPT: Ready for input')
            except sr.UnknownValueError:
                print("Still listening...")
                main()
            except sr.RequestError as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
