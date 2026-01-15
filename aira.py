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
from voskaModel import VoskEngine
from aira_function import function_aira
from comands import comands
from keys import ACCESS_KEYY


ACCESS_KEY = ACCESS_KEYY

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




COMMANDSs =comands
COMMANDS = COMMANDSs.COMMANDS
YES_WORDS = ["yes", "yeah", "confirm", "sure", "do it"]
NO_WORDS  = ["no", "cancel", "stop", "don't", "do not"]

script_path = "sudo ./keyboard.sh"


voskaa = VoskEngine(COMMANDS)
vosk_recognizer = voskaa.create_recognizer()

# ---------- STATES ----------
STATE_SLEEP = 0
STATE_ACTIVE = 1

state = STATE_SLEEP
last_command_time = time.time()

# ---------- CLEANUP ----------
def cleanup(sig=None, frame=None):
    print("\n Shutting down AIRA...")
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
    vosk_recognizer = voskaa.create_recognizer()

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
    free_recognizer = KaldiRecognizer(voskaa.vosk_model, 16000)
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

def speak(text):
    """Convert text to speech using Piper"""
    os.system(
        f'echo "{text}" | {PIPER_BIN} '
        f'-m {PIPER_MODEL} '
        f'-f /tmp/reply.wav && paplay /tmp/reply.wav'
    )

function_Aira =function_aira(SOUND_EFFECT=SOUND_EFFECT)

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
                free_recognizer = KaldiRecognizer(voskaa.vosk_model, 16000)
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
            speak(f"Playing {song_name}")
            function_Aira.play_song(song_name)
            
            # Reset timer after playing
            last_command_time = time.time()

        # Volume up commands
        elif best_cmd in ['volume up', "raise volume", "aira raise volume", 'increase volume']:
            speak("Increasing volume")
            function_Aira.volume_up()

        # Volume down commands
        elif best_cmd in ['volume down', 'decrease volume', 'lower volume']:
            speak("Decreasing volume")
            function_Aira.volume_down()

        # Date commands
        elif best_cmd in ["aira tell me the date", "aira what is the date"]:
            function_Aira.date_today()
            speak(get_today_date())

        # Flight mode on commands
        elif best_cmd in ["turn on flight mode", "enable flight mode", "flight mode on", "airplane mode on"]:
            speak("Enabling flight mode")
            function_Aira.airplane_mode_on()

        # Flight mode off commands
        elif best_cmd in ["turn off flight mode", "disable flight mode", "flight mode off", "airplane mode off"]:
            speak("Disabling flight mode")
            function_Aira.airplane_mode_off()

        # Battery commands
        elif best_cmd in ["aira battery percentage", "aira battery status", "aira how much battery", "aira battery level"]:
            battery_info = function_Aira.get_battery_info()
            speak(battery_info)

        # Brightness up commands
        elif best_cmd in ["brightness up", "increase brightness", "raise brightness"]:
            speak("Increasing brightness")
            function_Aira.brightness_up()

        # Brightness down commands
        elif best_cmd in ["brightness down", "decrease brightness", "lower brightness", "dim brightness"]:
            speak("Decreasing brightness")
            function_Aira.brightness_down()

        # Pause song commands
        elif best_cmd in ["pause song", "puse song", "pause music", "song puse","stop song"]:
            function_Aira.pause_song()
            speak("Song paused")

        # Resume song commands
        elif best_cmd in ["resume song", "play again", "continue song"]:      
            function_Aira.resume_song()
            speak("Resuming song")
            
        # sleep
        elif best_cmd in ["sleep system", "lock and sleep", "suspend system"]:
            speak("Are you sure you want to suspend the system?")
            
            # listen again for confirmation
            confirm_cmd, confirm_conf = listen_light_command()

            if not confirm_cmd:
                speak("No response received. Canceling.")
                

            if confirm_cmd in YES_WORDS:
                speak("Locking and suspending the system.")
                os.system("systemctl suspend")

            elif confirm_cmd in NO_WORDS:
                speak("Okay, canceled.")

            else:
                speak("I didn't understand. Canceling.")


            #next song
        elif best_cmd in ["next song","next music","song next"]:
            function_Aira.next()
            speak("playing next song ")
        elif best_cmd in ["turn on keyboard brightness", "keyboard brightness on","enable keyboard light"]:
            function_Aira.on_keyboard(script_path)
            speak("turn on keyboard brightness")

        elif best_cmd in ["turn off keyboard brightness", "keyboard brightness off", "disable keyboard light"]:
            function_Aira.off_keyboard(script_path)
            speak("turn off keyboard brightness")

        elif best_cmd in ["aira cpu percentage","aira cpu use","aira cpu use","cpu uses"]:
            cpu_percent = function_Aira.cpu_uses()
            speak(f"CPU usage is {cpu_percent}%")
        elif best_cmd in ["aira trun on night mode","night mode on","on night mode"]:
            function_Aira.night_mode_on()
            speak("night mode trun on")
        elif best_cmd in ["aira trun off night mode","night mode off","off night mode","trun off night mode"]:
            function_Aira.night_mode_off()
            speak("night mode trun off")
            #bluetooth on/off
        elif best_cmd in ["trun on bluetooth","aira trun on bluetooth","bluetooth on","on bluetooth"]:
            function_Aira.bluetoot_on()
            speak("bluetooth on")
        elif best_cmd in ["turn off bluetooth","aira trun off bluetooth","bluetooth off"]:
            function_Aira.bluetooth_off()
            speak("bluetooth off")

        #Take screenshorttttt

        elif best_cmd in ["Take a screenshot","AIRA Take a screenshot","aira screenshot Take"]:
            function_Aira.function_screenshort()
            speak("Tacking screenshort")

        #power off 
        else:
            speak("Sorry, I did not understand")

        print("🎧 Waiting for next command…")