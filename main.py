import time
from controller import handle_input
from audio.stt import STT
from audio.wake_word import WakeWord
from audio.tts import speak
from audio.mic_stream import start_stream, stop_stream
from logs.logger import logger


def main():
    # Entry point for the voice assistant runtime loop
    print("=== Voice Assistant ===")

    # Initialize core audio components
    stt = STT()
    wake = WakeWord()

    # Start continuous microphone stream for wake word detection
    stream = start_stream()

    while True:
        # Passive listening phase: wait for wake word trigger
        if wake.listen():

            # Reset logger state for a new interaction cycle
            logger.reset()

            # Stop stream before active recording to avoid conflicts
            stop_stream(stream)

            # Immediate feedback to user that system is listening
            speak("yes")

            # Restart stream for speech capture
            stream = start_stream()

            # Capture spoken command using STT
            start = time.time()
            command = stt.listen_command()

            # Stop stream after capturing command
            stop_stream(stream)  

            # If no speech was detected, restart listening loop
            if not command:
                stream = start_stream()
                continue

            # Log STT latency and recognized input
            logger.log_stt(time.time() - start)
            logger.set_input(command)

            # Process user input through controller (routing + tools/LLM)
            response = handle_input(command)
            logger.set_response(response)

            print("Assistant:", response)

            # Convert response to speech
            start = time.time()
            speak(response)
            logger.log_tts(time.time() - start)

            # Persist full interaction (input, output, timings)
            logger.save(event="interaction")

            # Restart microphone stream for next wake cycle
            stream = start_stream()


if __name__ == "__main__":
    # Run assistant only when script is executed directly
    main()
