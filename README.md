```markdown
# 🤖 AIRA – Offline Linux Voice Assistant

AIRA is a fully offline voice assistant for Linux that uses wake-word detection, speech recognition, confidence scoring, and command accuracy matching to control system functions like volume and brightness — all without internet access.

---

## 🚀 Features

- 🎙️ **Wake word detection** using Porcupine (`Hey Aira`)
- 🗣️ **Offline speech recognition** using Vosk
- 🧠 **Command matching** with accuracy percentage scoring
- 📊 **Confidence-based filtering** for reliable command execution
- 🔊 **Volume control** (increase / decrease)
- 🌞 **Brightness control** (increase / decrease)
- 💤 **Auto sleep mode** after 30 seconds of inactivity
- 🔈 **Offline text-to-speech** using Piper
- 🔐 **Privacy-first** (no cloud, no data sent)

---

## 🧠 How It Works

```
Wake Word (Porcupine)
        ↓
Active Mode
        ↓
Record Voice (arecord)
        ↓
Speech Recognition (Vosk)
        ↓
Confidence + Accuracy Check
        ↓
Execute System Command
        ↓
Sleep Mode (timeout / command)
```

---

## 📁 Project Structure

```
AIRA/
│
├── aira.py                           # Main assistant script
├── README.md                         # Documentation
├── wake.wav                          # Wake sound effect
├── hey-aira_en_linux_v4_0_0.ppn     # Porcupine wake word model
│
└── models/
    └── vosk-model-small-en-us-0.15/  # Vosk speech recognition model
```

---

## 🛠️ Installation

### 1. Prerequisites

Ensure you have Python 3.7+ and the following system tools:

```bash
sudo apt update
sudo apt install python3 python3-pip portaudio19-dev alsa-utils pulseaudio-utils brightnessctl
```

### 2. Install Python Dependencies

```bash
pip install pvporcupine pyaudio vosk
```

### 3. Download Models

#### Vosk Model (Speech Recognition)
Download the small English model from [Vosk Models](https://alphacephei.com/vosk/models):

```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/
```

#### Porcupine Wake Word Model
- Sign up at [Picovoice Console](https://console.picovoice.ai/)
- Train a custom wake word (`Hey Aira`) or use a built-in keyword
- Download the `.ppn` file and place it in the project directory

#### Piper TTS (Text-to-Speech)
Download Piper from [Piper Releases](https://github.com/rhasspy/piper/releases):

```bash
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
tar -xvzf piper_amd64.tar.gz
```

Download a voice model:

```bash
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx
```

### 4. Configure Paths

Edit `aira.py` and update these paths:

```python
ACCESS_KEY = "YOUR_PICOVOICE_ACCESS_KEY"
PIPER_BIN = "/path/to/piper"
PIPER_MODEL = "/path/to/en_US-amy-medium.onnx"
VOSK_MODEL_PATH = "/path/to/vosk-model-small-en-us-0.15"
```

---

## 🎮 Usage

### Run AIRA

```bash
python3 aira.py
```

### Supported Commands

| Category | Commands |
|----------|----------|
| **Volume** | volume up, volume down, increase volume, decrease volume, raise volume, lower volume |
| **Brightness** | brightness up, brightness down, increase brightness, decrease brightness, raise brightness, lower brightness, dim brightness |
| **System** | stop aira, aira stop, go to sleep, sleep mode |

### Example Interaction

```
😴 Sleeping… Say 'Hey Aira'
[User]: "Hey Aira"
🔊 Yes Vishal, I am listening

[User]: "Volume up"
🔊 Increasing volume
🎧 Waiting for next command…

[User]: "Go to sleep"
🔊 Okay, going to sleep
😴 Sleeping… Say 'Hey Aira'
```

---

## ⚙️ Configuration

### Adjust Thresholds

In `aira.py`, modify these values:

```python
TIMEOUT = 30              # Auto-sleep timer (seconds)
CONFIDENCE_LOW = 0.55     # Minimum confidence threshold
CONFIDENCE_HIGH = 0.75    # High confidence threshold
ACCURACY_MEDIUM = 60      # Minimum accuracy for command matching (%)
ACCURACY_HIGH = 75        # High accuracy threshold (%)
```

### Add Custom Commands

Add new commands to the `COMMANDS` list:

```python
COMMANDS = [
    "open browser",
    "close window",
    # ... existing commands
]
```

Implement the corresponding action functions:

```python
def open_browser():
    os.system("firefox &")

# Add to command handling section:
if best_cmd == "open browser":
    speak("Opening browser")
    open_browser()
```

---

## 🐛 Troubleshooting

### No Audio Input/Output

Check your audio devices:

```bash
arecord -l   # List recording devices
aplay -l     # List playback devices
```

Set default device in PulseAudio:

```bash
pactl list short sinks
pactl set-default-sink <sink-name>
```

### Porcupine Not Detecting Wake Word

- Verify your `ACCESS_KEY` is valid
- Ensure the `.ppn` file path is correct
- Check microphone permissions

### Vosk Recognition Issues

- Confirm the model path exists
- Try a larger Vosk model for better accuracy
- Reduce background noise

### Brightness Control Not Working

Ensure `brightnessctl` is installed and has proper permissions:

```bash
sudo usermod -aG video $USER
```

---

## 📊 Performance

- **Wake word detection latency**: ~200ms
- **Speech recognition**: ~1-2 seconds (depending on command length)
- **RAM usage**: ~150-200MB
- **CPU usage**: Low (single-threaded)

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Picovoice Porcupine](https://picovoice.ai/) - Wake word detection
- [Vosk](https://alphacephei.com/vosk/) - Offline speech recognition
- [Piper](https://github.com/rhasspy/piper) - Neural text-to-speech
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - Audio I/O

---

## 📧 Contact

For questions or suggestions, open an issue on GitHub or reach out via email.

---

**Made with ❤️ for privacy-conscious Linux users**
```