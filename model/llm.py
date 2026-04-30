import requests
import time
from model.chat_memory import memory
from logs.logger import logger


class LLM:
    def __init__(self, logger):
        """
        mode:
            "local": uses Ollama
            "cloud": uses Groq
        """

        self.mode = "cloud"

        # LOCAL (OLLAMA)
        #self.LOCAL_MODEL = "gemma:2b-instruct"
        #self.LOCAL_MODEL = "phi3:mini"
        self.LOCAL_MODEL = "qwen2:1.5b"
        self.LOCAL_URL = "http://localhost:11434/api/chat"

        # CLOUD (GROQ)
        self.CLOUD_MODEL = "llama-3.1-8b-instant"

        self.logger = logger
        self.cache = {}

    def chat(self, user_input):
        start = time.time()

        self.logger.set_mode("llm")

        u = user_input.lower().strip()

        # Fast path for trivial greetings (avoids unnecessary LLM calls)
        if u in ["hi", "hello"]:
            return "Hello."

        # Cache to avoid repeated latency on identical inputs
        if u in self.cache:
            return self.cache[u]

        # Memory control logic
        context = ""

        # Explicit memory request, full history
        if any(word in u for word in ["before", "last", "previous", "you said"]):
            context = memory.get_context(mode="full")

        # Implicit relevance, nly recent context
        elif memory.is_relevant(user_input):
            context = memory.get_context(limit=1)

        # System prompt defining strict response behavior
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a voice assistant.\n"
                    "Answer in exactly 2 short sentences.\n"
                    "Each sentence must be under 12 words.\n"
                    "Speak naturally like talking to a person.\n"
                    "Do not give long explanations.\n"
                    "Do not list multiple examples.\n"
                    "Always finish your sentence completely.\n"
                    "Keep answers simple, clear, and engaging.\n"
                )
            }
        ]

        # Add memory context only if needed
        if context:
            messages.append({
                "role": "system",
                "content": f"Conversation history:\n{context}"
            })

        messages.append({
            "role": "user",
            "content": user_input
        })

        try:
            # mode switch
            if self.mode == "cloud":
                from groq import Groq

                self.logger.set_model(self.CLOUD_MODEL)

                client = Groq(api_key="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")

                completion = client.chat.completions.create(
                    model=self.CLOUD_MODEL,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=100
                )

                answer = completion.choices[0].message.content.strip()

            else:
                #ocal model (Ollama)
                self.logger.set_model(self.LOCAL_MODEL)

                res = requests.post(self.LOCAL_URL, json={
                    "model": self.LOCAL_MODEL,
                    "messages": messages,
                    "stream": False,
                    "keep_alive": "5m",
                    "options": {
                        "num_predict": 100,
                        "temperature": 0.3,
                        "num_ctx": 512,
                        "num_thread": 4,
                        "num_batch": 8
                    }
                })

                data = res.json()
                answer = data.get("message", {}).get("content", "").strip()

                if not answer:
                    return "Error"

            # Log latency for performance tracking
            latency = time.time() - start
            self.logger.log_llm(latency)
            print(f"LLM CHAT LATENCY: {latency:.3f}s")

            # Hard filter to remove useless model disclaimers
            bad_patterns = [
                "i don't have access",
                "i am unable",
                "i cannot",
                "i'm unable",
                "as an ai",
            ]

            if any(p in answer.lower() for p in bad_patterns):
                return "I'm not sure."

            # Save useful responses into memory
            if "i'm not sure" not in answer.lower():
                memory.add(user_input, answer)

            # Cache response
            self.cache[u] = answer

            return answer

        except Exception as e:
            print("LLM ERROR:", e)
            return "Error"
