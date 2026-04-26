import time
import re
import threading
from datetime import datetime
from actions.media_manager import get_media
from vision.vision import vision_model
from actions.camera import camera
from model.chat_memory import memory
from actions.media_viewer import open_file_async, open_video
from logs.logger import logger
from vision.video_model import describe_video 


class VisionResult:
    def __init__(self):
        self.caption = None
        self.error = None


# Stores history of all vision observations
vision_history = []  # [{caption, time, path}]

# Stores last seen caption for quick access
last_seen_caption = None


def extract_object(question):
    # Extracts target object from user question by removing noise and patterns
    if not question:
        return ""

    question = question.lower()

    # Normalize number words
    try:
        from parser import words_to_numbers
        question = words_to_numbers(question)
    except:
        pass

    # Remove references like "in image 2", "in video 3"
    question = re.sub(r"in (image|photo|video)\s*(\d+)", "", question)
    question = re.sub(r"in (image|photo|video)\s*(one|two|three|four|five|six|seven|eight|nine|ten)", "", question)

    # Remove standalone references like "video 5"
    question = re.sub(r"\b(image|photo|video)\s*\d+\b", "", question)

    # Remove generic "video" keyword
    question = re.sub(r"\bvideo\b", "", question)

    # Remove question words
    question = re.sub(r"\b(what|when|where|who)\b", "", question)

    # Remove common question phrases
    for phrase in [
        "when did you see",
        "when have you seen",
        "can you see",
        "do you see",
        "did you see",
        "is there",
        "was there",
        "what is in",
        "what's in"
    ]:
        question = question.replace(phrase, "")

    # Remove filler words
    question = re.sub(r"\b(a|the|any)\b", "", question)

    # Remove weak positional words that break matching
    noise_words = ["in", "on", "at", "of"]
    words = [w for w in question.split() if w not in noise_words]

    # Final cleaned object string
    cleaned = " ".join(words).strip()

    return cleaned


def vision_describe(user_question=None):
    global last_seen_caption, vision_history

    try:
        start_total = time.time()

        print("Capturing image...")
        t0 = time.time()
        image_path = camera.capture_for_vision()
        t_capture = time.time() - t0

        print("Running vision model...")

        t1 = time.time()

        logger.set_model(vision_model.MODE)
        logger.set_mode("vision_live")

        caption = vision_model.describe(image_path)

        # Logs inference time only
        logger.log_vision(time.time() - t1)

        # Validate output before processing
        if not caption or not isinstance(caption, str):
            return "Vision failed."

        caption = caption.lower()
        t_model = time.time() - t1

        # Save result into short-term memory
        last_seen_caption = caption

        vision_history.append({
            "caption": caption,
            "time": datetime.now().strftime("%H:%M"),
            "path": image_path
        })

        # Optional memory integration
        try:
            memory.add("[LIVE VISION]", caption)
        except:
            pass

        # Description mode
        if (
            user_question is None or
            any(x in user_question.lower() for x in [
                "what do you see",
                "what can you see",
                "look around",
                "describe",
                "scan area",
                "what is in front of me"
            ])
        ):
            total = time.time() - start_total
            print(f"[VISION] capture={t_capture:.2f}s model={t_model:.2f}s total={total:.2f}s")
            return f"I see: {caption}"

        # Object query mode (yes/no)
        obj = extract_object(user_question)

        if not obj:
            return f"I see: {caption}"

        # Simple substring match (not semantic)
        if obj in caption:
            answer = f"Yes, I can see {obj}."
        else:
            answer = f"No, I cannot see {obj}."

        total = time.time() - start_total
        print(f"[VISION] capture={t_capture:.2f}s model={t_model:.2f}s total={total:.2f}s")

        return answer

    except Exception as e:
        # Any failure in capture or model returns generic error
        return f"Vision error: {e}"

def describe_saved_image(data):
    global last_seen_caption, vision_history

    # data is expected as (image_id, user_question)
    image_id, user_question = data

    media = get_media(image_id, "image")

    if not media:
        return f"Image {image_id} not found."

    # Opens image asynchronously for user context (non-blocking)
    try:
        open_file_async(media["path"], duration=4)
    except:
        pass

    logger.set_model(vision_model.MODE)
    logger.set_mode("vision")

    caption = vision_model.describe(media["path"]).lower()

    # Save into memory and history
    last_seen_caption = caption

    vision_history.append({
        "caption": caption,
        "time": datetime.now().strftime("%H:%M"),
        "path": media["path"]
    })

    try:
        memory.add(f"[IMAGE {image_id}]", caption)
    except:
        pass

    # Full description if no question provided
    if not user_question:
        return f"Image {image_id}: {caption}"

    question = user_question.lower()
    obj = extract_object(question)

    # Yes/No question handling
    yes_no_triggers = [
        "can you see",
        "do you see",
        "did you see",
        "is there",
        "was there"
    ]

    if any(t in question for t in yes_no_triggers) and obj:
        if obj in caption:
            return f"Yes, I can see {obj}."
        else:
            return f"No, I cannot see {obj}."

    # Description triggers
    description_triggers = [
        "what do you see",
        "what can you see",
        "what is in",
        "what's in",
        "describe"
    ]

    if any(t in question for t in description_triggers):
        return f"Image {image_id}: {caption}"

    # Default fallback
    return f"Image {image_id}: {caption}"


def describe_last_image(user_question):
    global last_seen_caption, vision_history

    question = user_question.lower().strip()

    # Automatically re-open last seen image if available
    if vision_history:
        last = vision_history[-1]
        try:
            open_file_async(last["path"], duration=4)
        except:
            pass

    # Direct recall
    if "what did you see" in question:
        if not last_seen_caption:
            return "I haven't seen anything yet."
        return f"I saw: {last_seen_caption}"

    # Object search across history
    obj = extract_object(question)

    if not obj:
        return "I couldn't understand the object."

    matches = []

    # Linear search (can grow over time)
    for item in vision_history:
        if obj in item["caption"]:
            matches.append(item)

    if matches:
        latest = matches[-1]
        return f"Yes, I saw {obj} at {latest['time']}."
    else:
        return f"No, I have not seen {obj} before."

def find_object_time(obj):
    global vision_history

    obj = obj.lower().strip()

    matches = []

    for item in vision_history:
        if obj in item["caption"]:
            matches.append(item)

    if matches:
        latest = matches[-1]
        return latest["time"]

    return None


def describe_saved_video(data):
    # data is expected as (video_id, user_question)
    video_id, user_question = data

    logger.set_model(vision_model.MODE)
    logger.set_mode("vision_video")

    media = get_media(video_id, "video")
    if not media:
        return f"Video {video_id} not found."

    path = media["path"]

    result = VisionResult()

    # Run vision processing in separate thread to overlap with playback
    def run_vision():
        try:
            result.caption = describe_video(path)
        except Exception as e:
            result.error = str(e)

    t = threading.Thread(target=run_vision)
    t.start()

    # Blocking video playback (user watches while processing happens)
    open_video(path)

    # Wait for vision processing to complete
    t.join()

    print("[DEBUG] result.caption =", result.caption)
    print("[DEBUG] result.error =", result.error)

    if result.error:
        return f"Vision error: {result.error}"

    if not result.caption or len(result.caption.strip()) == 0:
        return "Vision produced no usable result."

    caption = result.caption.lower()

    # Splitting by space limits matching accuracy
    captions_list = caption.split(" ")

    question = (user_question or "").lower()

    # Command-style queries (just play/open)
    if any(x in question for x in ["open video", "play video"]):
        return f"Video {video_id}: {caption}"

    # Yes/No query
    obj = extract_object(question)

    if obj:
        # Weak matching: substring inside words
        if any(obj in word for word in captions_list):
            return f"Yes, I can see {obj}."
        else:
            return f"No, I cannot see {obj}."

    # Default fallback
    return f"Video {video_id}: {caption}"
