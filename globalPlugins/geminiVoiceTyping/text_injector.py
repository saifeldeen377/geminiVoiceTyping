import ctypes
import logging
import time

try:
    import winUser
    import core
    import globalPluginHandler
    import api
    _in_nvda = True
except Exception:
    _in_nvda = False

log = logging.getLogger("geminiVoiceTyping.injector")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

def _send_ctrl_v():
    try:
        winUser.keybd_event(0x11, 0, 0, 0)
        winUser.keybd_event(0x56, 0, 0, 0)
        winUser.keybd_event(0x56, 0, 2, 0)
        winUser.keybd_event(0x11, 0, 2, 0)
    except Exception as e:
        log.warning(f"send_ctrl_v failed: {e}")

def _suppress_cliphistory():
    """Temporarily disables the ClipHistory addon from recording."""
    if not _in_nvda: return
    try:
        for plugin in globalPluginHandler.runningPlugins:
            if plugin.__module__ == "globalPlugins.ClipHistory":
                if hasattr(plugin, "suppress_clipboard_next"):
                    plugin.suppress_clipboard_next()
                    log.info("Suppressed ClipHistory for dictation.")
                    break
    except Exception as e:
        log.warning(f"Failed to suppress ClipHistory: {e}")

def paste_text(text, stealth=True):
    if not text or not _in_nvda:
        return

    if not stealth:
        # Standard visible paste without restoring the old clipboard
        try:
            api.copyToClip(text)
            core.callLater(50, _send_ctrl_v)
        except Exception as e:
            log.error(f"Standard clipboard paste failed: {e}")
        return
        
    # --- Stealth Mode ---
    # Tell ClipHistory to close its eyes for 500ms!
    _suppress_cliphistory()
    
    # 1. Backup old clipboard
    old_clip = None
    try:
        old_clip = api.getClipData()
    except Exception:
        pass

    try:
        if not user32.OpenClipboard(0):
            return
        
        user32.EmptyClipboard()
        
        # 2. Set the Unicode Text
        encoded = text.encode('utf-16-le') + b'\x00\x00'
        hGlobal = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
        if hGlobal:
            pGlobal = kernel32.GlobalLock(hGlobal)
            ctypes.memmove(pGlobal, encoded, len(encoded))
            kernel32.GlobalUnlock(hGlobal)
            user32.SetClipboardData(CF_UNICODETEXT, hGlobal)
            
        # 3. Tell clipboard monitors to IGNORE this entry!
        fmt_exclude = user32.RegisterClipboardFormatW("ExcludeClipboardContentFromMonitorProcessing")
        if fmt_exclude:
            hExclude = kernel32.GlobalAlloc(GMEM_MOVEABLE, 2)
            pExclude = kernel32.GlobalLock(hExclude)
            ctypes.memset(pExclude, 0, 2)
            kernel32.GlobalUnlock(hExclude)
            user32.SetClipboardData(fmt_exclude, hExclude)
            
        user32.CloseClipboard()
        
        # 4. Paste via Ctrl+V
        _send_ctrl_v()
        
        # 5. Restore the old clipboard
        def _restore():
            try:
                if old_clip is not None:
                    api.copyToClip(old_clip)
                else:
                    if user32.OpenClipboard(0):
                        user32.EmptyClipboard()
                        user32.CloseClipboard()
            except Exception:
                pass
                
        core.callLater(150, _restore)
        
    except Exception as e:
        log.error(f"Stealth clipboard paste failed: {e}")
        try:
            user32.CloseClipboard()
        except:
            pass





