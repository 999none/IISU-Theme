#!/usr/bin/env python3
"""Build a real Anemone3DS-compatible theme package."""

from __future__ import annotations

import os
import subprocess
import zipfile

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
THEME_DIR = os.path.join(ROOT_DIR, "iiSU_White_UI")
ZIP_PATH = os.path.join(ROOT_DIR, "iiSU_White_UI.zip")

PACKAGE_FILES = [
    "top.png",
    "bottom.png",
    "preview.png",
    "body_LZ.bin",
    "info.smdh",
    "README_BUILD.md",
]


def run_step(script_name: str) -> None:
    script = os.path.join(ROOT_DIR, script_name)
    subprocess.run(["python3", script], check=True)


def build_zip() -> None:
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for filename in PACKAGE_FILES:
            src = os.path.join(THEME_DIR, filename)
            if not os.path.isfile(src):
                raise FileNotFoundError(f"Missing expected file: {src}")
            zf.write(src, arcname=f"iiSU_White_UI/{filename}")


def main() -> None:
    run_step("generate_theme.py")
    run_step("generate_real_binaries.py")
    build_zip()
    print(f"Built {ZIP_PATH}")


if __name__ == "__main__":
    main()
