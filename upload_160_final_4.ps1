$env:Path = "$pwd\mingit\cmd;$pwd\gh_cli\bin;" + $env:Path

# Delete old 1.6.0 tags
@("v1.6.0") | ForEach-Object {
     = 
    while ($true) {
        gh release delete  -y --cleanup-tag 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 1) { break }
        Start-Sleep -Seconds 2
    }
}

while ($true) {
    gh release create v1.6.0 ./dist/geminiVoiceTyping.nvda-addon --title "Gemini Voice Typing v1.6.0 (Stable)" --notes "A completely refactored version that relies on Google's natural silence detection. Clean, fast, and simple. Includes fix for stdout architecture, python module imports, silence detection, and AI corrector (now using flash instead of flash-lite for better Arabic grammar/hamzas)."
    if ($LASTEXITCODE -eq 0) { break }
    Start-Sleep -Seconds 3
}
