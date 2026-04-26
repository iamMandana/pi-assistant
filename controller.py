from model.llm import LLM
from tools import TOOLS
from parser import parse_command
from logs.logger import logger
from actions.vision_tools import extract_object, find_object_time

# Initialize main language model with logger dependency
model = LLM(logger)


def is_valid_chat(text):
    # Normalize input for consistent processing
    t = text.lower().strip()
    words = t.split()

    # Reject extremely short inputs (likely noise or incomplete)
    if len(words) <= 1:
        return False

    # Allow clear question formats
    question_words = ["what", "why", "how", "who", "where", "when"]
    if any(t.startswith(q) for q in question_words):
        return True

    # Allow natural conversational requests
    natural_requests = [
        "can you", "could you", "would you",
        "please", "i need", "i want",
        "help me", "tell me", "show me"
    ]
    if any(x in t for x in natural_requests):
        return True

    # Allow general multi-word inputs
    if len(words) >= 2:
        return True

    # Reject vague or low-information inputs
    vague_patterns = [
        "do something",
        "anything",
        "whatever",
        "you decide",
        "something",
        "random",
        "we censor",
        "is therefore"
    ]
    if any(v in t for v in vague_patterns):
        return False

    # Default allow (fallback behavior)
    return True    

    
def handle_input(user_text):
    # Store raw input for logging and traceability
    logger.set_input(user_text)

    # Preprocess input for lightweight checks
    u = user_text.lower().strip()

    # First stage routing: parse command before any LLM usage
    action, args = parse_command(user_text)

    # Special-case handling for memory-based vision queries
    # This bypasses TOOLS and directly uses vision memory functions
    if action == "when_seen":
        logger.set_tool(action)

        obj = extract_object(user_text)
        if not obj:
            return "I couldn't understand the object."

        time_seen = find_object_time(obj)

        if time_seen:
            return f"I saw {obj} at {time_seen}."
        else:
            return f"I have not seen {obj}."

    # Primary tool execution path
    # If parser detects an action, execute it without involving LLM
    if action:
        print("DEBUG: DIRECT PARSE", action)
        logger.set_tool(action)

        # Vision tool uses a different logging mode
        if action == "vision_describe":
            logger.set_mode("vision")
        else:
            logger.set_model("tool")
            logger.set_mode("tool")

        try:
            # vision_describe expects full user text
            # other tools expect parsed arguments
            if action == "vision_describe":
                result = TOOLS[action](user_text)
            else:
                result = TOOLS[action](args)
        except Exception as e:
            # Catch tool failures to prevent system crash
            result = f"Tool error: {e}"

        return result

    # Handle very short inputs separately to avoid unnecessary LLM calls
    if len(u.split()) <= 2:
        casual = [
            "hi", "hello", "hey",
            "thanks", "thank you",
            "ok", "okay", "cool"
        ]

        # Allow simple conversational responses
        if u in casual:
            print("DEBUG: SHORT CASUAL CHAT")

            logger.set_model("LLM")
            logger.set_mode("chat")

            return model.chat(user_text)

        # Block unclear short inputs
        print("DEBUG: SHORT INPUT BLOCKED")

        logger.set_model("none")
        logger.set_mode("clarification")
        logger.save(event="clarification")

        return "Please say more clearly."

    # Validate input before sending to LLM
    # Prevents low-quality or vague queries from reaching the model
    if not is_valid_chat(user_text):
        print("DEBUG: REJECTED CHAT")

        logger.set_model("none")
        logger.set_mode("rejected_chat")

        return "I didn't understand. Please say it more clearly."

    # Default path: send to LLM for general conversation
    print("DEBUG: DIRECT CHAT")

    logger.set_model("LLM")
    logger.set_mode("chat")

    return model.chat(user_text)

    command_words = [
        "take", "capture", "record", "photo", "picture",
        "video", "image", "camera", "time", "ip", "wifi"
    ]

    if any(w in user_text.lower() for w in command_words):
        logger.set_model("none")
        logger.set_mode("clarification")

        return "Please say the command clearly."

    print("DEBUG: NORMAL FALLBACK")

    logger.set_model("LLM")
    logger.set_mode("fallback")

    return model.chat(user_text)
