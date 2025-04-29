import warnings
import pyttsx3
import speech_recognition as sr
import datetime
import os
import random
import requests
import webbrowser
import pywhatkit as kit
import sys
import pyjokes

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

# API Key for OpenWeatherMap
WEATHER_API_KEY = "your_weather_API_key" #replace weather Api key

# Set the wake word
WAKE_WORD = "nova"

# Initialize the speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't understand that.")
        return None
    except sr.RequestError:
        print("Could not request results. Please check your connection.")
        return None

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            return f"The current temperature in {city} is {temperature}°C with {description}."
        elif response.status_code == 404:
            return "City not found. Please check the city name and try again."
        else:
            return f"Error: Unable to fetch weather details (status code {response.status_code})."
    except requests.exceptions.RequestException as e:
        return f"Network error: {e}"

def system_control(command):
    if "shutdown" in command:
        speak("Shutting down the system.")
        os.system("shutdown /s /t 1")
    elif "restart" in command:
        speak("Restarting the system.")
        os.system("shutdown /r /t 1")
    elif "open notepad" in command:
        speak("Opening Notepad.")
        os.system("notepad")
    elif "open chrome" in command:
        speak("Opening Chrome.")
        os.system("start chrome")
    elif "close chrome" in command:
        speak("Closing Chrome.")
        os.system("taskkill /im chrome.exe /f")

def process_command(command):
    if any(word in command for word in ["weather", "temperature", "date", "time", "open", "close", "shutdown", "restart", "joke", "music", "song", "search", "exit"]):
        return "command"
    else:
        return "chat"

def handle_chat(command):
    responses = {
        "how are you": ["I'm doing well, thank you!", "I'm great, how about you?", "I'm fine, how can I assist you today?"],
        "what is your name": ["Hi! I am nova, your voice assistant.", "You can call me Nova.", "I don't have a name, but I’m here to help!"],
        "hello": ["Hello!", "Hi there!", "Hey, how can I help you today?"],
        "bye": ["Goodbye!", "See you later!", "Take care!"]
    }
    for question, answer_list in responses.items():
        if question in command:
            return random.choice(answer_list)
    return "I'm here to chat! Feel free to ask me anything."

def handle_command(command):
    if "weather" in command or "temperature" in command:
        if "in" in command:
            city = command.split("in")[-1].strip()
        else:
            speak("Please specify the city.")
            city = listen()
        weather_info = get_weather(city)
        speak(weather_info)
        return

    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The current time is {current_time}")

    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%A, %d %B %Y")
        speak(f"Today's date is {current_date}")

    elif "play" in command:
        speak("What song would you like to hear?")
        song = listen()
        if song:
            kit.playonyt(song)
            speak(f"Playing {song} on YouTube.")

    elif "joke" in command:
        joke = pyjokes.get_joke()
        speak(joke)

    elif "search" in command:
        speak("What would you like me to search for?")
        query = listen()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            speak(f"Searching for {query} on Google.")

    elif "exit" in command:
        speak("Goodbye!")
        return True

    elif "shutdown" in command or "restart" in command or "open" in command or "close" in command:
        system_control(command)

    else:
        speak("Command not recognized. Please try again.")
    return False

def greet_user():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        return "Good morning!"
    elif 12 <= hour < 17:
        return "Good afternoon!"
    else:
        return "Good evening!"

def main():
    speak("Initializing assistant...")
    speak(f"{greet_user()} I am your Assistant.")
    while True:
        command = listen()
        if command:
            if WAKE_WORD in command:
                command = command.replace(WAKE_WORD, "").strip()
                command_type = process_command(command)
                if command_type == "command":
                    if handle_command(command):
                        break
                else:
                    response = handle_chat(command)
                    speak(response)
        else:
            print("No wake word detected. Waiting...")

if __name__ == "__main__":
    main()
