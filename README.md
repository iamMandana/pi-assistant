# AI-Voice-Assistant-on-Raspberry-Pi-5-with-Tool-Execution-and-Vision-Capabilities

Real-time voice assistant with offline speech recognition, vision, and tool execution, designed for edge deployment.

---

## Quick Start (Recommended)

```bash
git clone https://github.com/YOUR_USERNAME/voice-assistant.git
cd voice-assistant

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python main.py

---

## Features
```markdown
- Wake word detection + speech interaction
- Offline speech-to-text (Vosk)
- Text-to-speech (Piper)
- Vision-based scene description
- Tool execution (camera, WiFi, notes, system info)
- Local + cloud LLM support
- Modular architecture

## Hardware Requirements
- Raspberry Pi 5 (8GB recommended)
- Camera Module
- Microphone
- Speaker

## Installation

sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    python3-pip python3-venv \
    portaudio19-dev python3-pyaudio \
    ffmpeg vlc feh iwlist alsa-utils \
    libatlas-base-dev libopenblas-dev \
    python3-picamera2


### Download Models
mkdir -p models

# Vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 models/vosk

# Piper
mkdir -p models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx -P models/piper/
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json -P models/piper/

## Configuration

GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

### LLM Mode

In model/llm.py:
self.mode = "local"   # offline
# self.mode = "cloud" # better quality

### Vision Mode
In vision/vision.py:
self.MODE = "blip_base"      # local
# self.MODE = "gemini_cloud" # cloud

## Usage

Run:
python main.py

Example commands:
- "Hey Pi, what do you see?"
- "Hey Pi, take a picture"
...

## 🧠 System Architecture

(Add your diagram image here)

## Project Structure

audio/        # STT, TTS, wake word
model/        # LLM + memory
vision/       # vision models
actions/      # tools
controller/   # routing logic
main.py       # entry point

## 📄 License
MIT License
