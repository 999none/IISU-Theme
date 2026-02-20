-# IISU-Theme
\ No newline at end of file
+# iiSU White UI — Nintendo 3DS Theme Build
+
+This repository is now focused on generating a **real hardware-compatible** Nintendo 3DS theme package for **Anemone3DS**.
+
+## What this repo builds
+
+- `top.png` (412x240)
+- `bottom.png` (320x240)
+- `preview.png`
+- `body_LZ.bin` (real LZ11-compressed theme body)
+- `info.smdh` (valid SMDH with 24x24 + 48x48 tiled RGB565 icons)
+- `iiSU_White_UI.zip` (Anemone-ready package)
+
+## Usage
+
+```bash
+python3 -m pip install pillow
+python3 build_theme_package.py
+python3 verify_theme.py
+```
+
+## Output
+
+- Theme folder: `iiSU_White_UI/`
+- Zip package: `iiSU_White_UI.zip`
+
+The zip is structured for Anemone as:
+
+```text
+iiSU_White_UI/
+  top.png
+  bottom.png
+  preview.png
+  body_LZ.bin
+  info.smdh
+  README_BUILD.md
+```
 
EOF
)
