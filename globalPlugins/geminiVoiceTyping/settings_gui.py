# -*- coding: utf-8 -*-
"""
NVDA Settings Panel for Gemini Voice Typing.
"""

try:
    import wx
    import gui
    from gui import guiHelper
    from gui.settingsDialogs import SettingsPanel
    _has_gui = True
except Exception:
    _has_gui = False

    class SettingsPanel:
        pass

from .config import config


if _has_gui:
    class GeminiVoiceTypingSettingsPanel(SettingsPanel):
        title = "Gemini Voice Typing"

        def makeSettings(self, settingsSizer):
            sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

            self.apiKeysCtrl = sHelper.addLabeledControl(
                "Gemini API Keys (separate multiple keys with commas for auto-failover):",
                wx.TextCtrl,
            )
            self.apiKeysCtrl.SetValue(config.get("api_keys", ""))

            self.beepOnRotateCheckbox = sHelper.addItem(
                wx.CheckBox(self, label="Play double-beep sound when automatically switching to another API key")
            )
            self.beepOnRotateCheckbox.SetValue(config.get("beep_on_key_rotation", False))

            self.copyClipboardCheckbox = sHelper.addItem(
                wx.CheckBox(self, label="Auto copy result to clipboard")
            )
            self.copyClipboardCheckbox.SetValue(config.get("copy_to_clipboard", False))

        def onSave(self):
            config.set("api_keys", self.apiKeysCtrl.GetValue().strip())
            config.set("beep_on_key_rotation", self.beepOnRotateCheckbox.GetValue())
            config.set("copy_to_clipboard", self.copyClipboardCheckbox.GetValue())

else:
    class GeminiVoiceTypingSettingsPanel:
        title = "Gemini Voice Typing"
