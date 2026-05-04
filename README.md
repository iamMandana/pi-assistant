# Pi Voice Assistant

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
  - [6. Enable Camera](#6-enable-camera)
- [Configuration](#configuration)
  - [Vision Model Selection](#vision-model-selection)
  - [LLM Selection (Local vs Cloud)](#llm-selection-local-vs-cloud)
  - [API Keys (Optional)](#api-keys-optional)
- [Usage](#usage)
  - [Start the Assistant](#start-the-assistant)
  - [Wake Word](#wake-word)
  - [All Commands](#all-commands)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contact](#contact)
- [License](#license)

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
git clone [https://github.com/YOUR_USERNAME/pi-voice-assistant.git](https://github.com/iamMandana/AI-Voice-Assistant-on-Raspberry-Pi-5-with-Tool-Execution-and-Vision-Capabilities)
cd pi-voice-assistant

### 2. **System Dependencies**


