import json
from vosk import Model, KaldiRecognizer
from audio.mic_stream import audio_q


class STT:
    def __init__(self):
        # Loads offline speech recognition model
        self.model = Model("models/vosk")

        # Recognizer configured
        self.rec = KaldiRecognizer(self.model, 16000)

    def listen_command(self):
        print("Listening for command...")

        # Reset recognizer state before starting new utterance
        self.rec.Reset()

        while True:
            # Blocking call: waits until audio data is available
            data = audio_q.get()

            if self.rec.AcceptWaveform(data):
                # Parse final recognition result
                result = json.loads(self.rec.Result())

                # Extract recognized text
                text = result.get("text", "").strip()

                print("You said:", text)

                # Returns immediately after first complete phrase
                return text
