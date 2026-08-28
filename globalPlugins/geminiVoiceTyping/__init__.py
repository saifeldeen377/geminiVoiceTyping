# -*- coding: utf-8 -*-
"""
Gemini Voice Typing - NVDA Global Plugin.

Architecture (learned from Vision Assistant Pro):
  - Launches transcriber.py as a subprocess using system Python.
  - Reads transcribed text from stdout line-by-line.
  - Pastes text using NVDA's api.copyToClip() + winUser Ctrl+V via core.callLater().
  - All network/audio runs in subprocess so NVDA NEVER blocks.
"""

import os
import subprocess
import threading
import logging
import time

try:
    import globalPluginHandler
    import api
    import ui
    import core
    import controlTypes
    import tones
    import winUser
    from gui import settingsDialogs
    _in_nvda = True
except Exception:
    _in_nvda = False

    class globalPluginHandler:
        class GlobalPlugin:
            pass

from .config import config
from .text_injector import paste_text
from .settings_gui import GeminiVoiceTypingSettingsPanel

log = logging.getLogger("geminiVoiceTyping")

TRANSCRIBER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcriber.py")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "Gemini Voice Typing"

    def __init__(self):
        super().__init__()
        self._proc = None
        self._reader_thread = None
        self._is_active = False
        self._mode = "normal"

        if _in_nvda and hasattr(settingsDialogs, "NVDASettingsDialog"):
            if GeminiVoiceTypingSettingsPanel not in settingsDialogs.NVDASettingsDialog.categoryClasses:
                settingsDialogs.NVDASettingsDialog.categoryClasses.append(GeminiVoiceTypingSettingsPanel)

    def terminate(self):
        self._do_stop()
        if _in_nvda and hasattr(settingsDialogs, "NVDASettingsDialog"):
            if GeminiVoiceTypingSettingsPanel in settingsDialogs.NVDASettingsDialog.categoryClasses:
                settingsDialogs.NVDASettingsDialog.categoryClasses.remove(GeminiVoiceTypingSettingsPanel)
        super().terminate()

    # ── Focus check ──────────────────────────────────────
    def _is_focus_editable(self):
        if not _in_nvda:
            return True
        try:
            obj = api.getFocusObject()
            if not obj:
                return False
            role = getattr(obj, "role", None)
            states = getattr(obj, "states", set())

            for name in ("EDITABLETEXT", "DOCUMENT", "TERMINAL", "RICHEDIT"):
                r = getattr(controlTypes.Role, name, None)
                if r is not None and role == r:
                    return True

            editable = getattr(controlTypes.State, "EDITABLE", None)
            if editable and editable in states:
                return True

            if getattr(obj, "isContentEditable", False):
                return True

            wc = str(getattr(obj, "windowClassName", "")).lower()
            if any(x in wc for x in ("edit", "scintilla", "rich", "textarea")):
                return True
        except Exception:
            return True
        return False

    # ── Dynamic gesture binding for Manual Commit Mode ──
    _MANUAL_GESTURES = {
        "kb:enter": "manualCommit",
        "kb:space": "manualCommit",
        "kb:escape": "manualEscape",
    }

    def _bind_manual_gestures(self):
        """Bind Enter/Space/Escape only when Manual Commit Mode is active."""
        for gesture_id, script_name in self._MANUAL_GESTURES.items():
            try:
                self.bindGesture(gesture_id, script_name)
            except Exception:
                pass

    def _unbind_manual_gestures(self):
        """Remove Enter/Space/Escape bindings when leaving Manual Commit Mode."""
        for gesture_id in self._MANUAL_GESTURES:
            try:
                self.removeGestureBinding(gesture_id)
            except Exception:
                pass

    # ── Start ────────────────────────────────────────────
    def _do_start(self, mode="normal"):
        if self._is_active:
            return

        if not config.has_keys():
            if _in_nvda:
                tones.beep(200, 150)
                ui.message("No API key set. Go to NVDA Settings, Gemini Voice Typing.")
            return

        python_path = config.get("python_path", "python")
        keys_csv = config.get_api_keys_csv()

        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0

            args = [python_path, TRANSCRIBER_SCRIPT, keys_csv]
            if mode == "manual":
                args.append("--manual")

            self._proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=si,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except FileNotFoundError:
            if _in_nvda:
                tones.beep(200, 150)
                ui.message(f"Python not found at: {python_path}")
            return
        except Exception as e:
            log.error(f"Failed to launch transcriber: {e}")
            if _in_nvda:
                tones.beep(200, 150)
                ui.message("Failed to start voice typing.")
            return

        self._is_active = True
        self._mode = mode

        # Bind Enter/Space/Escape ONLY when in manual mode
        if mode == "manual":
            self._bind_manual_gestures()

        self._reader_thread = threading.Thread(target=self._stdout_reader, daemon=True)
        self._reader_thread.start()

        # Also read stderr for debug logging
        threading.Thread(target=self._stderr_reader, daemon=True).start()

    # ── Stop ─────────────────────────────────────────────
    def _do_stop(self):
        if not self._is_active:
            return

        was_manual = self._mode == "manual"
        self._is_active = False

        proc = self._proc
        self._proc = None
        self._mode = "normal"

        # Unbind Enter/Space/Escape when leaving manual mode
        if was_manual:
            self._unbind_manual_gestures()

        if proc:
            try:
                proc.stdin.write(b"STOP\n")
                proc.stdin.flush()
            except Exception:
                pass
            try:
                proc.terminate()
            except Exception:
                pass

        if _in_nvda:
            tones.beep(400, 80)

    # ── STDOUT reader ────────────────────────────────────
    def _stdout_reader(self):
        proc = self._proc
        if not proc:
            return

        try:
            for raw_line in proc.stdout:
                if not self._is_active:
                    break

                try:
                    line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                except Exception:
                    continue

                if not line:
                    continue

                # READY -> beep high
                if line == "READY":
                    if _in_nvda:
                        core.callLater(0, tones.beep, 1800, 60)
                    continue

                # DONE -> clean exit
                if line == "DONE":
                    break

                # ROTATE -> double tone (if enabled)
                if line.startswith("ROTATE:"):
                    log.warning(f"Transcriber Key Rotation: {line[7:]}")
                    if _in_nvda and config.get("beep_on_key_rotation", False):
                        core.callLater(0, tones.beep, 800, 50)
                        core.callLater(100, tones.beep, 800, 50)
                    continue

                # ERROR:message
                if line.startswith("ERROR:"):
                    err_msg = line[6:]
                    log.error(f"Transcriber: {err_msg}")
                    if _in_nvda:
                        core.callLater(0, tones.beep, 200, 150)
                        core.callLater(50, ui.message, err_msg)
                    break

                if line.startswith("TEXT:"):
                    text = line[5:]
                    if text and _in_nvda:
                        is_stealth = not config.get("copy_to_clipboard", False)
                        core.callLater(0, paste_text, text, stealth=is_stealth)
                    continue

        except Exception as e:
            log.error(f"stdout reader error: {e}")
        finally:
            if self._is_active:
                self._is_active = False
                if self._mode == "manual":
                    self._unbind_manual_gestures()
                if _in_nvda:
                    core.callLater(0, tones.beep, 400, 80)

    # ── STDERR reader ────────────────────────────────────
    def _stderr_reader(self):
        proc = self._proc
        if not proc:
            return
        try:
            for raw_line in proc.stderr:
                if not self._is_active:
                    break
                try:
                    line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if line:
                        log.warning(f"Transcriber stderr: {line}")
                except Exception:
                    pass
        except Exception:
            pass

    # ── Manual Commit Mode ───────────────────────────────
    def _manual_mode_allowed(self):
        return bool(config.get("manual_mode_enabled", True))

    def _toggle_manual_mode_worker(self):
        if not self._manual_mode_allowed():
            if _in_nvda:
                tones.beep(200, 120)
                ui.message("Manual Commit Mode is disabled in Gemini Voice Typing settings.")
            return

        if self._is_active:
            if self._mode == "manual":
                self._do_stop()
                return
            # Switch cleanly from normal mode to manual mode.
            self._do_stop()
            time.sleep(0.15)

        if not self._is_active:
            self._do_start("manual")

    def script_toggleManualCommitMode(self, gesture):
        """Toggle Manual Commit Mode (NVDA+Alt+G)."""
        threading.Thread(target=self._toggle_manual_mode_worker, daemon=True).start()

    script_toggleManualCommitMode.__doc__ = "Toggle Manual Commit Mode"

    def script_manualCommit(self, gesture):
        """Commit accumulated speech only while Manual Commit Mode is active."""
        if self._is_active and self._mode == "manual":
            if not self._is_focus_editable():
                gesture.send()
                return
            self._send_command("COMMIT")
            return
        gesture.send()

    script_manualCommit.__doc__ = "Commit manual voice typing text"

    def script_manualEscape(self, gesture):
        """Exit Manual Commit Mode without sending Escape to the application."""
        if self._is_active and self._mode == "manual":
            threading.Thread(target=self._do_stop, daemon=True).start()
            return
        gesture.send()

    script_manualEscape.__doc__ = "Exit Manual Commit Mode"

    # ── NVDA Script ──────────────────────────────────────
    def script_toggleVoiceTyping(self, gesture):
        """Toggle Gemini Voice Typing on or off."""
        if self._is_active:
            threading.Thread(target=self._do_stop, daemon=True).start()
        else:
            threading.Thread(target=self._do_start, args=("normal",), daemon=True).start()

    script_toggleVoiceTyping.__doc__ = "Toggle Gemini Voice Typing"

    # Only permanent gestures — Enter/Space/Escape are bound dynamically
    # via _bind_manual_gestures() when Manual Commit Mode starts.
    __gestures = {
        "kb:NVDA+shift+g": "toggleVoiceTyping",
        "kb:NVDA+alt+g": "toggleManualCommitMode",
    }
