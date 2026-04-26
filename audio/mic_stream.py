import sounddevice as sd
import queue

# Shared queue used to store incoming raw audio chunks
audio_q = queue.Queue()


def callback(indata, frames, time, status):
    # This function is called continuously by the audio stream (in a separate thread)
    # Converts incoming audio buffer to bytes and pushes it into the queue
    audio_q.put(bytes(indata))


def start_stream():
    # Initializes a raw audio input stream (non-blocking)
    # Uses 16kHz mono audio, suitable for speech recognition (e.g., Whisper)
    stream = sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,   # number of frames per chunk (affects latency vs throughput)
        dtype='int16',    # 16-bit PCM format
        channels=1,       # mono audio
        callback=callback
    )

    # Starts audio capture; callback begins feeding data into queue
    stream.start()
    return stream


def stop_stream(stream):
    # Safely stops and releases the audio stream
    if stream:
        stream.stop()
        stream.close()
