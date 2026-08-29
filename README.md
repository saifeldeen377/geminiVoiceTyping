# 🎙️ Gemini Voice Typing for NVDA

![NVDA Add-on](https://img.shields.io/badge/NVDA-Add--on-blue.svg)
![Version](https://img.shields.io/badge/version-1.8.9-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An ultra-fast, highly accurate multilingual speech-to-text dictation add-on for the NVDA screen reader, powered by Google's Gemini AI APIs.

Unlike traditional voice typing tools, **Gemini Voice Typing** uses advanced Large Language Models (LLMs) to not only transcribe your speech with zero latency, but also instantly fix grammar, spelling, and seamlessly handle complex multilingual code-switching (e.g., mixing Arabic and English in the same sentence).

---

## ✨ Key Features

- **🚀 Dual Transcription Engines:**
  - **Strict Live Mode (Zero Latency):** Streams audio directly to the gemini-3.5-transcribe-live API. Types instantly as you speak, word-by-word. Perfect for rapid dictation.
  - **Smart Batch Mode (Perfect Accuracy):** Uses gemini-3.5-flash-lite to record your sentence, then intelligently analyze and transcribe it upon pausing. Flawlessly formats text, corrects grammar, and stops transliteration errors dead in their tracks.
- **📝 Manual Commit Mode:** Take full control! Dictate freely in the background and only inject the text when you press Enter. Perfect for chatting and sending messages.
- **🧠 AI Grammar & Spelling Corrector:** Automatically cleans up your dictated text before pasting it.
- **🥷 Stealth Paste Mode:** Injects text with extreme speed without polluting your clipboard history (bypasses Windows Win+V and ClipHistory).
- **🔄 Multi-Key Failover:** Input multiple Gemini API keys separated by commas. If one runs out of quota, it instantly fails over to the next without dropping your dictation!
- **🎵 Accessible Audio Feedback:** Intuitive earcons (chimes) for starting, stopping, API key rotation, and errors.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| NVDA + Shift + G | **Start / Stop** Voice Typing |
| NVDA + Alt + Shift + G | **Toggle Model:** Switch between *Strict Live Mode* and *Smart Batch Mode* |
| NVDA + Alt + G | **Toggle Manual Mode:** Turn *Manual Commit Mode* on/off |
| NVDA + G | **Toggle Corrector:** Turn the *AI Grammar Corrector* on/off |

> **Note:** When *Manual Commit Mode* is active, use **Enter** or **Space** to paste the accumulated text, and **Escape** to cancel and clear the background buffer.

*(All shortcuts can be customized via **NVDA Menu -> Preferences -> Input Gestures -> Gemini Voice Typing**)*

---

## ⚙️ Setup & Configuration

1. Download the latest .nvda-addon file from the [Releases](https://github.com/saifeldeen377/geminiVoiceTyping/releases) page.
2. Install it in NVDA and restart NVDA.
3. Open NVDA Settings: Press NVDA + N, then go to **Preferences -> Settings**.
4. Navigate to **Gemini Voice Typing** in the categories list.
5. In **Gemini API Keys**, enter one or more API keys separated by commas. *(You can get a free API key from Google AI Studio).*
6. Customize your transcription modes and AI system prompts as desired.
7. Click **OK** to save.

---

## 💡 Best Practices for Multilingual Dictation

- **Pause Briefly:** For the best accuracy, speak in natural phrases and pause briefly (about 1 second) after each thought.
- **Wait for NVDA:** Wait until NVDA announces the pasted text before starting your next sentence to prevent audio overlapping.
- **Switching Modes:** If you change the model or corrector settings while the microphone is already active, you must stop and restart voice typing (NVDA + Shift + G) for the new AI prompts to take effect.

