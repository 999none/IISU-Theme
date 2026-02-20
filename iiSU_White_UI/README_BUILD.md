# iiSU White UI — Nintendo 3DS Custom Theme

**Version:** 1.0 White Edition  
**Author:** none  
**Compatibility:** Anemone3DS / Theme Plaza

---

## Theme Overview

A fully custom Nintendo 3DS theme inspired by the iiSU network interface.  
Designed with a modern white base, soft pastel gradients, rounded UI elements,  
and subtle shadows for a premium console feel.

### Color Palette

| Role      | Hex       | Description              |
|-----------|-----------|--------------------------|
| Base      | `#FFFFFF` | Primary white            |
| Base      | `#F8F8F8` | Warm white               |
| Base      | `#F2F2F2` | Light gray               |
| Accent    | `#7C8CFF` | Pastel violet (primary)  |
| Accent    | `#9FAAFF` | Pastel violet (mid)      |
| Accent    | `#B8C0FF` | Pastel violet (light)    |
| Text      | `#333333` | Dark gray text           |
| Shadow    | `rgba(0,0,0,0.05)` | Soft shadow     |
| Shadow    | `rgba(0,0,0,0.08)` | Medium shadow   |

---

## File Manifest

```
iiSU_White_UI/
├── top.png           412x240  Top screen background
├── bottom.png        320x240  Bottom screen background
├── preview.png       444x552  Combined dual-screen preview
├── body_LZ.bin       512B     PLACEHOLDER — see instructions below
├── info.smdh         14KB     PLACEHOLDER with embedded metadata
├── README_BUILD.md            This file
└── generate_theme.py          Python source (asset generator)
```

---

## Asset Details

### top.png (412×240)
- White base with subtle vertical gradient (lighter top → slightly darker bottom)
- Ultra-subtle staggered dotted texture overlay
- Custom "iiSU" logo rendered in pastel violet (#7C8CFF / #9FAAFF)
- Anti-aliased at 4× resolution, downscaled for smooth edges
- Soft elliptical glow behind logo area
- "WHITE UI" subtitle and version number
- Decorative corner accents and diamond shapes
- Clean spacing — premium glassy white console feel

### bottom.png (320×240)
- White base with subtle gradient
- 5×3 grid of icon placeholders with rounded corners (radius 7px)
- Each icon has unique minimal geometric pattern
- Center icon highlighted with pastel violet (#7C8CFF) glow border
- Soft drop shadows under each icon
- Bottom toolbar with 3DS-style button prompts:
  - (Y) Edit | (O) Details | Page dots | (A) Select | (+) Menu
- Active page dot in accent violet

### preview.png
- Combined dual-screen mockup
- Both screens shown in bezel frames with soft shadows
- Theme label at bottom

---

## Placeholder Files — How to Generate Real Binaries

### body_LZ.bin

The `body_LZ.bin` file controls the 3DS theme's UI layout, including:
- Folder selection highlight colors
- Text colors
- Highlight border styles
- Animation parameters
- Icon layout configuration

**The included file is a PLACEHOLDER.** Generate the real one using:

#### Option 1: YATA+ (Yet Another Theme Application)
1. Download YATA+ from: https://github.com/CyberYoshi64/YATA-AIO
2. Open the application
3. Load `top.png` as the top screen wallpaper
4. Load `bottom.png` as the bottom screen wallpaper
5. Configure theme settings:
   - Folder highlight color: `#7C8CFF`
   - Text color: `#333333`
   - Selection glow color: `#9FAAFF`
   - Remove default blue highlights
   - Enable rounded highlight borders
6. Export → This generates the proper `body_LZ.bin`

#### Option 2: 3DS Theme Editor (Usagi 3DS Theme Editor)
1. Download from: https://usagi-theme.com or search "Usagi 3DS Theme Editor"
2. Create new theme project
3. Import `top.png` and `bottom.png` as background images
4. Set body customization:
   - **Top draw type:** Texture
   - **Bottom draw type:** Texture  
   - **Cursor color:** `#7C8CFF`
   - **Folder arrow color:** `#9FAAFF`
   - **Folder BG color:** `#F8F8F8`
   - **Open/Close text color:** `#333333`
   - **File text color:** `#333333`
5. Build theme → Exports `body_LZ.bin`

#### Option 3: Manual with 3dstool
1. Create a theme body configuration matching the 3DS theme spec
2. Compress with LZ11 compression
3. Output as `body_LZ.bin`

Reference: https://www.3dbrew.org/wiki/Home_Menu/Themes

### info.smdh

The `info.smdh` file contains theme metadata (title, description, author)  
and small/large icon images displayed in Anemone3DS.

**The included file is a structured PLACEHOLDER** with correct SMDH header  
and UTF-16LE encoded metadata. It contains:
- Title: "iiSU White UI"
- Short Description: "Minimal iiSU-inspired white interface theme."
- Long Description: Full theme description
- Author: "none"

**To generate a proper info.smdh with icons:**

1. Create a 24×24 small icon and 48×48 large icon (PNG, RGB565 format)
2. Use `smdhtool` (from devkitPro):
   ```bash
   smdhtool --create "iiSU White UI" \
     "Minimal iiSU-inspired white interface theme." \
     "none" \
     icon_48x48.png \
     info.smdh
   ```
3. Or use bannertool:
   ```bash
   bannertool makesmdh \
     -s "iiSU White UI" \
     -l "A fully custom Nintendo 3DS theme inspired by iiSU. White Edition." \
     -p "none" \
     -i icon_48x48.png \
     -o info.smdh
   ```

---

## Installation on Nintendo 3DS

### Via Anemone3DS
1. Place the `iiSU_White_UI` folder on your SD card:
   ```
   SD:/Themes/iiSU_White_UI/
   ```
2. Open Anemone3DS on your 3DS
3. Navigate to the theme
4. Select and apply

### Via Theme Plaza
1. Ensure all files are properly generated (real `body_LZ.bin` required)
2. Upload to https://themeplaza.art/
3. Fill in theme metadata
4. Submit for review

---

## BGM (Background Music)

BGM (`bgm.bcstm`) is **excluded** from this build.

If you want to add ambient music:
1. Prepare a 30-45 second seamless loop audio file
2. Convert to BCSTM format using:
   - `vgmstream` or `citric-composer` for conversion
   - Loop point must be set in the BCSTM header
3. Name the file `bgm.bcstm` and place in the theme folder

Style recommendation: ambient minimal, soft piano/synth, console UI feel.

---

## Regenerating Assets

The Python generator script is included. To regenerate:

```bash
pip install pillow
python3 generate_theme.py
```

Output will be written to `/app/iiSU_White_UI/`.

---

## Credits & Legal

- **Design inspiration:** iiSU Network (https://iisu.network/)
- **All artwork is original** — no iiSU assets were copied or reused
- **Style inspiration only** — design language adapted for 3DS theme format
- Nintendo 3DS is a trademark of Nintendo Co., Ltd.
- This theme is a fan creation for personal use

---

*iiSU White UI v1.0 — White Edition*
