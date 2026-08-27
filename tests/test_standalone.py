# -*- coding: utf-8 -*-
"""
Standalone smoke test for Gemini Voice Typing modules.
"""

import os
import sys

# Add globalPlugins directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "globalPlugins"))

from geminiVoiceTyping.config import ConfigManager
from geminiVoiceTyping.sound_effects import play_start_sound, play_stop_sound, play_key_rotate_sound
from geminiVoiceTyping.text_injector import inject_text

def test_config_multi_key():
    print("Testing Multi-Key management and rotation...")
    cfg = ConfigManager()
    cfg.set("api_keys", "key1_abc, key2_def, key3_ghi")
    cfg.set("current_key_index", 0)

    keys = cfg.get_api_keys_list()
    assert len(keys) == 3, f"Expected 3 keys, got {len(keys)}"
    assert keys[0] == "key1_abc"
    assert keys[1] == "key2_def"
    assert keys[2] == "key3_ghi"
    assert cfg.get_active_key() == "key1_abc"

    # Test rotation
    next_key = cfg.rotate_to_next_key()
    assert next_key == "key2_def"
    assert cfg.get_active_key() == "key2_def"

    next_key = cfg.rotate_to_next_key()
    assert next_key == "key3_ghi"

    next_key = cfg.rotate_to_next_key()
    assert next_key == "key1_abc"
    print("[PASS] Multi-Key rotation works correctly!")


def test_audio_effects():
    print("Testing audio cues...")
    play_start_sound()
    play_key_rotate_sound()
    play_stop_sound()
    print("[PASS] Audio cues executed without errors!")


if __name__ == "__main__":
    test_config_multi_key()
    test_audio_effects()
    print("\nAll standalone module tests passed!")
