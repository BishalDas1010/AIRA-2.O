# AIRA 2.0 - AI Voice Assistant

A sophisticated AI-powered voice assistant for Linux systems that responds to voice commands and performs various system operations.

## Features

### Voice Control
- **Wake Word Detection**: Responds to "Hey Aira" wake word using Porcupine
- **Speech Recognition**: Uses Vosk for offline speech-to-text conversion
- **Text-to-Speech**: Integrates Piper for natural voice responses
- **Intelligent Matching**: Advanced command matching with accuracy thresholds

### Supported Commands

#### Music Control
- Play song/music: `"play song [song name]"`, `"play music"`
- Pause: `"pause song"`, `"pause music"`, `"stop song"`
- Resume: `"resume song"`, `"play again"`, `"continue song"`

#### Volume Control
- Increase: `"volume up"`, `"increase volume"`, `"raise volume"`
- Decrease: `"volume down"`, `"decrease volume"`, `"lower volume"`

#### Brightness Control
- Increase: `"brightness up"`, `"increase brightness"`, `"raise brightness"`
- Decrease: `"brightness down"`, `"decrease brightness"`, `"lower brightness"`

#### System Commands
- Sleep: `"stop aira"`, `"aira stop"`, `"go to sleep"`, `"sleep mode"`
- Flight Mode: `"turn on/off flight mode"`, `"enable/disable flight mode"`
- Battery: `"aira battery status"`, `"aira battery level"`, `"aira how much battery"`

#### Information
- Date: `"aira what is the date"`, `"aira tell me the date"`

## Requirements

### Python Packages
- `pvporcupine` - Wake word detection
- `pyaudio` - Audio input/output
- `vosk` - Offline speech recognition
- `requests` - HTTP requests
- `websockets` - WebSocket support

### External Dependencies
- **Piper TTS**: Text-to-speech engine
- **Vosk Model**: Speech recognition model (included in `models/`)
- **Porcupine Access Key**: Required for wake word detection

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/BishalDas1010/AIRA-2.O.git
cd AIRA-2.O
```

### 2. Create Virtual Environment
```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download Models
- Vosk model is included in the `models/` directory
- Voice model (Piper) is included in the `voices/` directory

### 5. Configure Paths
Edit `aira.py` and update these paths according to your system:
```python
PIPER_BIN = "/path/to/piper/piper"
PIPER_MODEL = "/path/to/voices/en_US-amy-medium.onnx"
VOSK_MODEL_PATH = "/path/to/models/vosk-model-small-en-us-0.15"
```

### 6. Set Porcupine Access Key
Update the `ACCESS_KEY` in `aira.py`:
```python
ACCESS_KEY = "your_porcupine_access_key"
```

## Usage

### Start AIRA
```bash
python aira.py
```

### Interaction Flow
1. AIRA starts in sleep mode waiting for the wake word "Hey Aira"
2. Say "Hey Aira" to activate
3. Speak your command clearly
4. AIRA processes the command and responds
5. Returns to listening mode after command execution
6. Auto-sleeps after 30 seconds of inactivity

## Configuration

### Adjustable Settings (in `aira.py`)
```python
TIMEOUT = 30                    # Auto-sleep timeout in seconds
CONFIDENCE_LOW = 0.55          # Low confidence threshold
CONFIDENCE_HIGH = 0.75         # High confidence threshold
ACCURACY_MEDIUM = 60           # Medium accuracy threshold (%)
ACCURACY_HIGH = 75             # High accuracy threshold (%)
USER_NAME = "Vishal"           # User's name
```

## Project Structure

```
AIRA-2.O/
├── aira.py                          # Main application
├── wake_ira.py                      # Wake word detection utility
├── test.py                          # Testing utilities
├── test_voice.py                    # Voice testing
├── README.md                        # This file
├── hey-aira_en_linux_v4_0_0.ppn    # Porcupine wake word model
├── models/
│   └── vosk-model-small-en-us-0.15/ # Vosk speech recognition model
├── voices/
│   └── en_US-amy-medium.onnx       # Piper TTS voice model
└── myenv/                           # Python virtual environment
```

## How It Works

### 1. Wake Word Detection
- Uses Porcupine to detect "Hey Aira" without cloud dependency
- Requires valid Porcupine access key

### 2. Speech Recognition
- Captures audio using PyAudio
- Converts speech to text using Vosk offline model
- Returns confidence scores for accuracy assessment

### 3. Command Matching
- Compares recognized speech against predefined command list
- Uses sequence matching to handle variations and typos
- Filters results based on accuracy thresholds

### 4. Command Execution
- Executes appropriate system commands
- Provides voice feedback via Piper TTS
- Maintains state for sleep/active modes

## Troubleshooting

### Common Issues

**Vosk model not found**
- Ensure the model path in `aira.py` is correct
- Download the model from [Vosk Models](https://alphacephei.com/vosk/models)

**Audio not working**
- Check PyAudio installation: `pip install pyaudio`
- Verify system audio permissions
- Test with `test_voice.py`

**Wake word not detected**
- Verify Porcupine access key is valid
- Check audio input device
- Ensure "Hey Aira" is spoken clearly

**Piper TTS errors**
- Verify Piper binary path is correct
- Ensure voice model file exists
- Check system has required audio codec libraries

## Performance Notes

- **Offline Operation**: Works completely offline after initial setup
- **Accuracy**: ~75-80% accuracy on clear commands
- **Response Time**: 1-2 seconds for typical commands
- **Resource Usage**: Minimal CPU and memory footprint

## Future Enhancements

- Cloud integration for advanced features
- Custom wake word training
- Machine learning-based command learning
- Multi-language support
- Context-aware responses
- Smart home integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Bishal Das** - [GitHub Profile](https://github.com/BishalDas1010)

## Acknowledgments

- [Porcupine](https://porcupine.ai/) - Wake word detection
- [Vosk](https://alphacephei.com/vosk/) - Speech recognition
- [Piper](https://github.com/rhasspy/piper) - Text-to-speech
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - Audio handling

## Support

For issues, questions, or suggestions, please open an [Issue](https://github.com/BishalDas1010/AIRA-2.O/issues) on GitHub.
