# AI Voice Assistant on Raspberry Pi 5

A fully offline-capable voice assistant for Raspberry Pi 5 with vision, conversation, and system tools.

---

## Table of Contents

- [Features](#features)
- [Hardware Required](#hardware-required)
- [Installation](#installation)
  - [1. Clone the Repo](#1-clone-the-repo)
  - [2. System Dependencies](#2-system-dependencies)
  - [3. Python Environment](#3-python-environment)
  - [4. Install Python Packages](#4-install-python-packages)
  - [5. Download Models](#5-download-models)
- [Configuration](#configuration)
  - [Vision Model Selection](#vision-model-selection)
  - [LLM Selection (Local vs Cloud)](#llm-selection-local-vs-cloud)
- [Contact](#contact)

---

## Features

- **Wake Word Detection** – "Hey Pi" activates the assistant
- **Speech-to-Text** – Offline Vosk model converts speech to text
- **Text-to-Speech** – Piper TTS reads responses aloud
- **Computer Vision** – Describe what the camera sees in real time
- **Photo & Video Capture** – Take pictures and record video with auto-indexing
- **Saved Media Description** – Ask questions about previously captured images/videos
- **Vision Memory** – Ask "when did you see X?" to search past observations
- **WiFi Scanning** – List available networks
- **Public IP Lookup** – Get your public IP address
- **Notes** – Write and read persistent notes
- **System Health** – Read CPU temperature and free disk space
- **Calculator** – Simple spoken math like "15 times 3"
- **Conversational AI** – General chat with LLM (local via Ollama or cloud via Groq)
- **Performance Logging** – All interactions logged to CSV with timing metrics

---

## Hardware Required

| Component | Details |
|-----------|---------|
| **Board** | Raspberry Pi 5 (8GB RAM) |
| **Storage** | 64GB microSD card (or larger) |
| **Camera** | Raspberry Pi Camera Module 3 |
| **Microphone** | Bluetooth microphone |
| **Speaker** | Bluetooth speaker |
| **Optional** | Active cooling fan/case for sustained LLM use |

---

## Installation

### 1. Clone the Repo

```bash
git clone https://github.com/iamMandana/pi-assistant/

cd pi-assistant
```

### 2. System Dependencies
Run these commands on your Raspberry Pi 5:

```bash
sudo apt update && sudo apt upgrade -y

# Audio and media
sudo apt install -y \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    vlc \
    feh \
    alsa-utils \
    wireless-tools

# Python build tools 
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libatlas-base-dev \
    libopenblas-dev \
    libcap-dev

# Picamera2 (Raspberry Pi OS Bookworm)
sudo apt install -y python3-picamera2

# Piper TTS binary
wget https://sourceforge.net/projects/piper-tts.mirror/files/v1.0.0/piper_arm64.tar.gz/download -O piper_arm64.tar.gz
tar -xzf piper_arm64.tar.gz
sudo cp piper/piper /usr/local/bin/
rm -rf piper piper_arm64.tar.gz
```

### 3. Python Environment
Always activate the virtual environment with source venv/bin/activate before running the assistant or installing packages.

```bash
# Create virtual environment
python3 -m venv venv --system-site-packages

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```
### 4. Install Python Packages
```bash
pip install -r requirements.txt
```
Important:
This project relies on system-installed NumPy for compatibility with Picamera2 and simplejpeg.

Do NOT install or upgrade NumPy using pip, as this can cause binary incompatibility errors.
If issues occur, run:
```bash
    pip uninstall numpy
```    
### 5. Download Models
Vosk (Speech-to-Text)
``` bash
mkdir -p models

# Download small English model (~40 MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
mv vosk-model-small-en-us-0.15 models/vosk
rm vosk-model-small-en-us-0.15.zip
```

Piper (Text-to-Speech)
```bash
mkdir -p models/piper

# Download voice model
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx \
    -P models/piper/

wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json \
    -P models/piper/
```

---

## Configuration
### Vision Model Selection
Open vision/vision.py and find the __init__ method of VisionModel. Uncomment one mode:
```python
class VisionModel:
    def __init__(self):
        # choose one model
        
        # Local – BLIP Base (fast, low RAM)
        self.MODE = "blip_base"
        
        # Local – BLIP Large (better accuracy, slower, more RAM)
        # self.MODE = "blip_large"
        
        # Local – GIT Base (alternative model)
        # self.MODE = "git_base"
        
        # Cloud – Google Gemini (best accuracy, needs internet + API key)
        # self.MODE = "gemini_cloud"
```
If you choose cloud:
Create a .env file in the project root:
```bash
nano .env
```
Add:
```bash
# Only needed if using gemini_cloud vision mode
GOOGLE_API_KEY=your_actual_gemini_api_key
```

### LLM Selection (Local vs Cloud)
Open model/llm.py and find:

```python
class LLM:
    def __init__(self, logger):
        # choose one
        
        # cloud – uses Groq API (fast, needs internet + API key)
        self.mode = "cloud"
        
        # Local – uses Ollama (offline, runs on Pi)
        # self.mode = "local"
```
If you choose LOCAL:

1. Install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```
2. Pull a lightweight model:

```bash
ollama pull qwen2:1.5b
# Alternatives: phi3:mini, gemma:2b-instruct, tinyllama
```
3. Update model name in model/llm.py:

```python
self.LOCAL_MODEL = "qwen2:1.5b"   # Change to your model
```

If you choose CLOUD:

1.Sign up at console.groq.com

2.Generate an API key

In model/llm.py, find this line and replace with your key:

```python
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")
```

---

## Contact
Mandana Bakhshi

Email: bakhshi.m2004@gmail.com

For bugs, feature requests, or questions, please contact me.




