import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pyjokes
import webbrowser
import urllib.parse
import sys
import time

from typing import cast



# Initialize the recognizer and TTS engine
listener = sr.Recognizer()
engine = pyttsx3.init()

# Set the voice to female if available, else use default
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

def engine_talk(text):
    """Make Alexa speak and print debug message."""
    print(f"Alexa: {text}")
    engine.say(text)
    engine.runAndWait()

def user_commands():
    """Capture voice command from the microphone."""
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=2)
            print("\nListening...")
            voice = listener.listen(source)

            # Use getattr to avoid Pylance warning
            recognize_func = getattr(listener, "recognize_google", None)
            if callable(recognize_func):
                command = cast(str, recognize_func(voice)).lower()

            else:
                print("recognize_google method not found.")
                return ""

            if 'alexa' in command:
                command = command.replace('alexa', '').strip()
                print(f"User Command: {command}")
                return command
            else:
                return ""
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError:
        print("Network/API unavailable")
        return ""
    except Exception as e:
        print(f"Error: {e}")
        return ""

# --- Command Handlers ---

def play_song(song):
    """Open YouTube search for the song."""
    query = urllib.parse.quote(song)
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)

def handle_play(command):
    song = command.replace('play', '').strip()
    engine_talk(f'Playing {song}')
    play_song(song)

def handle_time(_):
    time_now = datetime.datetime.now().strftime('%I:%M %p')
    engine_talk(f'The current time is {time_now}')

def handle_who_is(command):
    person = command.replace('who is', '').strip()
    try:
        info = wikipedia.summary(person, sentences=1)
        print(info)
        engine_talk(info)
    except wikipedia.exceptions.DisambiguationError:
        engine_talk("Multiple matches found. Please be more specific.")
    except wikipedia.exceptions.PageError:
        engine_talk(f"I couldn't find any information about {person}.")

def handle_joke(_):
    engine_talk(pyjokes.get_joke())

def handle_stop(_):
    engine_talk("Goodbye!")
    sys.exit()

# --- Command Router ---
command_map = {
    'play': handle_play,
    'time': handle_time,
    'who is': handle_who_is,
    'joke': handle_joke,
    'stop': handle_stop
}

def run_alexa():
    """Process the command and perform actions."""
    command = user_commands()
    if command:
        for key in command_map:
            if key in command:
                command_map[key](command)
                return
        engine_talk('I did not catch that. Please speak again.')
    else:
        engine_talk('I did not catch that. Please speak again.')

# --- Main Loop ---
if __name__ == "__main__":
    engine_talk("Hello, I am Alexa. How can I help you?")
    time.sleep(1)
    while True:
        run_alexa()