# AURA – AI Desktop Assistant (Version 2.0)

A lightweight, permission-controlled, voice-driven AI desktop assistant for **Windows 11 (64-bit)** built with Python 3.11+.

AURA enables users to control laptop operations (volume, brightness, application launching, Wi-Fi, Bluetooth, battery query, workstation locking, and screenshot capture) through natural language voice commands.

Unlike unrestricted computer agents, AURA operates under a **strictly controlled execution model**:
- **Deterministic Action Registry:** The AI cannot execute arbitrary Python code or shell scripts.
- **Strict Power Prohibitions:** All shutdown and restart operations are permanently disabled.
- **Strict File Isolation:** AURA has zero tools or access to personal files, directories, or documents.
- **Result Verification:** System state is verified before any confirmation response is spoken.
- **Local-First & Offline:** Core commands work without internet connectivity.

---

## Architecture Overview

```
User Voice Command (Push-to-Talk)
          │
          ▼
   Audio Processor
          │
          ▼
 Speech Recognition (Faster-Whisper)
          │
          ▼
 Command Parser & Security Policy
 ├── Refuses Shutdown/Restart Commands
 └── Refuses Personal File Access
          │
          ▼
 Permission Manager & Schema Validator (Pydantic)
          │
          ▼
   Action Dispatcher
   ├── Volume Controller (pycaw)
   ├── Brightness Controller (screen-brightness-control)
   ├── Application Controller (Whitelisted aliases only)
   ├── Network Controller (Wi-Fi status/toggle)
   ├── Bluetooth Controller (Bluetooth radio)
   └── System Controller (Lock, Battery, Screenshot)
          │
          ▼
  Result Verification (Actual State Comparison)
          │
          ▼
Text-to-Speech Feedback (pyttsx3) & CustomTkinter UI
```

---

## Directory Structure

```text
AURA/
├── main.py                    # Application entry point
├── config.py                  # Configuration loader
├── requirements.txt           # Dependencies
├── docs/
│   ├── SRS.md                 # Software Requirements Specification
│   └── SDD.md                 # System Design Document
├── config/
│   ├── settings.json          # Preferences and model settings
│   ├── app_aliases.json       # Approved application aliases
│   └── authorized_actions.json# Capabilities definition
├── core/
│   ├── assistant.py           # Central coordinator
│   ├── state_manager.py       # Thread-safe state machine
│   └── event_manager.py       # GUI event bus
├── voice/
│   ├── microphone.py          # Sounddevice Push-to-Talk capture
│   ├── audio_processor.py     # In-memory audio normalization
│   ├── speech_recognition.py  # Faster-Whisper transcription
│   └── speech_response.py     # Non-blocking pyttsx3 speech queue
├── intelligence/
│   ├── command_parser.py      # Deterministic regex parser
│   ├── intent_classifier.py   # Intent routing
│   ├── context_manager.py     # Pronoun and reference resolution
│   └── ai_engine.py           # Optional Ollama integration
├── security/
│   ├── action_registry.py     # Authorized action whitelist
│   ├── security_policy.py     # Rejection of power & file commands
│   ├── request_validator.py   # Pydantic schemas
│   └── permission_manager.py  # Capability checks against SQLite
├── controllers/
│   ├── action_dispatcher.py   # Action routing & execution
│   ├── application_controller.py
│   ├── volume_controller.py
│   ├── brightness_controller.py
│   ├── wifi_controller.py
│   ├── bluetooth_controller.py
│   └── system_controller.py
├── platform/
│   ├── windows_audio.py       # Core Audio API adapter
│   ├── windows_display.py     # DDC/CI & WMI display adapter
│   ├── windows_network.py     # Wi-Fi netsh adapter
│   ├── windows_bluetooth.py   # Bluetooth service adapter
│   ├── windows_process.py     # Whitelist process launcher
│   └── windows_system.py      # Lock, Battery, Screenshot adapter
├── verification/
│   └── result_verifier.py     # Post-execution verification
├── database/
│   ├── database.py            # SQLite schema migrations
│   ├── models.py              # Pydantic database models
│   └── repositories.py        # Append-only logs & settings CRUD
├── interface/
│   ├── dashboard.py           # CustomTkinter dark-mode UI
│   ├── components.py          # Custom status badges and cards
│   ├── permissions_ui.py      # Dynamic capability toggles
│   ├── activity_history.py    # Log viewer & clearing tool
│   └── settings.py            # Speech & recognition preferences
└── tests/
    ├── unit/
    └── security/
```

---

## Installation & Setup

1. **Prerequisites:**
   - Windows 11 (64-bit)
   - Python 3.11+
   - Microphone and speakers

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run AURA:**
   ```bash
   python main.py
   ```

---

## Example Voice Commands

- **Volume:**
  - *"Set volume to 40 percent"*
  - *"Increase volume"*
  - *"Mute audio"* / *"Unmute"*
- **Brightness:**
  - *"Set brightness to 70 percent"*
  - *"Make my screen brighter"*
  - *"Dim the screen"*
- **Applications:**
  - *"Open Chrome"*
  - *"Open Notepad"*
  - *"Close Chrome"*
  - *"Open Paint"*
  - *"Open Windows Terminal"*
  - *"Open VLC media player"*
  - *"Open Settings"*
- **Connectivity:**
  - *"Wi-Fi status"*
  - *"Turn on Wi-Fi"* / *"Turn off Wi-Fi"*
  - *"Check Bluetooth"*
- **System Utilities:**
  - *"Check battery"*
  - *"Lock my screen"*
  - *"Take a screenshot"*

---

## Security Guarantees

1. **Power Shutdown Rejection:**
   - Command: *"Shut down my computer"* or *"Restart laptop"*
   - Response: *"I am not authorized to shut down or restart the system."*
2. **Personal File Rejection:**
   - Command: *"Open my documents"* or *"Search files for password"*
   - Response: *"I do not have access to personal files."*
3. **No Shell Injections:**
   - Subprocesses are invoked strictly as argument vectors with whitelisted executable binaries without `shell=True`.
