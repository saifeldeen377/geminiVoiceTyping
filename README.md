# Gemini Voice Typing for NVDA

Ultra-fast, real-time speech-to-text dictation add-on for the NVDA screen reader powered by Google Gemini Live API. 
Specifically tuned for highly accurate bilingual (Arabic & English) voice typing.

---

## Features

- **Real-Time Dictation**: Streams audio directly to Gemini Live API and injects transcribed words into the active field as you speak.
- **Stealth Paste Mode**: Injects text with extreme speed and accuracy using a smart clipboard bypass. It respects clipboard managers (like ClipHistory and Windows Win+V) by temporarily hiding the text so it never pollutes your clipboard history! This is the default behavior, but you can opt to copy text to your clipboard in the settings.
- **Multilingual Excellence**: Effortlessly switches between languages. It is heavily tuned to follow strict Arabic spelling rules. You can seamlessly mix Arabic and English in the same sentence.
- **Multi-Key Failover**: Put multiple Gemini API keys separated by commas (e.g. key1, key2, key3). If a key hits a rate limit or runs out of quota (HTTP 429), the add-on automatically switches to the next key without interrupting your workflow.
- **Accessible Earcons / Audio Feedback**:
  - High ascending chime when listening starts.
  - Descending chime when listening stops.
  - Optional double-tone when an API key is automatically rotated (configurable in settings).
  - Low error beep if an issue occurs.
- **Universal Compatibility**: Works across all text fields, editors, and Windows apps without restricting where you can type.

---

## Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| NVDA + Shift + G | Start / Stop Voice Typing |

*(You can also customize the shortcut in **NVDA Menu -> Preferences -> Input Gestures -> Gemini Voice Typing**)*

---

## Setup & Configuration

1. Open NVDA Settings: Press NVDA + N, then go to **Preferences -> Settings**.
2. Navigate to **Gemini Voice Typing** in the categories list.
3. In **Gemini API Keys**, enter one or more API keys separated by commas (e.g. AIzaSy..., AIzaSy...).
4. (Optional) Enable the checkbox to play a double-beep sound when automatically switching to another API key.
5. (Optional) Enable "Auto copy result to clipboard" if you want your dictated text to be saved in your clipboard manager's history.
6. Click **OK** to save.