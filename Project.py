import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import pyaudio
import sys
import yt_dlp
from textblob import TextBlob
import threading
import os
import pygame

listener = sr.Recognizer()
engine = pyttsx3.init()

voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

engine_lock = threading.Lock()

def engine_talk(text):
    with engine_lock:
        print(f"Tony is saying: {text}")
        engine.say(text)
        engine.runAndWait()

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "happy"
    elif sentiment < 0:
        return "sad"
    else:
        return "neutral"

def user_command():
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source)
            print("Start Speaking !!")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if "tony" in command:
                command = command.replace('tony', '')
                print(f"User Said: {command}")
                return command.strip()
    except Exception as e:
        print(f"Error: {e}")
        return ""

def search_and_recommend(song):
    engine_talk(f"Searching for {song} on YouTube")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch10:{song}", download=False)['entries']
            recommendations = [f"{i+1}. {entry['title']}" for i, entry in enumerate(search_results[:5])]
            return recommendations, search_results
    except Exception as e:
        engine_talk(f"Sorry, I couldn't find recommendations. Error: {e}")
        return [], []

def show_recommendations_from_desktop(directory):
    try:
        if not os.path.exists(directory):
            engine_talk(f"The directory {directory} does not exist.")
            return

        songs = [f for f in os.listdir(directory) if f.endswith('.mp3')]
        if not songs:
            engine_talk("No songs found in the directory.")
            return

        engine_talk("Here are the songs available in the desktop directory:")
        for i, song in enumerate(songs, 1):
            engine_talk(f"{i}. {song}")

        engine_talk("Please say the song number to play it.")
        selected_song = user_command()
        if selected_song and selected_song.startswith("song number"):
            try:
                song_number = int(selected_song.replace("song number", "").strip())
                if 1 <= song_number <= len(songs):
                    song_to_play = os.path.join(directory, songs[song_number - 1])
                    play_song_from_desktop(song_to_play)
                else:
                    engine_talk(f"Invalid selection. Please say a number between 1 and {len(songs)}.")
            except ValueError:
                engine_talk("Please say the song number correctly.")
        else:
            engine_talk("I didn't catch that. Please say 'Tony song number' followed by the number.")
    except Exception as e:
        engine_talk(f"An error occurred while accessing the directory. Error: {e}")
        print(f"Exception: {e}")

def play_song_from_desktop(file_path):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        engine_talk(f"Failed to play the song. Error: {e}")
        print(f"Exception: {e}")

def download_song(song):
    try:
        engine_talk(f"Searching for {song} on YouTube")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': r'C:\Users\usha v\OneDrive\Desktop\downloaded songs\%(title)s.%(ext)s',  # Save to specified directory
            'ffmpeg_location': r'C:\Program Files\ffmpeg',  # Specify the path to ffmpeg (only needed if not in PATH)
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{song}", download=True)
            video_title = info_dict['entries'][0]['title']
        engine_talk(f"Downloaded {video_title} and saved it to your desktop directory.")
    except yt_dlp.utils.DownloadError as de:
        engine_talk(f"Failed to download the song. Check your internet connection or the song's availability.")
        print(f"DownloadError: {de}")
    except Exception as e:
        engine_talk(f"An error occurred while downloading the song. Error: {e}")
        print(f"Exception: {e}")

def stop_tony():
    engine_talk("Time's up. Stopping now.")
    sys.exit()

def run_tony():
    command = user_command()
    if command:
        emotion = analyze_sentiment(command)
        engine_talk(f"Detected sentiment: {emotion}")

        if 'recommendation' in command and 'desktop' in command:
            show_recommendations_from_desktop(r"C:\Users\usha v\OneDrive\Desktop\downloaded songs")
        elif 'play' in command and 'desktop' in command:
            song = command.replace('play songs from the desktop', '').strip()
            show_recommendations_from_desktop(r"C:\Users\usha v\OneDrive\Desktop\downloaded songs")
        elif 'recommendation' in command:
            song = command.replace('show recommendation on', '').strip()
            recommendations, search_results = search_and_recommend(song)
            if recommendations:
                engine_talk(f"I found these songs for {song}. Please say 'Tony song number' followed by the number to select a song.")
                for recommendation in recommendations:
                    engine_talk(recommendation)

                selected_song = user_command()
                if selected_song and selected_song.startswith("song number"):
                    try:
                        song_number = int(selected_song.replace("song number", "").strip())
                        if 1 <= song_number <= len(recommendations):
                            engine_talk(f"Playing {search_results[song_number - 1]['title']}")
                            pywhatkit.playonyt(search_results[song_number - 1]['webpage_url'])
                        else:
                            engine_talk(f"Invalid selection. Please say a number between 1 and {len(recommendations)}.")
                    except ValueError:
                        engine_talk("Please say the song number correctly.")
                else:
                    engine_talk("I didn't catch that. Please say 'Tony song number' followed by the number.")
        elif 'play' in command:
            song = command.replace('play', '').strip()
            engine_talk('playing ' + song)
            pywhatkit.playonyt(song)
        elif 'time' in command:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            engine_talk('The current time is ' + current_time)
        elif 'who is' in command:
            name = command.replace('who is', '').strip()
            info = wikipedia.summary(name, 1)
            print(info)
            engine_talk(info)
        elif 'joke' in command:
            engine_talk(pyjokes.get_joke())
        elif 'download' in command:
            song = command.replace('download', '').strip()
            download_song(song)
        elif 'stop' in command:
            stop_tony()
        else:
            engine_talk('I could not hear you properly')
    else:
        engine_talk('I did not catch that, please speak again')

timer = threading.Timer(10, stop_tony)
timer.start()

while True:
run_tony()