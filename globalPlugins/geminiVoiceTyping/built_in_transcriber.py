import os
import time
import json
import base64
import ctypes
import threading
import urllib.request
import urllib.error

# For NVDA tones and UI
try:
    import core
    import tones
    import ui
    from .text_injector import paste_text
    from .config import config
    _in_nvda = True
except ImportError:
    _in_nvda = False

winmm = ctypes.windll.winmm

def mci_send_string(command):
    winmm.mciSendStringW(command, None, 0, None)

class BuiltInTranscriber:
    def __init__(self):
        self.api_keys = []
        self.current_key_idx = 0
        self.recording = False
        self.temp_file = os.path.join(os.environ.get("TEMP", "C:\\"), "nvda_gemini_recording.wav")
        self.mode = "normal"

    def get_api_key(self):
        from .config import config
        raw_keys = config.get_api_keys_csv()
        keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        if not keys:
            return None
        if self.current_key_idx >= len(keys):
            self.current_key_idx = 0
        return keys[self.current_key_idx]

    def _rotate_key(self):
        from .config import config
        raw_keys = config.get_api_keys_csv()
        keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        if keys:
            self.current_key_idx = (self.current_key_idx + 1) % len(keys)
            
            if _in_nvda and config.get("beep_on_key_rotation", False):
                core.callLater(0, tones.beep, 800, 50)
                core.callLater(100, tones.beep, 800, 50)

    def start(self, mode="normal"):
        if self.recording:
            return
        
        self.mode = mode
        
        # Audio setup via winmm
        mci_send_string("close all")
        mci_send_string("open new type waveaudio alias recsound")
        mci_send_string("set recsound alignment 2 bitspersample 16 samplespersec 16000 channels 1")
        mci_send_string("record recsound")
        
        self.recording = True
        
        if _in_nvda:
            core.callLater(0, tones.beep, 1800, 60) # Ready beep

    def commit(self):
        # In built-in mode, committing stops recording and fires API
        if not self.recording:
            return
            
        mci_send_string("stop recsound")
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass
        mci_send_string(f'save recsound "{self.temp_file}"')
        mci_send_string("close recsound")
        self.recording = False
        
        if _in_nvda:
            core.callLater(0, tones.beep, 400, 80) # Stop beep
            
        threading.Thread(target=self._process_audio, daemon=True).start()

    def stop(self):
        if self.recording:
            self.commit()

    def _process_audio(self):
        from .config import config
        api_key = self.get_api_key()
        if not api_key:
            if _in_nvda:
                core.callLater(0, ui.message, "No API key configured.")
            return

        if not os.path.exists(self.temp_file):
            return

        with open(self.temp_file, "rb") as f:
            audio_data = f.read()

        if len(audio_data) < 1000: # Too short
            if _in_nvda:
                core.callLater(0, ui.message, "Audio too short or failed to record.")
            return

        b64_audio = base64.b64encode(audio_data).decode("utf-8")

        model = config.get("llm_model", "gemini-2.5-flash")
        
        # Always use smart mode prompt for built-in, because it's a batch request
        prompt = config.get("system_prompt_smart", "")
        if not prompt:
            prompt = "Transcribe exactly what you hear."

        payload = {
            "system_instruction": {
                "parts": [{"text": prompt}]
            },
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "audio/wav",
                                "data": b64_audio
                            }
                        },
                        {
                            "text": "Transcribe the audio exactly. Output ONLY the transcription."
                        }
                    ]
                }
            ]
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        while True:
            try:
                req = urllib.request.Request(url, method="POST", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    
                text = ""
                if "candidates" in res_data and len(res_data["candidates"]) > 0:
                    parts = res_data["candidates"][0]["content"].get("parts", [])
                    if len(parts) > 0:
                        text = parts[0].get("text", "").strip()
                
                if text and _in_nvda:
                    is_stealth = not config.get("copy_to_clipboard", False)
                    core.callLater(0, paste_text, text, stealth=is_stealth)
                else:
                    if _in_nvda:
                        core.callLater(0, ui.message, "No text returned from Gemini.")
                break # Success
                
            except urllib.error.HTTPError as e:
                err_text = e.read().decode('utf-8')
                if e.code == 429 or "quota" in err_text.lower() or "exhausted" in err_text.lower():
                    # Rate limit, try next key
                    self._rotate_key()
                    new_key = self.get_api_key()
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={new_key}"
                else:
                    if _in_nvda:
                        core.callLater(0, tones.beep, 200, 150)
                        core.callLater(50, ui.message, f"API Error: {e.code} - {err_text[:50]}")
                    break
            except Exception as e:
                if _in_nvda:
                    core.callLater(0, tones.beep, 200, 150)
                    core.callLater(50, ui.message, f"Connection Error: {str(e)}")
                break

built_in_transcriber_instance = BuiltInTranscriber()
