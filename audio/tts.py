import subprocess
import time


# Path to Piper TTS model
MODEL_PATH = "models/piper/en_US-lessac-medium.onnx"


def speak(text):
    # Small delay to reduce overlap between consecutive TTS calls
    time.sleep(0.2)

    # Start Piper TTS process
    # Outputs raw PCM audio to stdout
    piper = subprocess.Popen(
        ["piper", "--model", MODEL_PATH, "--output-raw"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )

    # Start audio playback process
    aplay = subprocess.Popen(
        ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw"],
        stdin=piper.stdout
    )

    try:
        # Send text input to Piper via stdin
        piper.stdin.write(text.encode())

        # Close stdin to signal end of input
        piper.stdin.close()

        # Wait for playback process to finish
        aplay.communicate()

    except Exception as e:
        # Prints error but does not stop or clean up processes explicitly
        print("TTS error:", e)
