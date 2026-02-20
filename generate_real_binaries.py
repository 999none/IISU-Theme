#!/usr/bin/env python3
"""
Generate REAL Nintendo 3DS theme binary files.
Produces proper body_LZ.bin (LZ11-compressed) and info.smdh with icons.
Based on 3dbrew.org/wiki/Home_Menu/Themes specification.
"""

import struct
import os
import io
import sys
from PIL import Image

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT_DIR, 'backend'))
from lz11 import compress_nlz11

OUTPUT_DIR = os.path.join(ROOT_DIR, "iiSU_White_UI")

# Theme accent colors (RGB888)
CURSOR_BORDER   = (124, 140, 255)  # #7C8CFF
CURSOR_MAIN     = (159, 170, 255)  # #9FAAFF
CURSOR_UNKNOWN  = (184, 192, 255)  # #B8C0FF
CURSOR_GLOW     = (210, 215, 255)  # #D6DBFF

FOLDER_SHADOW   = (200, 205, 240)
FOLDER_MAIN     = (124, 140, 255)


def rgb565(r, g, b):
    """Convert RGB888 to RGB565."""
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)


def tile_offset(x, y):
    """Get Morton/Z-order index for pixel (x,y) within an 8x8 tile."""
    return (
        (x & 1) |
        ((y & 1) << 1) |
        ((x & 2) << 1) |
        ((y & 2) << 2) |
        ((x & 4) << 2) |
        ((y & 4) << 3)
    )


def image_to_tiled_rgb565(img, tex_w, tex_h):
    """Convert PIL Image to tiled RGB565 for 3DS texture format."""
    buf = bytearray(tex_w * tex_h * 2)
    img_w, img_h = img.size
    img_rgb = img.convert('RGB')
    pixels = img_rgb.load()

    tiles_x = tex_w // 8
    tiles_y = tex_h // 8

    for ty in range(tiles_y):
        for tx in range(tiles_x):
            tile_idx = ty * tiles_x + tx
            for py in range(8):
                for px in range(8):
                    ix = tx * 8 + px
                    iy = ty * 8 + py
                    if ix < img_w and iy < img_h:
                        r, g, b = pixels[ix, iy]
                    else:
                        r, g, b = 248, 248, 248  # Fill with theme base color
                    val = rgb565(r, g, b)
                    morton = tile_offset(px, py)
                    offset = (tile_idx * 64 + morton) * 2
                    struct.pack_into('<H', buf, offset, val)

    return bytes(buf)


def build_body_data(top_img, bottom_img):
    """
    Build the decompressed body data according to 3dbrew spec.

    Structure:
      0x00-0xC3: Header
      0xD0+:     Data blocks (colors, textures)

    Top screen: draw type 3 (texture), frame type 1 (texture0, no scroll)
    Bottom screen: draw type 3 (texture), frame type 1 (texture2, no scroll)
    """
    # Texture sizes: 512x256 for both texture0 and texture2
    TEX_W, TEX_H = 512, 256
    tex_size = TEX_W * TEX_H * 2  # RGB565 = 2 bytes per pixel

    # Convert images to tiled RGB565
    print("    Converting top screen to tiled RGB565 (512x256)...")
    top_tex = image_to_tiled_rgb565(top_img, TEX_W, TEX_H)
    print("    Converting bottom screen to tiled RGB565 (512x256)...")
    bot_tex = image_to_tiled_rgb565(bottom_img, TEX_W, TEX_H)

    # Layout data blocks after header (padded to 0xD0)
    header_size = 0xD0

    # Data section offsets (relative to file start)
    cursor_color_offset = header_size        # 0xD0, 12 bytes
    folder_color_offset = cursor_color_offset + 0x10  # 0xE0, 12 bytes
    top_tex_offset = folder_color_offset + 0x10       # 0xF0
    bot_tex_offset = top_tex_offset + tex_size         # 0xF0 + 262144

    total_size = bot_tex_offset + tex_size
    # Align to 16 bytes
    total_size = (total_size + 0xF) & ~0xF

    body = bytearray(total_size)

    # === Header ===
    # 0x00: Version = 1
    struct.pack_into('<I', body, 0x00, 1)
    # 0x04: Unknown = 0
    body[0x04] = 0
    # 0x05: BGM enable = 0 (no bgm)
    body[0x05] = 0
    # 0x08: Normally 0
    struct.pack_into('<I', body, 0x08, 0)

    # 0x0C: Top screen draw type = 3 (texture)
    struct.pack_into('<I', body, 0x0C, 3)
    # 0x10: Top screen frame type = 1 (texture0, no scroll)
    struct.pack_into('<I', body, 0x10, 1)
    # 0x14: Top screen solid color offset = 0 (not used)
    struct.pack_into('<I', body, 0x14, 0)
    # 0x18: Top screen texture offset
    struct.pack_into('<I', body, 0x18, top_tex_offset)
    # 0x1C: Additional top screen texture offset = 0
    struct.pack_into('<I', body, 0x1C, 0)

    # 0x20: Bottom screen draw type = 3 (texture)
    struct.pack_into('<I', body, 0x20, 3)
    # 0x24: Bottom screen frame type = 1 (texture2, no scroll)
    struct.pack_into('<I', body, 0x24, 1)
    # 0x28: Bottom screen texture offset
    struct.pack_into('<I', body, 0x28, bot_tex_offset)

    # 0x2C: Cursor enable = 1
    struct.pack_into('<I', body, 0x2C, 1)
    # 0x30: Cursor color offset
    struct.pack_into('<I', body, 0x30, cursor_color_offset)

    # 0x34: Folder colors enable = 1
    struct.pack_into('<I', body, 0x34, 1)
    # 0x38: Folder color offset
    struct.pack_into('<I', body, 0x38, folder_color_offset)

    # 0x3C-0xC3: Remaining enables = 0 (already zero from bytearray)
    # Just ensure they're 0
    for off in range(0x3C, 0xC4, 8):
        struct.pack_into('<I', body, off, 0)

    # === Cursor color data (0xC bytes = 4 RGB888 colors) ===
    off = cursor_color_offset
    # Border color
    body[off:off+3] = bytes(CURSOR_BORDER)
    off += 3
    # Main color
    body[off:off+3] = bytes(CURSOR_MAIN)
    off += 3
    # Unknown
    body[off:off+3] = bytes(CURSOR_UNKNOWN)
    off += 3
    # Expanded glow color
    body[off:off+3] = bytes(CURSOR_GLOW)

    # === Folder color data (0xC bytes = 2 RGB888 colors + unknown) ===
    off = folder_color_offset
    # Shadowed color
    body[off:off+3] = bytes(FOLDER_SHADOW)
    off += 3
    # Main color
    body[off:off+3] = bytes(FOLDER_MAIN)

    # === Texture data ===
    body[top_tex_offset:top_tex_offset + tex_size] = top_tex
    body[bot_tex_offset:bot_tex_offset + tex_size] = bot_tex

    return bytes(body)


def generate_body_lz(top_img, bottom_img):
    """Generate the real body_LZ.bin file."""
    print("  Building body data structure...")
    body_data = build_body_data(top_img, bottom_img)
    print(f"    Decompressed body: {len(body_data):,} bytes")

    print("  LZ11 compressing (this may take a moment)...")
    out_buf = io.BytesIO()
    compress_nlz11(body_data, out_buf)
    compressed = out_buf.getvalue()
    print(f"    Compressed: {len(compressed):,} bytes ({100*len(compressed)/len(body_data):.1f}%)")

    filepath = os.path.join(OUTPUT_DIR, "body_LZ.bin")
    with open(filepath, 'wb') as f:
        f.write(compressed)
    print(f"    Saved: {filepath}")
    return compressed


def create_icon(size, scale=1):
    """Create a simple iiSU-themed icon at given size."""
    img = Image.new('RGB', (size, size), (248, 248, 248))
    from PIL import ImageDraw
    d = ImageDraw.Draw(img)

    # Simple iiSU-inspired icon: two dots + vertical bars
    cx = size // 2
    cy = size // 2
    s = max(size // 12, 1)

    # Background circle
    pad = size // 8
    d.ellipse((pad, pad, size - pad, size - pad), fill=(230, 233, 255))

    # 'i' dots
    dot_r = max(s, 1)
    dot_y = cy - size // 4
    d.ellipse((cx - size//6 - dot_r, dot_y - dot_r, cx - size//6 + dot_r, dot_y + dot_r),
              fill=(124, 140, 255))
    d.ellipse((cx + size//6 - dot_r, dot_y - dot_r, cx + size//6 + dot_r, dot_y + dot_r),
              fill=(159, 170, 255))

    # 'i' stems
    stem_w = max(s * 2, 2)
    stem_top = cy - size // 8
    stem_bot = cy + size // 4
    d.rectangle((cx - size//6 - stem_w//2, stem_top, cx - size//6 + stem_w//2, stem_bot),
                fill=(124, 140, 255))
    d.rectangle((cx + size//6 - stem_w//2, stem_top, cx + size//6 + stem_w//2, stem_bot),
                fill=(159, 170, 255))

    return img


def image_to_tiled_rgb565_icon(img, size):
    """Convert icon to tiled RGB565 for SMDH (same tiling as textures)."""
    buf = bytearray(size * size * 2)
    img_rgb = img.convert('RGB')
    pixels = img_rgb.load()

    tiles = size // 8

    for ty in range(tiles):
        for tx in range(tiles):
            tile_idx = ty * tiles + tx
            for py in range(8):
                for px in range(8):
                    ix = tx * 8 + px
                    iy = ty * 8 + py
                    r, g, b = pixels[ix, iy]
                    val = rgb565(r, g, b)
                    morton = tile_offset(px, py)
                    offset = (tile_idx * 64 + morton) * 2
                    struct.pack_into('<H', buf, offset, val)

    return bytes(buf)


def generate_info_smdh():
    """Generate proper info.smdh with icon graphics."""
    SMDH_SIZE = 0x36C0
    data = bytearray(SMDH_SIZE)

    # Magic + version
    data[0:4] = b'SMDH'
    struct.pack_into('<H', data, 4, 0)

    # Title entries
    title = "iiSU White UI"
    short_desc = "Minimal iiSU-inspired white interface theme."
    long_desc = (
        "A fully custom Nintendo 3DS theme inspired by the iiSU network. "
        "Modern white base, soft pastel gradients, rounded UI, subtle shadows. "
        "White Edition v1.0"
    )
    author = "none"

    def to_utf16(s, max_bytes):
        return s.encode('utf-16-le')[:max_bytes].ljust(max_bytes, b'\x00')

    for i in range(16):
        base = 0x08 + i * 0x200
        data[base:base + 0x80] = to_utf16(title, 0x80)
        desc = long_desc if i == 1 else short_desc
        data[base + 0x80:base + 0x180] = to_utf16(desc, 0x100)
        data[base + 0x180:base + 0x200] = to_utf16(author, 0x80)

    # Settings at 0x2008 (0x30 bytes)
    # Age ratings, region lock, etc. — leave as zeros (all-ages, region-free)
    # matchmaker_id, flags, etc. at various offsets within 0x2008-0x2037

    # Icon graphics at 0x2040
    print("  Generating 24x24 small icon...")
    small_icon = create_icon(24)
    small_icon_data = image_to_tiled_rgb565_icon(small_icon, 24)
    assert len(small_icon_data) == 0x480, f"Small icon wrong size: {len(small_icon_data)}"
    data[0x2040:0x2040 + 0x480] = small_icon_data

    print("  Generating 48x48 large icon...")
    large_icon = create_icon(48)
    large_icon_data = image_to_tiled_rgb565_icon(large_icon, 48)
    assert len(large_icon_data) == 0x1200, f"Large icon wrong size: {len(large_icon_data)}"
    data[0x24C0:0x24C0 + 0x1200] = large_icon_data

    filepath = os.path.join(OUTPUT_DIR, "info.smdh")
    with open(filepath, 'wb') as f:
        f.write(data)
    print(f"    Saved: {filepath} ({len(data)} bytes)")

    # Also save icons as PNG for reference
    small_icon.save(os.path.join(OUTPUT_DIR, "icon_24x24.png"))
    large_icon.save(os.path.join(OUTPUT_DIR, "icon_48x48.png"))


def main():
    print("=" * 55)
    print("  iiSU White UI — Real 3DS Binary Generator")
    print("=" * 55)

    top_path = os.path.join(OUTPUT_DIR, "top.png")
    bot_path = os.path.join(OUTPUT_DIR, "bottom.png")

    if not os.path.exists(top_path) or not os.path.exists(bot_path):
        print("ERROR: Run generate_theme.py first to create top.png and bottom.png")
        return

    top_img = Image.open(top_path)
    bot_img = Image.open(bot_path)
    print(f"  Top screen: {top_img.size}")
    print(f"  Bottom screen: {bot_img.size}")

    print()
    print("[1/2] Generating body_LZ.bin...")
    generate_body_lz(top_img, bot_img)

    print()
    print("[2/2] Generating info.smdh...")
    generate_info_smdh()

    print()
    print("=" * 55)
    print("  Done! Real binary files generated.")
    print("=" * 55)
    for f in sorted(os.listdir(OUTPUT_DIR)):
        fpath = os.path.join(OUTPUT_DIR, f)
        sz = os.path.getsize(fpath)
        print(f"  {f:24s} {sz:>10,} bytes")


if __name__ == "__main__":
    main()
