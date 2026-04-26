import subprocess
import time


def open_video(path):
    # Plays video using VLC in blocking mode
    # Execution will pause here until playback finishes
    try:
        subprocess.run([
            "cvlc",
            "--play-and-exit",
            "--quiet",
            path
        ])
    except Exception as e:
        # Returns error message if VLC fails or is not installed
        return f"Video error: {e}"

    return "Video played."


import subprocess
import threading
import time


def open_file_async(path, duration=4):
    # Opens image asynchronously using feh and closes it after a fixed duration
    def _open():
        try:
            # Launch external viewer process (non-blocking)
            p = subprocess.Popen(["feh", path])

            # Keep window open for specified duration
            time.sleep(duration)

            # Force close the viewer process
            p.terminate()
        except:
            # Suppresses all errors
            pass

    # Run in daemon thread so it does not block main program flow
    threading.Thread(target=_open, daemon=True).start()
