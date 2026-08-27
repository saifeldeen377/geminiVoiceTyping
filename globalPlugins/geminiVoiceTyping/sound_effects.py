# -*- coding: utf-8 -*-
"""
Simple beep sound effects for Gemini Voice Typing.
Fallback for non-NVDA testing.
"""

try:
    import tones

    def play_start():
        tones.beep(1800, 60)

    def play_stop():
        tones.beep(400, 80)

    def play_error():
        tones.beep(200, 150)

except Exception:
    import winsound

    def play_start():
        try:
            winsound.Beep(1800, 60)
        except Exception:
            pass

    def play_stop():
        try:
            winsound.Beep(400, 80)
        except Exception:
            pass

    def play_error():
        try:
            winsound.Beep(200, 150)
        except Exception:
            pass
