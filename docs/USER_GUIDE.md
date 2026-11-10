# AURA – AI Desktop Assistant: User Guide & Command Reference

**Version:** 2.0  
**Target Platform:** Windows 11 (64-bit)  

---

## 1. Getting Started

### 1.1 Launching the Application
You can start AURA anytime in either of two ways:
- **Command Line:**
  ```powershell
  python main.py
  ```
- **Batch Script:**
  Double-click `run_aura.bat` in the project root.

---

## 2. Interaction Modes

### 2.1 Push-to-Talk (PTT)
- **Mouse Control:** Click and hold the large blue **"HOLD TO SPEAK"** button on the dashboard. Speak your instruction, then release the button to process and execute.
- **Global Hotkey:** Press `Ctrl+Shift+A` from anywhere on Windows to activate Push-to-Talk without bringing the window to the foreground.

### 2.2 Text Command Input
If you are in a quiet room or prefer typing:
- Use the quick command entry bar at the bottom of the Dashboard.
- Type any supported instruction (e.g., `set volume to 50`, `check battery`) and press <kbd>Enter</kbd>.

---

## 3. Supported Voice Commands Reference

| Category | Spoken Command Variations | System Action |
|---|---|---|
| **Volume Control** | • *"Set volume to 40 percent"*<br>• *"Change volume to 60"*<br>• *"Increase volume"* / *"Turn it up"*<br>• *"Decrease volume by 15"*<br>• *"Mute laptop"* / *"Unmute"* | Adjusts Windows master volume with verification. |
| **Brightness** | • *"Set brightness to 80 percent"*<br>• *"Make my screen brighter"*<br>• *"Dim the screen"* / *"Lower brightness"* | Adjusts primary display brightness. |
| **Applications** | • *"Open Chrome"*<br>• *"Launch Notepad"*<br>• *"Start VS Code"*<br>• *"Close Chrome"* / *"Close it"* | Launches whitelisted applications or sends graceful `WM_CLOSE`. |
| **Wi-Fi** | • *"Turn on Wi-Fi"*<br>• *"Disable Wi-Fi"*<br>• *"Wi-Fi status"* | Queries connection state or toggles adapter. |
| **Bluetooth** | • *"Turn on Bluetooth"*<br>• *"Disable Bluetooth"*<br>• *"Check Bluetooth status"* | Queries radio state or toggles service. |
| **System Utilities** | • *"Check battery"*<br>• *"Lock my workstation"* / *"Lock screen"*<br>• *"Take a screenshot"* | Queries battery level, locks Windows session, or saves screenshot. |

---

## 4. Strict Security & Safety Guarantees

### 4.1 System Power Protection (Shutdown / Restart)
- **Rule:** AURA is strictly prohibited from executing power-off, restart, reboot, or shutdown operations.
- **Trigger Examples:**
  - *"Shut down my computer"*
  - *"Restart the laptop"*
  - *"Power off"*
- **Guaranteed Response:**
  > *"I am not authorized to shut down or restart the system."*

### 4.2 Personal Files Protection
- **Rule:** AURA has zero access to user personal folders, document libraries, or filesystem browsing.
- **Trigger Examples:**
  - *"Open my personal documents"*
  - *"Read passwords.txt"*
  - *"Show files in my downloads"*
- **Guaranteed Response:**
  > *"I do not have access to personal files."*

---

## 5. Dashboard Features

- **Capability Permissions Panel:** In the **Permissions** tab, you can independently toggle any capability (Volume, Brightness, Application Launching, Wi-Fi, Bluetooth, System Utilities). Disabling a permission immediately blocks all subsequent commands for that action.
- **Activity History Panel:** In the **History** tab, review all past commands, execution outcomes (SUCCESS/FAILED), timestamps, and verification messages. Includes a **Clear History** button to purge logs.
- **Settings Panel:** Adjust speech synthesis speed (words per minute), switch Faster-Whisper recognition models, or enable/disable local Ollama LLM integration.

