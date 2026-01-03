import pvporcupine
import pyaudio
import struct
import os
import signal
import sys
import json
import time
from vosk import Model, KaldiRecognizer
from difflib import SequenceMatcher

# ================= CONFIG =================
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
# ==========================================

# ---------- CHECK MODEL ----------
if not os.path.exists(VOSK_MODEL_PATH):
    print("❌ Vosk model not found")
    sys.exit(1)

# ---------- COMMAND GRAMMAR ----------
COMMANDS = [
    # Volume
    "volume up",
    "volume down",
    "increase volume",
    "decrease volume",
    "raise volume",
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
    "sleep mode"
]


vosk_model = Model(VOSK_MODEL_PATH)
vosk_recognizer = KaldiRecognizer(
    vosk_model,
    16000,
    json.dumps(COMMANDS)
)
vosk_recognizer.SetWords(True)

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

# ---------- CONFIDENCE ----------
def extract_confidence(result):
    words = result.get("result")
    if not words:
        return None
    confs = [w.get("conf", 0.0) for w in words if "conf" in w]
    return sum(confs) / len(confs) if confs else None

# ---------- ACCURACY ----------
def command_accuracy(spoken, valid_commands):
    best_score = 0
    best_match = None
    for cmd in valid_commands:
        score = SequenceMatcher(None, spoken, cmd).ratio()
        if score > best_score:
            best_score = score
            best_match = cmd
    return best_match, round(best_score * 100, 2)

# ---------- COMMAND LISTENER ----------
def listen_light_command():
    print("🎙️ Listening...")

    os.system("arecord -d 3 -r 16000 -f S16_LE -c 1 /tmp/cmd.wav 2>/dev/null")

    with open("/tmp/cmd.wav", "rb") as f:
        f.read(44)
        audio = f.read()
        vosk_recognizer.AcceptWaveform(audio)

    result = json.loads(vosk_recognizer.Result())
    command = result.get("text", "").lower().strip()
    confidence = extract_confidence(result)

    print(f"VOSK: '{command}' | confidence={confidence}")
    if not command:
        return None, None

    return command, confidence

os_path ="paplay /usr/share/sounds/freedesktop/stereo/audio-volume-change.oga"
# ACTIONS 

def volume_up():
    os.system("pactl set-sink-volume @DEFAULT_SINK@ +10%")
    os.system(os_path)
def volueme_down():
    os.system("pactl set-sink-volume @DEFAULT_SINK@ -5%")
    os.system(os_path)

def sleep_mode():
    pass
def sound_increse():
    pass 
def sound_decrese():
    pass
def wifi_on():
    pass
def wifi_off():
    pass


def brightness_up():
    os.system("brightnessctl set +10%")
    os.system(os_path)

def brightness_down():
    os.system("brightnessctl set 10%-")
    os.system(os_path)

def speak(text):
    os.system(
        f'echo "{text}" | {PIPER_BIN} '
        f'-m {PIPER_MODEL} '
        f'-f /tmp/reply.wav && paplay /tmp/reply.wav'
    )

# PORCUPINE 
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

print(" :) AIRA running...")
print("😴 Sleeping… Say 'Hey Aira'")

# ---------- MAIN LOOP ----------
while True:

    # ================= SLEEP MODE =================
    if state == STATE_SLEEP:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm) >= 0:
            os.system(f"paplay {WAKE_SOUND}")
            speak("Yes Vishal, I am listening")
            state = STATE_ACTIVE
            last_command_time = time.time()

    # ================= ACTIVE MODE =================
    elif state == STATE_ACTIVE:

        # Auto-sleep on timeout
        if time.time() - last_command_time > TIMEOUT:
            speak("Going to sleep")
            state = STATE_SLEEP
            print("😴 Sleeping… Say 'Hey Aira'")
            continue

        command, confidence = listen_light_command()
        last_command_time = time.time()

        # Silence
        if command is None:
            speak("Going to sleep")
            state = STATE_SLEEP
            continue

        # Confidence check
        if confidence is not None and confidence < CONFIDENCE_LOW:
            speak("I am not sure I heard you correctly. Please repeat.")
            continue

        # Accuracy check
        best_cmd, accuracy = command_accuracy(command, COMMANDS)
        print(f" Accuracy: {accuracy}% (match='{best_cmd}')")

        if accuracy < ACCURACY_MEDIUM:
            speak("I am not sure what you meant. Please repeat.")
            continue

        # Stop commands
        if best_cmd in ["stop aira", "aira stop", "go to sleep", "sleep mode"]:
            speak("Okay, going to sleep")
            state = STATE_SLEEP
            print("😴 Sleeping… Say 'Hey Aira'")
            continue
         #volume increse 
        if best_cmd in ['volume up','increase volume']:
            speak("Increasing volume")
            volume_up()
        

        # Brightness commands
        if best_cmd in ["brightness up", "increase brightness", "raise brightness"]:
            speak("Increasing brightness")
            brightness_up()

        elif best_cmd in ["brightness down", "decrease brightness", "lower brightness", "dim brightness"]:
            speak("Decreasing brightness")
            brightness_down()

        else:
            speak("Sorry, I did not understand")

        print("🎧 Waiting for next command…")
