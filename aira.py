import pvporcupine
import pyaudio
import struct
import os
import signal
import sys
import json
import time
import subprocess
from vosk import Model, KaldiRecognizer
from difflib import SequenceMatcher
from datetime import datetime
import webbrowser
import urllib.parse
import requests
import re

ACCESS_KEY = "nIQ6KLjPZ9+wibbwBOjDDY5jhoH+h8fVXGS+wts4R/rR3fdEW8Y6jA=="

WAKE_SOUND = "wake.wav"

PIPER_BIN = "/home/bishaldas/piper/piper/piper"
PIPER_MODEL = "/home/bishaldas/piper/voices/en_US-amy-medium.onnx"

VOSK_MODEL_PATH = "/media/bishaldas/Apps/AIRA/models/vosk-model-small-en-us-0.15"

# Auto-sleep after inactivity (seconds)
TIMEOUT = 30

# Confidence thresholds
CONFIDENCE_LOW = 0.55
CONFIDENCE_HIGH = 0.75

# Accuracy thresholds (percentage)
ACCURACY_MEDIUM = 60
ACCURACY_HIGH = 75

# User name (configurable)
USER_NAME = "Vishal"

# CHECK MODEL
if not os.path.exists(VOSK_MODEL_PATH):
    print("Vosk model not found")
    sys.exit(1)


def get_today_date():
    """Get formatted date string"""
    now = datetime.now()
    day = now.strftime("%A")
    date = now.strftime("%d").lstrip("0")
    month = now.strftime("%B")
    year = now.strftime("%Y")
    return f"Today is {day}, {date} {month} {year}"


# ---------- COMMAND GRAMMAR ----------
COMMANDS = [

    "pause song", 
    "puse song", 
    "pause music", 
    "stop song",

    #song 
    "resume song", 
    "play again",
    "continue song",


    # Volume
    "volume up",
    "increase volume",
    "raise volume",
    "aira raise volume",
    "decrease volume",
    "volume down",
    "lower volume",

    # Brightness
    "brightness up",
    "brightness down",
    "increase brightness",
    "decrease brightness",
    "raise brightness",
    "lower brightness",
    "dim brightness",

    # System
    "stop aira",
    "aira stop",
    "go to sleep",
    "sleep mode",

    # Date 
    "aira what is the date",
    "aira tell me the date",
    
    # Flight mode
    "turn on flight mode",
    "enable flight mode",
    "flight mode on",
    "airplane mode on",
    "turn off flight mode",
    "disable flight mode",
    "flight mode off",
    "airplane mode off",
    
    # Battery
    "aira battery percentage",
    "aira battery status",
    "aira how much battery",
    "aira battery level",

    # Music
    "play song",
    "play music",
    "aira play song",
    "aira play music"
]


vosk_model = Model(VOSK_MODEL_PATH)

def create_recognizer():
    """Create a fresh Vosk recognizer instance"""
    recognizer = KaldiRecognizer(
        vosk_model,
        16000,
        json.dumps(COMMANDS)
    )
    recognizer.SetWords(True)
    return recognizer

vosk_recognizer = create_recognizer()

# ---------- STATES ----------
STATE_SLEEP = 0
STATE_ACTIVE = 1

state = STATE_SLEEP
last_command_time = time.time()

# ---------- CLEANUP ----------
def cleanup(sig=None, frame=None):
    print("\n🛑 Shutting down AIRA...")
    try:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
    except:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

# CONFIDENCE
def extract_confidence(result):
    words = result.get("result")
    if not words:
        return None
    confs = [w.get("conf", 0.0) for w in words if "conf" in w]
    return sum(confs) / len(confs) if confs else None

# ACCURACY 
def command_accuracy(spoken, valid_commands):
    best_score = 0
    best_match = None
    for cmd in valid_commands:
        score = SequenceMatcher(None, spoken, cmd).ratio()
        if score > best_score:
            best_score = score
            best_match = cmd
    return best_match, round(best_score * 100, 2)

# COMMAND LISTENER 
def listen_light_command():
    global vosk_recognizer
    print("🎤 Listening...")

    os.system("arecord -d 3 -r 16000 -f S16_LE -c 1 /tmp/cmd.wav 2>/dev/null")

    # Create fresh recognizer for each command
    vosk_recognizer = create_recognizer()

    with open("/tmp/cmd.wav", "rb") as f:
        f.read(44)  # Skip WAV header
        audio = f.read()
        vosk_recognizer.AcceptWaveform(audio)

    result = json.loads(vosk_recognizer.Result())
    command = result.get("text", "").lower().strip()
    confidence = extract_confidence(result)

    print(f"📝 VOSK: '{command}' | confidence={confidence}")
    if not command:
        return None, None

    return command, confidence


def listen_free_form():
    """Listen for free-form speech (not constrained to COMMANDS)"""
    print("🎤 Listening for free-form input...")
    
    os.system("arecord -d 3 -r 16000 -f S16_LE -c 1 /tmp/cmd.wav 2>/dev/null")
    
    # Create recognizer WITHOUT grammar constraints
    free_recognizer = KaldiRecognizer(vosk_model, 16000)
    free_recognizer.SetWords(True)
    
    with open("/tmp/cmd.wav", "rb") as f:
        f.read(44)  # Skip WAV header
        audio = f.read()
        free_recognizer.AcceptWaveform(audio)
    
    result = json.loads(free_recognizer.Result())
    text = result.get("text", "").lower().strip()
    confidence = extract_confidence(result)
    
    print(f"📝 FREE-FORM: '{text}' | confidence={confidence}")
    return text, confidence


# Sound effect path
SOUND_EFFECT = "paplay /usr/share/sounds/freedesktop/stereo/audio-volume-change.oga"

# ---------- ACTIONS ----------
def pause_song():
    """Pause currently playing media"""
    os.system("playerctl pause")
    speak("Song paused")

def resume_song():
    """Resume/play currently paused media"""
    os.system("playerctl play")
    speak("Resuming song")

def volume_up():
    """Increase system volume"""
    os.system("pactl set-sink-volume @DEFAULT_SINK@ +10%")
    os.system(SOUND_EFFECT)

def volume_down():
    """Decrease system volume"""
    os.system("pactl set-sink-volume @DEFAULT_SINK@ -10%")
    os.system(SOUND_EFFECT)

def date_today():
    """Speak the current date"""
    speak(get_today_date())

def get_battery_info():
    """Get battery percentage"""
    try:
        result = subprocess.run(
            "upower -i $(upower -e | grep BAT) | grep -E 'percentage' | awk '{print $2}'",
            shell=True,
            capture_output=True,
            text=True
        )
        battery_percent = result.stdout.strip()
        if battery_percent:
            return f"Battery is at {battery_percent}"
        else:
            return "Unable to get battery status"
    except Exception as e:
        return "Error checking battery"

def airplane_mode_on():
    """Enable airplane mode (disable WiFi)"""
    os.system("nmcli radio wifi off")
    os.system(SOUND_EFFECT)

def airplane_mode_off():
    """Disable airplane mode (enable WiFi)"""
    os.system("nmcli radio wifi on")
    os.system(SOUND_EFFECT)

def brightness_up():
    """Increase screen brightness"""
    os.system("brightnessctl set +10%")
    os.system(SOUND_EFFECT)

def brightness_down():
    """Decrease screen brightness"""
    os.system("brightnessctl set 10%-")
    os.system(SOUND_EFFECT)

def speak(text):
    """Convert text to speech using Piper"""
    os.system(
        f'echo "{text}" | {PIPER_BIN} '
        f'-m {PIPER_MODEL} '
        f'-f /tmp/reply.wav && paplay /tmp/reply.wav'
    )

def play_song(song):
    """Play song on YouTube Music (with fallback to regular YouTube)"""
    query = urllib.parse.quote(song)
    
    try:
        # Try YouTube Music first
        music_search_url = f"https://music.youtube.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(music_search_url, headers=headers, timeout=5)
        html = response.text
        
        # Try multiple patterns for YouTube Music
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        
        if not video_ids:
            # Fallback: Try getting from regular YouTube
            print("🔄 Trying regular YouTube...")
            yt_search_url = f"https://www.youtube.com/results?search_query={query}+official+audio"
            response = requests.get(yt_search_url, headers=headers, timeout=5)
            html = response.text
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        
        speak(f"Playing {song}")
        
        if video_ids:
            # Open first result in YouTube Music
            music_url = f"https://music.youtube.com/watch?v={video_ids[0]}"
            print(f"🎵 Opening: {music_url}")
            webbrowser.open(music_url)
        else:
            # Last resort: direct search on YouTube Music
            print("⚠️ No video ID found, opening search page")
            webbrowser.open(f"https://music.youtube.com/search?q={query}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        speak("Unable to play song")


# ---------- PORCUPINE ----------
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keyword_paths=["/media/bishaldas/Apps/AIRA/hey-aira_en_linux_v4_0_0.ppn"]
)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("✨ AIRA running...")
print("😴 Sleeping… Say 'Hey Aira'")

# ---------- MAIN LOOP ----------
while True:

    # SLEEP MODE 
    if state == STATE_SLEEP:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm) >= 0:
            os.system(f"paplay {WAKE_SOUND}")
            speak(f"Yes {USER_NAME}, I am listening")
            state = STATE_ACTIVE
            last_command_time = time.time()

    # ACTIVE MODE 
    elif state == STATE_ACTIVE:

        # Auto-sleep on timeout
        if time.time() - last_command_time > TIMEOUT:
            speak("Going to sleep")
            state = STATE_SLEEP
            print("😴 Sleeping… Say 'Hey Aira'")
            continue

        command, confidence = listen_light_command()

        # Silence - go to sleep
        if command is None:
            speak("Going to sleep")
            state = STATE_SLEEP
            print("😴 Sleeping… Say 'Hey Aira'")
            continue

        # Confidence check (handle None and low confidence)
        if confidence is None or confidence < CONFIDENCE_LOW:
            speak("I am not sure I heard you correctly. Please repeat.")
            continue

        # Accuracy check
        best_cmd, accuracy = command_accuracy(command, COMMANDS)
        print(f"🎯 Accuracy: {accuracy}% (match='{best_cmd}')")

        if accuracy < ACCURACY_MEDIUM:
            speak("I am not sure what you meant. Please repeat.")
            continue

        # Only reset timer on successful command recognition
        last_command_time = time.time()

        # Stop commands
        if best_cmd in ["stop aira", "aira stop", "go to sleep", "sleep mode"]:
            speak("Okay, going to sleep")
            state = STATE_SLEEP
            print("😴 Sleeping… Say 'Hey Aira'")
            continue

        # Music commands - Advanced Siri-like behavior
        elif best_cmd in ["play song", "play music", "aira play song", "aira play music"]:
            # Check if song name is already in the command
            song_name = None
            
            # Only extract if command is longer than the matched command
            if command != best_cmd:
                # Extract song name from original command if present
                for prefix in ["aira play song", "aira play music", "play song", "play music", "aira play", "play"]:
                    if command.startswith(prefix):
                        potential_song = command[len(prefix):].strip()
                        # Must have at least 2 characters to be valid
                        if potential_song and len(potential_song) >= 5:
                            song_name = potential_song
                            break
            
            # If no song name found, ask for it
            if not song_name:
                speak("Which song?")
                
                # Listen for song name with shorter timeout (2 seconds instead of 3)
                os.system("arecord -d 2 -r 16000 -f S16_LE -c 1 /tmp/song.wav 2>/dev/null")
                
                # Use free-form recognizer
                free_recognizer = KaldiRecognizer(vosk_model, 16000)
                free_recognizer.SetWords(True)
                
                with open("/tmp/song.wav", "rb") as f:
                    f.read(44)  # Skip WAV header
                    audio = f.read()
                    free_recognizer.AcceptWaveform(audio)
                
                result = json.loads(free_recognizer.Result())
                song_name = result.get("text", "").lower().strip()
                
                print(f"🎵 Song name: '{song_name}'")
                
                if not song_name:
                    speak("I didn't catch that")
                    continue
            
            # Validate song name length
            word_count = len(song_name.split())
            if word_count > 8:
                speak("Please say a shorter song name")
                continue
            
            if word_count == 0:
                speak("I didn't hear a song name")
                continue
            
            # Play immediately without re-checking
            play_song(song_name)
            
            # Reset timer after playing
            last_command_time = time.time()

        # Volume up commands
        elif best_cmd in ['volume up', "raise volume", "aira raise volume", 'increase volume']:
            speak("Increasing volume")
            volume_up()

        # Volume down commands
        elif best_cmd in ['volume down', 'decrease volume', 'lower volume']:
            speak("Decreasing volume")
            volume_down()

        # Date commands
        elif best_cmd in ["aira tell me the date", "aira what is the date"]:
            date_today()

        # Flight mode on commands
        elif best_cmd in ["turn on flight mode", "enable flight mode", "flight mode on", "airplane mode on"]:
            speak("Enabling flight mode")
            airplane_mode_on()

        # Flight mode off commands
        elif best_cmd in ["turn off flight mode", "disable flight mode", "flight mode off", "airplane mode off"]:
            speak("Disabling flight mode")
            airplane_mode_off()

        # Battery commands
        elif best_cmd in ["aira battery percentage", "aira battery status", "aira how much battery", "aira battery level"]:
            battery_info = get_battery_info()
            speak(battery_info)

        # Brightness up commands
        elif best_cmd in ["brightness up", "increase brightness", "raise brightness"]:
            speak("Increasing brightness")
            brightness_up()

        # Brightness down commands
        elif best_cmd in ["brightness down", "decrease brightness", "lower brightness", "dim brightness"]:
            speak("Decreasing brightness")
            brightness_down()

        # Pause song commands
        elif best_cmd in ["pause song", "puse song", "pause music", "stop song"]:
            pause_song()

        # Resume song commands
        elif best_cmd in ["resume song", "play again", "continue song"]:      
            resume_song()
            
        else:
            speak("Sorry, I did not understand")

        print("🎧 Waiting for next command…")