# -*- coding: utf-8 -*-
"""
Build and package script for Gemini Voice Typing NVDA Add-on.
Creates a valid .nvda-addon file ready to be installed in NVDA.
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_FILE = os.path.join(BASE_DIR, "manifest.ini")
GLOBAL_PLUGINS_DIR = os.path.join(BASE_DIR, "globalPlugins")
OUTPUT_DIR = os.path.join(BASE_DIR, "dist")


def parse_manifest(manifest_path):
    info = {"name": "geminiVoiceTyping", "version": "1.0.0"}
    if not os.path.exists(manifest_path):
        return info
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                info[key.strip()] = val.strip().strip('"').strip("'")
    return info


def build_addon():
    if not os.path.exists(MANIFEST_FILE):
        print(f"Error: manifest.ini not found at {MANIFEST_FILE}")
        return

    info = parse_manifest(MANIFEST_FILE)
    name = info.get("name", "geminiVoiceTyping")
    version = info.get("version", "1.0.0")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    addon_filename = f"{name}.nvda-addon"
    addon_path = os.path.join(OUTPUT_DIR, addon_filename)

    print(f"Building {addon_filename} ...")

    with zipfile.ZipFile(addon_path, "w", zipfile.ZIP_DEFLATED) as z:
        # Add manifest.ini
        z.write(MANIFEST_FILE, "manifest.ini")
        print("  Added: manifest.ini")

        # Add all files in globalPlugins
        for root, dirs, files in os.walk(GLOBAL_PLUGINS_DIR):
            for file in files:
                if file.endswith(".pyc") or "__pycache__" in root:
                    continue
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, BASE_DIR)
                z.write(abs_path, rel_path)
                print(f"  Added: {rel_path}")

        # Add all files in doc
        doc_dir = os.path.join(BASE_DIR, "doc")
        if os.path.exists(doc_dir):
            for root, dirs, files in os.walk(doc_dir):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, BASE_DIR)
                    z.write(abs_path, rel_path)
                    print(f"  Added: {rel_path}")

    print(f"\n[SUCCESS] Add-on built successfully at:\n{addon_path}\n")
    return addon_path


if __name__ == "__main__":
    build_addon()
