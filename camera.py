import os
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

from actions.media_manager import add_media, load_index, get_next_id, save_index

# Directory for storing all captured media
MEDIA_DIR = "data/media"
os.makedirs(MEDIA_DIR, exist_ok=True)


class CameraController:
    def __init__(self):
        self.picam2 = None
        self.started = False

    def init(self):
        # Initialize camera only once per operation cycle
        if not self.started:
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration()
            self.picam2.configure(config)
            self.picam2.start()

            # Short delay to allow camera sensor to stabilize
            time.sleep(1)

            self.started = True

    def close(self):
        # Safely release camera resources after each operation
        if self.picam2 and self.started:
            try:
                self.picam2.stop()
                self.picam2.close()
            except:
                # Suppress hardware shutdown errors to avoid crashing main loop
                pass
            self.started = False

    def take_picture(self):
        try:
            self.init()

            # Load media index and assign next available ID
            data = load_index()
            file_id = get_next_id(data, "image")

            filename = f"{MEDIA_DIR}/image_{file_id}.jpg"

            # Capture and save image to disk
            self.picam2.capture_file(filename)

            # Register file in media index system
            media_id = add_media(filename, "image")

            # Always close camera after operation to free hardware
            self.close()

            return f"image {media_id}"

        except Exception as e:
            # Ensure camera is closed even on failure
            self.close()
            return f"Camera error: {e}"
    def record_video(self, duration=5):
        try:
            self.init()

            # Temporary filename used during recording
            filename = f"{MEDIA_DIR}/video_temp.h264"

            encoder = H264Encoder()
            output = FileOutput(filename)

            # Start recording using H264 encoder
            self.picam2.start_recording(encoder, output)

            # Blocking wait for duration
            time.sleep(int(duration))

            self.picam2.stop_recording()

            # Release camera before file operations
            self.close()

            # Register temporary file first to obtain media ID
            media_id = add_media(filename, "video")

            # Rename file to permanent ID-based filename
            new_filename = f"{MEDIA_DIR}/video_{media_id}.h264"
            os.rename(filename, new_filename)

            # Update stored path in media index
            data = load_index()
            for item in data:
                if item["id"] == media_id and item["type"] == "video":
                    item["path"] = new_filename
                    break
            save_index(data)

            return f"video {media_id}"

        except Exception as e:
            # Ensure camera is closed even if recording fails
            self.close()
            return f"Camera error: {e}"

    def capture_for_vision(self):
        try:
            self.init()

            # Temporary image used for immediate vision processing
            filename = f"{MEDIA_DIR}/vision_temp.jpg"

            self.picam2.capture_file(filename)

            # Close camera immediately after capture to minimize lock time
            self.close()

            return filename

        except Exception as e:
            # Ensure camera is closed on failure
            self.close()
            return f"Camera error: {e}"


# Shared singleton instance used across the system
camera = CameraController()
