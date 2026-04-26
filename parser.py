import re


def words_to_numbers(text):
    # Maps spoken number words to numeric values
    units = {
        "zero": 0, "one": 1, "two": 2, "to": 2, "three": 3,
        "four": 4, "for": 4, "five": 5, "six": 6,
        "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16,
        "seventeen": 17, "eighteen": 18, "nineteen": 19
    }

    tens = {
        "twenty": 20, "thirty": 30, "forty": 40,
        "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90
    }

    # Normalize text and split into tokens
    words = text.lower().replace("-", " ").split()
    result = []

    i = 0
    while i < len(words):
        word = words[i]

        # Handle compound numbers like "twenty one"
        if word in tens:
            num = tens[word]
            if i + 1 < len(words) and words[i + 1] in units:
                num += units[words[i + 1]]
                i += 1
            result.append(str(num))

        elif word in units:
            result.append(str(units[word]))

        else:
            # Keep non-number words unchanged
            result.append(word)

        i += 1

    return " ".join(result)


def normalize_math(text):
    # Converts natural language math into symbolic expressions
    text = text.lower()
    text = words_to_numbers(text)

    # Order matters here: multi-word phrases must be replaced before single words
    text = text.replace("plus", "+")
    text = text.replace("minus", "-")
    text = text.replace("times", "*")
    text = text.replace("multiplied by", "*")
    text = text.replace("divided by", "/")
    text = text.replace("percent of", "* 0.01 *")
    text = text.replace("percent", "* 0.01")
    text = text.replace("to the power of", "**")
    text = text.replace("power of", "**")

    return text


def is_math_expression(text):
    # Detects simple binary math expressions
    return bool(re.search(r"\d+\s*[\+\-\*/]\s*\d+", text))


def parse_command(user_input):
    # Normalize input once at the beginning for consistent matching
    u = user_input.lower().strip()

    # Basic typo correction for common STT errors
    u = u.replace("wifii", "wifi")
    u = u.replace("recrod", "record")
    u = u.replace("vedio", "video")
    u = u.replace("phote", "photo")

    # Normalize spoken numbers before any parsing
    u = words_to_numbers(u)

    # Math detection is placed first to avoid interference from other rules
    math_text = normalize_math(u)
    if is_math_expression(math_text):
        return "calculate", math_text

    # High-priority memory query (must come before general "did you see" logic)
    if re.search(r"\bwhen\s+(did|have)\s+you\s+see\b", u):
        return "when_seen", user_input

    # Camera trigger requires both action phrase and media keyword
    picture_keywords = [
        "take picture", "take photo", "take photos",
        "take a picture", "take pictures", "take a photo",
        "capture image", "capture photo",
        "capture a photo", "capture a picture",
        "snap photo", "snap picture",
        "click photo", "click picture",
        "please take", "please capture"
    ]

    if any(k in u for k in picture_keywords) and any(x in u for x in ["photo", "picture", "image"]):
        return "take_picture", None

    # Extract optional duration for video recording; default to 10 seconds
    video_keywords = [
        "record video", "start recording", "record a video",
        "capture video", "take video", "make a video"
    ]

    if any(k in u for k in video_keywords):
        match = re.search(r"(\d+)", u)
        duration = int(match.group(1)) if match else 10
        return "record_video", duration

    # Explicit "open" commands route to saved media description
    # Returns None if no ID is found to avoid incorrect tool execution
    if any(x in u for x in ["open image", "open photo", "open picture", "open video"]):
        match = re.search(r"(image|photo|picture|video)\s*(\d+)", u)
        if match:
            media_type = match.group(1)
            media_id = match.group(2)

            if media_type in ["image", "photo", "picture"]:
                return "describe_saved_image", (media_id, user_input)
            elif media_type == "video":
                return "describe_saved_video", (media_id, user_input)

        return None, None

    # Order is critical: image/video detection must come before generic vision or memory rules
    match = re.search(r"(image|photo)\s*(\d+)", u)
    if match:
        return "describe_saved_image", (match.group(2), user_input)

    video_match = re.search(r"(video)\s*(\d+)", u)
    if video_match:
        return "describe_saved_video", (video_match.group(2), user_input)

    # Memory query fallback (only if no specific image/video was referenced)
    if re.search(r"\b(did you see|was there|is there)\b", u) and "when" not in u:
        return "describe_last_image", user_input

    # Controlled vision triggers to avoid hijacking general questions
    vision_commands = [
        "look around",
        "what do you see",
        "what can you see",
        "scan area",
        "describe scene",
        "what is in front of me",
        "what's in front of me",
        "what is around me",
        "what's around me"
    ]

    if any(x in u for x in vision_commands):
        return "vision_describe", None

    # Regex allows flexible phrasing
    if re.search(r"\b(what|can|do)\b.*\bsee\b", u):
        return "vision_describe", None

    # Fallback vision trigger when user asks about presence without specifying media
    if any(x in u for x in ["can you see", "do you see", "is there"]) and "image" not in u and "video" not in u:
        return "vision_describe", user_input
    # System status queries
    if any(x in u for x in ["system health", "check system", "system status", "cpu usage", "device status"]):
        return "system_health", None

    # WiFi scanning commands
    if any(x in u for x in [
        "wifi list", "scan wifi", "show wifi",
        "available wifi", "list wifi",
        "check wifi", "network list"
    ]):
        return "wifi_scan", None

    # Public IP queries
    if any(x in u for x in ["my ip", "public ip", "ip address", "what is my ip"]):
        return "public_ip", None

    # Combined time and date handling
    if any(k in u for k in [
        "what time", "time now", "current time",
        "tell me the time", "what's the time",
        "what date", "today date", "current date",
        "what date is it", "what's the date",
        "tell me the date"
    ]):
        return "time_date", None

    # Note creation extracts remaining text after command phrases
    if any(x in u for x in [
        "write note", "right note", "rite note",
        "create note", "make a note", "add note",
        "save note", "store note"
    ]):
        content = u
        for p in ["write note", "right note", "rite note", "create note", "make a note", "add note", "save note", "store note"]:
            content = content.replace(p, "")
        content = content.strip()
        return "write_note", content if content else None

    # Note retrieval commands
    if any(x in u for x in [
        "read note", "read my note", "get note",
        "show note", "display note", "read notes", "read the notes", "read not",
    ]):
        return "read_note", None


    # Default fallback when no command is matched
    return None, None
