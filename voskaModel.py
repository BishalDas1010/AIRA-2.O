from vosk import Model as VoskModel, KaldiRecognizer
import json

VOSK_MODEL_PATH = "/media/bishaldas/Apps/AIRA/models/vosk-model-small-en-us-0.15"

class VoskEngine:
    def __init__(self, commands):
        # Load Vosk model ONCE
        self.vosk_model = VoskModel(VOSK_MODEL_PATH)
        self.commands = commands
    def create_recognizer(self):
        """Create a fresh Vosk recognizer instance"""
        recognizer = KaldiRecognizer(
            self.vosk_model,
            16000,
            json.dumps(self.commands)
        )
        recognizer.SetWords(True)
        return recognizer
