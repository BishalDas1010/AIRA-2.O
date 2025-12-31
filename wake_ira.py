import pvporcupine
import pyaudio
import struct
import os
import signal
import sys

ACCESS_KEY = "p0NrqyvjKthFyzLAzUufVls5MgKSz3RYOQczVV9cCkfBMn/aZXug3Q=="

def cleanup(sig, frame):
    print("\n Stopping IRA...")
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)

porcupine = pvporcupine.create(
    access_key=ACCESS_KEY,
    keywords=["hey google"]
)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("IRA is listening for wake word...")

while True:
    pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

    if porcupine.process(pcm) >= 0:
        print(" Wake word detected!")

        # Wake sound
        os.system("paplay wake.wav")

        # Voice response
        os.system(
            'echo "Yes Vishal, how can I help you?" | '
            '/home/bishaldas/piper/piper/piper '
            '-m /home/bishaldas/piper/voices/en_US-amy-medium.onnx '
            '-f /tmp/reply.wav && paplay /tmp/reply.wav'
        )
