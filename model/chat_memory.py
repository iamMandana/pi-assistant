class ChatMemory:
    def __init__(self, max_turns=10):
        # Stores conversation
        self.history = []

        # Maximum number of turns to keep
        self.max_turns = max_turns

    def add(self, user, assistant):
        # Add a new interaction pair to memory
        self.history.append((user, assistant))

        # Maintain fixed memory size
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_context(self, limit=None, mode="recent"):
        # Returns formatted conversation history as a single string
        if not self.history:
            return ""

        # Full history override
        if mode == "full":
            history = self.history

        # Limit to last N turns if specified
        elif limit:
            history = self.history[-limit:]

        # Default: return all stored history
        else:
            history = self.history

        # Convert history into LLM-friendly text format
        context = ""
        for u, a in history:
            context += f"User: {u}\nAssistant: {a}\n"

        return context.strip()

    def has_topic(self, topic):
        # Checks if a keyword appears anywhere in stored conversation
        topic = topic.lower()

        # Flatten history into one string
        text = " ".join([f"{u} {a}" for u, a in self.history]).lower()

        return topic in text

    def clear(self):
        # Completely resets memory
        self.history = []

    def is_relevant(self, user_input, threshold=1):
        # Simple relevance check based on word overlap with last turn
        user_words = set(user_input.lower().split())

        if not self.history:
            return False

        # Only compares against the most recent interaction
        last_user, last_assistant = self.history[-1]

        memory_text = (last_user + " " + last_assistant).lower()
        memory_words = set(memory_text.split())

        # Compute shared words between current input and last memory
        overlap = user_words.intersection(memory_words)

        # Returns True if overlap meets threshold
        return len(overlap) >= threshold


# Global shared memory instance
memory = ChatMemory()
