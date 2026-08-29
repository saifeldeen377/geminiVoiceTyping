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
            
            # Mode selection
            self.modeChoices = [
                "Strict Transcriber (Very Fast) - gemini-3.5-transcribe-live",
                "Smart Multimodal (Better for mixed languages) - gemini-3.5-flash"
            ]
            self.modeCtrl = sHelper.addLabeledControl(
                "Transcription Model Mode:",
                wx.Choice,
                choices=self.modeChoices
            )
            mode_val = config.get("transcription_mode", "strict")
            self.modeCtrl.SetSelection(0 if mode_val == "strict" else 1)
            self.modeCtrl.Bind(wx.EVT_CHOICE, self.onModeChange)

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
            self.promptLabel = wx.StaticText(self, label="Transcription Prompt (Gemini Live API):")
            settingsSizer.Add(self.promptLabel, 0, wx.ALL, 5)
            self.promptCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 100))
            if mode_val == "strict":
                self.promptCtrl.SetValue(config.get("system_prompt_strict", config.get("system_prompt", "")))
            else:
                self.promptCtrl.SetValue(config.get("system_prompt_smart", ""))
            settingsSizer.Add(self.promptCtrl, 0, wx.ALL | wx.EXPAND, 5)
            
            # Corrector Section
            self.enableCorrectorCheckbox = sHelper.addItem(
                wx.CheckBox(self, label="Enable Corrector (Gemini Flash Lite)")
            )
            self.enableCorrectorCheckbox.SetValue(config.get("enable_corrector", True))
            self.enableCorrectorCheckbox.Bind(wx.EVT_CHECKBOX, self.onCorrectorToggle)
            
            # Corrector Prompt text control
            self.correctorPromptLabel = wx.StaticText(self, label="Correction Prompt (Gemini Flash Lite):")
            settingsSizer.Add(self.correctorPromptLabel, 0, wx.ALL, 5)
            self.correctorPromptCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1, 100))
            self.correctorPromptCtrl.SetValue(config.get("corrector_prompt", ""))
            settingsSizer.Add(self.correctorPromptCtrl, 0, wx.ALL | wx.EXPAND, 5)
            
            self._updateCorrectorVisibility()

        def onModeChange(self, evt):
            # Save current prompt to the appropriate config variable before switching
            current_sel = self.modeCtrl.GetSelection()
            # If selection is 0 (strict), we are switching *to* strict, which means we were on smart?
            # Wait, no. We need to know what we are switching *to*, but we don't know what we switched *from* easily unless we track it.
            # Instead of saving on change, we just load the default or saved value for the new selection.
            # Let's save the current text to memory so we don't lose it if they switch back and forth.
            
            # Actually, to make it simple, we just load from config. If they haven't saved, they lose edits on switch.
            if current_sel == 0:
                self.promptCtrl.SetValue(config.get("system_prompt_strict", config.get("system_prompt", "")))
            else:
                self.promptCtrl.SetValue(config.get("system_prompt_smart", ""))
                
        def onCorrectorToggle(self, evt):
            self._updateCorrectorVisibility()
            
        def _updateCorrectorVisibility(self):
            is_enabled = self.enableCorrectorCheckbox.GetValue()
            self.correctorPromptLabel.Show(is_enabled)
            self.correctorPromptCtrl.Show(is_enabled)
            self.Layout()

        def onSave(self):
            config.set("api_keys", self.apiKeysCtrl.GetValue().strip())
            
            mode_sel = self.modeCtrl.GetSelection()
            mode_str = "strict" if mode_sel == 0 else "smart"
            config.set("transcription_mode", mode_str)
            
            config.set("beep_on_key_rotation", self.beepOnRotateCheckbox.GetValue())
            config.set("copy_to_clipboard", self.copyClipboardCheckbox.GetValue())
            config.set("smart_shutdown_delay", self.smartShutdownCheckbox.GetValue())
            
            if mode_str == "strict":
                config.set("system_prompt_strict", self.promptCtrl.GetValue())
            else:
                config.set("system_prompt_smart", self.promptCtrl.GetValue())
                
            config.set("enable_corrector", self.enableCorrectorCheckbox.GetValue())
            config.set("corrector_prompt", self.correctorPromptCtrl.GetValue())

else:
    class GeminiVoiceTypingSettingsPanel:
        title = "Gemini Voice Typing"
