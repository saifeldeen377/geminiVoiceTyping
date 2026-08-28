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
            
            self.smartShutdownCheckbox = sHelper.addItem(
                wx.CheckBox(self, label="Smart Shutdown (Wait 1 sec to paste final words when closing mic)")
            )
            self.smartShutdownCheckbox.SetValue(config.get("smart_shutdown_delay", True))
            
            # Transcription Prompt text control
            promptLabel = wx.StaticText(self, label="Transcription Prompt (Gemini Live API):")
            settingsSizer.Add(promptLabel, 0, wx.ALL, 5)
            self.promptCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 100))
            self.promptCtrl.SetValue(config.get("system_prompt", ""))
            settingsSizer.Add(self.promptCtrl, 0, wx.ALL | wx.EXPAND, 5)
            
            # Corrector Prompt text control
            correctorPromptLabel = wx.StaticText(self, label="Correction Prompt (Gemini Flash Lite):")
            settingsSizer.Add(correctorPromptLabel, 0, wx.ALL, 5)
            self.correctorPromptCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 100))
            self.correctorPromptCtrl.SetValue(config.get("corrector_prompt", ""))
            settingsSizer.Add(self.correctorPromptCtrl, 0, wx.ALL | wx.EXPAND, 5)

        def onSave(self):
            config.set("api_keys", self.apiKeysCtrl.GetValue().strip())
            config.set("beep_on_key_rotation", self.beepOnRotateCheckbox.GetValue())
            config.set("copy_to_clipboard", self.copyClipboardCheckbox.GetValue())
            config.set("smart_shutdown_delay", self.smartShutdownCheckbox.GetValue())
            config.set("system_prompt", self.promptCtrl.GetValue())
            config.set("corrector_prompt", self.correctorPromptCtrl.GetValue())

else:
    class GeminiVoiceTypingSettingsPanel:
        title = "Gemini Voice Typing"
