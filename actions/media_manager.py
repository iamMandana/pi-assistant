import os
import json
from actions.media_viewer import open_file_async, open_video

# JSON file used as persistent storage for media metadata
INDEX_FILE = "data/media/index.json"

# Ensure media directory exists before any file operations
os.makedirs("data/media", exist_ok=True)


def load_index():
    # Load media index from disk
    # Returns empty list if file does not exist or is corrupted
    if not os.path.exists(INDEX_FILE):
        return []

    try:
        with open(INDEX_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_index(data):
    # Persist full media index to disk
    with open(INDEX_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_next_id(data, media_type):
    # Generate next ID based only on items of the same type
    # This means image IDs and video IDs are independent sequences
    filtered = [item for item in data if item["type"] == media_type]

    if not filtered:
        return 1

    return max(item["id"] for item in filtered) + 1


def add_media(path, media_type):
    # Add new media entry and persist it
    data = load_index()

    media_id = get_next_id(data, media_type)

    entry = {
        "id": media_id,
        "type": media_type,
        "path": path
    }

    data.append(entry)
    save_index(data)

    return media_id


def get_media(media_id, media_type=None):
    # Retrieve media by ID, optionally filtering by type
    # If type is provided and does not match, continues searching
    data = load_index()

    for item in data:
        if item["id"] == int(media_id):
            if media_type:
                if item["type"] == media_type:
                    return item
                else:
                    continue  # continue searching for matching type
            return item

    # Returns None if no matching media found
    return None


def get_latest_media(media_type="image"):
    # Returns the most recently added media of a given type
    # Assumes entries are appended in chronological order
    data = load_index()

    filtered = [x for x in data if x["type"] == media_type]

    if not filtered:
        return None

    return filtered[-1]


def open_saved_image(image_id):
    # Retrieve image metadata and open file asynchronously
    media = get_media(image_id, "image")

    if not media:
        return f"Image {image_id} not found."

    return open_file_async(media["path"])


def open_saved_video(video_id):
    # Retrieve video metadata and open using video-specific handler
    media = get_media(video_id, "video")

    if not media:
        return f"Video {video_id} not found."

    return open_video(media["path"])
