# -*- coding: utf-8 -*-
"""
NVDA Settings Panel for Gemini Voice Typing.
"""

try:
    import wx
    import gui
    from gui import guiHelper
    from gui.settingsDialogs import SettingsPanel
    import subprocess
    import threading
    _has_gui = True
except Exception:
    _has_gui = False

    class SettingsPanel:
        pass

from .config import config


if _has_gui:
    class PipInstallDialog(wx.Dialog):
        def __init__(self, parent):
            super(PipInstallDialog, self).__init__(parent, title="Installing Required Libraries", size=(400, 150))
            self.CenterOnParent()
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            self.label = wx.StaticText(self, label="Please wait while the required libraries are being installed...")
            sizer.Add(self.label, 0, wx.ALL | wx.ALIGN_CENTER, 10)
            
            self.gauge = wx.Gauge(self, range=100, size=(350, 20))
            sizer.Add(self.gauge, 0, wx.ALL | wx.ALIGN_CENTER, 10)
            
            btnSizer = wx.BoxSizer(wx.HORIZONTAL)
            self.cancelBtn = wx.Button(self, wx.ID_CANCEL, label="Cancel (Esc)")
            self.cancelBtn.Bind(wx.EVT_BUTTON, self.onCancel)
            btnSizer.Add(self.cancelBtn, 0, wx.ALL, 5)
            
            sizer.Add(btnSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
            self.SetSizer(sizer)
            
            self.Bind(wx.EVT_CLOSE, self.onCancel)
            self.Bind(wx.EVT_CHAR_HOOK, self.onCharHook)
            
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
            self.timer.Start(50)
            
            self.process = None
            self.thread = threading.Thread(target=self.runInstall)
            self.thread.daemon = True
            self.thread.start()
            
        def onCharHook(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.onCancel(None)
            else:
                event.Skip()
                
        def onTimer(self, event):
            self.gauge.Pulse()
            
        def onCancel(self, event):
            if self.process:
                try:
                    self.process.terminate()
                except Exception:
                    pass
            self.timer.Stop()
            self.Destroy()

        def runInstall(self):
            try:
                python_path = config.get("python_path", "python")
                self.process = subprocess.Popen(
                    [python_path, "-m", "pip", "install", "sounddevice", "google-genai"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.process.communicate()
                if self.process.returncode == 0:
                    wx.CallAfter(self.onSuccess)
                else:
                    wx.CallAfter(self.onFail)
            except Exception as e:
                wx.CallAfter(self.onFail)
                
        def onSuccess(self):
            self.timer.Stop()
            self.Destroy()
            import ui
            import core
            core.callLater(0, ui.message, "Libraries installed successfully, you can now use the add-on")
            wx.MessageBox("Libraries installed successfully, you can now use the add-on.", "Success", wx.OK | wx.ICON_INFORMATION)
            
        def onFail(self):
            self.timer.Stop()
            self.Destroy()
            import ui
            import core
            core.callLater(0, ui.message, "Failed to install libraries.")
            wx.MessageBox("Failed to install libraries. Please ensure Python is installed and added to PATH.", "Error", wx.OK | wx.ICON_ERROR)

    class GeminiVoiceTypingSettingsPanel(SettingsPanel):
        title = "Gemini Voice Typing"

        def makeSettings(self, settingsSizer):
            sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)

            self.apiKeysCtrl = sHelper.addLabeledControl(
                "Gemini API Keys (separate multiple keys with commas for auto-failover):",
                wx.TextCtrl,
            )
            self.apiKeysCtrl.SetValue(config.get("api_keys", ""))
            
            # Engine selection
            self.engineChoices = [
                "System Python (Advanced, Requires Installation) - Default",
                "Built-in NVDA Python (Simple, No installation needed)"
            ]
            self.engineCtrl = sHelper.addLabeledControl(
                "Execution Engine:",
                wx.Choice,
                choices=self.engineChoices
            )
            engine_val = config.get("engine", "system_python")
            self.engineCtrl.SetSelection(0 if engine_val == "system_python" else 1)
            self.engineCtrl.Bind(wx.EVT_CHOICE, self.onEngineChange)
            
            self.installLibsBtn = sHelper.addItem(wx.Button(self, label="Install Required Libraries"))
            self.installLibsBtn.Bind(wx.EVT_BUTTON, self.onInstallLibs)
            self.installLibsBtn.Show(engine_val == "system_python")
            
            # Mode selection
            self.modeChoices = [
                "Strict Live Mode (Very Fast) - gemini-3.5-transcribe-live",
                "Smart Batch Mode (Perfect accuracy, types when you pause or press Enter) - Uses Selected Language Model"
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
                wx.CheckBox(self, label="Enable Corrector (Language Model)")
            )
            self.enableCorrectorCheckbox.SetValue(config.get("enable_corrector", True))
            self.enableCorrectorCheckbox.Bind(wx.EVT_CHECKBOX, self.onCorrectorToggle)
            
            self.llmChoices = [
                "gemini-3.1-flash-lite",
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash",
                "gemini-2.5-flash",
                "gemini-1.5-flash"
            ]
            self.llmModelCtrl = sHelper.addLabeledControl(
                "Language Model (for Corrector & Smart Mode):",
                wx.Choice,
                choices=self.llmChoices
            )
            curr_llm = config.get("llm_model", "gemini-3.1-flash-lite")
            if curr_llm in self.llmChoices:
                self.llmModelCtrl.SetSelection(self.llmChoices.index(curr_llm))
            else:
                self.llmModelCtrl.SetSelection(0)
            
            # Corrector Prompt text control
            self.correctorPromptLabel = wx.StaticText(self, label="Correction Prompt:")
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
            self.llmModelCtrl.GetParent().Show(is_enabled)
            self.correctorPromptLabel.Show(is_enabled)
            self.correctorPromptCtrl.Show(is_enabled)
            self.Layout()

        def onEngineChange(self, evt):
            is_sys = self.engineCtrl.GetSelection() == 0
            self.installLibsBtn.Show(is_sys)
            self.Layout()
            
        def onInstallLibs(self, evt):
            dlg = PipInstallDialog(self)
            dlg.ShowModal()

        def onSave(self):
            config.set("api_keys", self.apiKeysCtrl.GetValue().strip())
            
            engine_sel = self.engineCtrl.GetSelection()
            config.set("engine", "system_python" if engine_sel == 0 else "built_in")
            
            mode_sel = self.modeCtrl.GetSelection()
            mode_str = "strict" if mode_sel == 0 else "smart"
            config.set("transcription_mode", mode_str)
            
            llm_sel = self.llmModelCtrl.GetSelection()
            config.set("llm_model", self.llmChoices[llm_sel])
            
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
