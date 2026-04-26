import json
import os

# File used to persist user notes
NOTES_FILE = "data/notes.json"


def write_note(content):
    # Reject empty or missing note content
    if not content:
        return "No note content provided."

    notes = []

    # Load existing notes if file exists
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            notes = json.load(f)

    # Append new note to in-memory list
    notes.append(content)

    # Overwrite file with updated notes list
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f)

    return "Note saved."


def read_notes():
    # Return message if notes file does not exist
    if not os.path.exists(NOTES_FILE):
        return "No notes found."

    with open(NOTES_FILE, "r") as f:
        notes = json.load(f)

    # Handle empty note list
    if not notes:
        return "No notes found."

    # Join notes into a single string for output
    return " | ".join(notes)
