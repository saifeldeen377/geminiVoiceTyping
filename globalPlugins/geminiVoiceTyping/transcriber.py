# -*- coding: utf-8 -*-
import os
import sys
import asyncio
import traceback
import warnings
import time

warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from google import genai
    from google.genai import types
except ImportError:
    pass

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    pass

SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SAMPLES = 1024
MODEL = "models/gemini-3.5-transcribe-live"

class Transcriber:
    def __init__(self, api_keys: list[str]):
        self.api_keys = api_keys
        self.session = None
        self.out_queue = None
        self.running = True
        self._stream = None
        
        self._current_text = ""
        self._flushed_text = ""
        self._last_update_time = time.time()

    def _audio_callback(self, indata, frames, time_info, status):
        if not self.running or self.out_queue is None:
            return
        pcm = (indata[:, 0] * 32767).astype(np.int16).tobytes()
        try:
            self.out_queue.put_nowait(pcm)
        except Exception:
            pass

    async def send_audio(self):
        while self.running:
            try:
                pcm_data = await asyncio.wait_for(self.out_queue.get(), timeout=0.3)
            except asyncio.TimeoutError:
                continue
            except Exception:
                break
            
            if self.session and self.running:
                try:
                    await self.session.send_realtime_input(
                        audio={"mime_type": "audio/pcm", "data": pcm_data}
                    )
                except Exception as e:
                    self._emit(f"ERROR:Audio send failed: {e}")
                    self.running = False
                    break

    async def watch_silence(self):
        while self.running:
            await asyncio.sleep(0.2)
            if self._current_text:
                if time.time() - self._last_update_time > 1.0:
                    self._flush_text()

    def _flush_text(self):
        if not self._current_text:
            return
            
        if self._current_text.startswith(self._flushed_text):
            diff = self._current_text[len(self._flushed_text):].strip()
            if diff:
                self._emit(f"TEXT:{diff} ")
        else:
            self._emit(f"TEXT:{self._current_text} ")
            
        self._flushed_text = self._current_text
        self._last_update_time = time.time() 

    async def receive_text(self):
        while self.running:
            if not self.session:
                await asyncio.sleep(0.1)
                continue
            try:
                turn = self.session.receive()
                async for response in turn:
                    if not self.running:
                        break
                    try:
                        sc = getattr(response, "server_content", None)
                        if not sc:
                            continue

                        interim = getattr(sc, "interim_input_transcription", None)
                        if interim:
                            t = getattr(interim, "text", "")
                            if t:
                                clean = t.strip(" .")
                                if clean and clean != self._current_text:
                                    self._current_text = clean
                                    self._last_update_time = time.time()
                                    
                        model_turn = getattr(sc, "model_turn", None)
                        if model_turn:
                            for part in getattr(model_turn, "parts", []):
                                if hasattr(part, "text") and part.text:
                                    clean_part = part.text.strip(" .")
                                    if clean_part:
                                        self._emit(f"TEXT:{clean_part} ")
                                    
                    except Exception:
                        pass
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.running:
                    self._emit(f"ERROR:Receive failed: {e}")
                    self.running = False
                break

    async def listen_stdin(self):
        while self.running:
            try:
                line = await asyncio.to_thread(sys.stdin.readline)
            except Exception:
                self.running = False
                break
            if not line or line.strip().upper() == "STOP":
                self.running = False
                self._flush_text()
                break

    def _emit(self, msg: str):
        try:
            sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
            sys.stdout.buffer.flush()
        except Exception:
            pass

    async def run_with_key(self, api_key: str):
        if "google.genai" not in sys.modules:
            self._emit("ERROR:google-genai not installed.")
            return
            
        client = genai.Client(
            http_options={"api_version": "v1beta"},
            api_key=api_key,
        )

        self.out_queue = asyncio.Queue(maxsize=40)
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            blocksize=CHUNK_SAMPLES,
            callback=self._audio_callback,
        )

        try:
            # Simplified system instruction focusing only on transcription and mixed languages
            sys_inst = {"parts": [{"text": "You are a highly accurate multilingual voice typing dictation tool. Transcribe the user's speech exactly as spoken. If the user mixes multiple languages (like Arabic and English) in the same sentence, transcribe both naturally without getting confused. Output ONLY the transcribed text. Do not translate. Do not add unnecessary trailing punctuation."}]}
            
            config = types.LiveConnectConfig(
                response_modalities=["TEXT"],
                system_instruction=sys_inst
            )
            
            async with client.aio.live.connect(model=MODEL, config=config) as session:
                self.session = session
                self._emit("READY")
                self._stream.start()

                try:
                    async with asyncio.TaskGroup() as tg:
                        tg.create_task(self.send_audio())
                        tg.create_task(self.receive_text())
                        tg.create_task(self.listen_stdin())
                        tg.create_task(self.watch_silence())
                except* Exception as eg:
                    non_cancelled = [e for e in eg.exceptions if not isinstance(e, asyncio.CancelledError)]
                    if non_cancelled:
                        raise non_cancelled[0]
        finally:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass

    async def run(self):
        last_err = None
        total = len(self.api_keys)
        for i, key in enumerate(self.api_keys):
            if not self.running:
                break
            try:
                await self.run_with_key(key)
                self._emit("DONE")
                return
            except asyncio.CancelledError:
                self._emit("DONE")
                return
            except Exception as e:
                last_err = e
                if i < total - 1:
                    self._emit(f"ROTATE:Key {i+1} failed ({e}), switching to next.")
                else:
                    break

        if last_err:
            self._emit(f"ERROR:All API keys exhausted. Last error: {last_err}")
        else:
            self._emit("DONE")

def main():
    if len(sys.argv) < 2:
        print("ERROR:Usage: transcriber.py key1,key2,...", flush=True)
        sys.exit(1)

    keys = [k.strip() for k in sys.argv[1].split(",") if k.strip()]
    if not keys:
         print("ERROR:Please enter a valid API key.", flush=True)
         sys.exit(1)

    t = Transcriber(keys)
    try:
        asyncio.run(t.run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"ERROR:Fatal: {e}", flush=True)

if __name__ == "__main__":
    main()
