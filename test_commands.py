import sys
import time
from core.assistant import assistant

commands = [
    "increase volume",
    "set brightness to 70",
    "enable wifi",
    "disable bluetooth",
    "open app chrome",
]

for cmd in commands:
    print(f"\n--- Executing: {cmd} ---")
    resp = assistant.process_text_command(cmd)
    print("Response:", resp.model_dump())
    # small pause to allow TTS thread to process
    time.sleep(1)

print("\nAll commands executed.")

