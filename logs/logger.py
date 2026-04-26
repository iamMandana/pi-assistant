import csv
import os
import time
from datetime import datetime

# CSV file used to store full system interaction metrics
LOG_FILE = "logs/system_metrics_full.csv"

# Ensure logs directory exists before writing
os.makedirs("logs", exist_ok=True)


# Initialize CSV file with header if it does not exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "event",
            "user_input",
            "assistant_response",
            "tool_used",
            "model_used",
            "mode",
            "stt_time",
            "vision_time",
            "llm_time",
            "tts_time",
            "total_time"
        ])


class SystemLogger:
    def __init__(self):
        # Initialize per-interaction state
        self.reset()

    def reset(self):
        # Marks start of a new interaction
        self.start_time = time.time()

        # Context fields
        self.user_input = ""
        self.response = ""
        self.tool_used = ""

        # Metadata about execution path
        self.model_used = "unknown"
        self.mode = "default"

        # Timing metrics (seconds)
        self.stt_time = 0
        self.vision_time = 0
        self.llm_time = 0
        self.tts_time = 0

    # Context setters used across system pipeline
    def set_input(self, text):
        self.user_input = text

    def set_response(self, text):
        self.response = text

    def set_tool(self, tool_name):
        self.tool_used = tool_name

    def set_model(self, model_name):
        self.model_used = model_name

    def set_mode(self, mode_name):
        self.mode = mode_name

    # Timing setters
    def log_stt(self, t): self.stt_time = t
    def log_vision(self, t): self.vision_time = t
    def log_llm(self, t): self.llm_time = t
    def log_tts(self, t): self.tts_time = t

    def save(self, event="interaction"):
        # Compute total time since last reset
        total_time = time.time() - self.start_time

        # Append a new row to CSV log
        with open(LOG_FILE, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                event,
                self.user_input,
                self.response,
                self.tool_used,
                self.model_used,
                self.mode,
                round(self.stt_time, 3),
                round(self.vision_time, 3),
                round(self.llm_time, 3),
                round(self.tts_time, 3),
                round(total_time, 3)
            ])


# Global logger instance shared across system
logger = SystemLogger()
