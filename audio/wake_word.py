import json
from vosk import Model, KaldiRecognizer
from audio.mic_stream import audio_q 

# List of phrases that trigger the assistant
WAKE_WORDS = ["hey pi", "hey pie", "hi pi"]


class WakeWord:
    def __init__(self):
        # Loads Vosk model
        # This duplicates memory usage and initialization time
        self.model = Model("models/vosk")

        # Recognizer configured
        self.rec = KaldiRecognizer(self.model, 16000)

    def listen(self):
        print("Waiting for wake word...")

        # Reset recognizer before listening loop
        self.rec.Reset()

        while True:
            data = audio_q.get()

            # Only processes final results
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())

                # Extract recognized text
                text = result.get("text", "").lower()

                # Simple substring match for wake word detection
                if any(w in text for w in WAKE_WORDS):
                    print("Wake detected:", text)

                    return True
