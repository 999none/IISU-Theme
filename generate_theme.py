#!/usr/bin/env python3
"""
iiSU White UI - Nintendo 3DS Custom Theme Asset Generator v2
Generates: top.png, bottom.png, preview.png, body_LZ.bin, info.smdh
Inspired by iiSU Network design language. All artwork is original.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import struct
import math
import os

OUTPUT_DIR = "/app/iiSU_White_UI"

# === Color Palette ===
WHITE = (255, 255, 255)
BASE_1 = (248, 248, 248)
BASE_2 = (242, 242, 242)
BASE_3 = (235, 235, 238)
ACCENT_1 = (124, 140, 255)
ACCENT_2 = (159, 170, 255)
ACCENT_3 = (184, 192, 255)
ACCENT_4 = (210, 215, 255)
ACCENT_5 = (230, 233, 255)
TEXT_DARK = (51, 51, 51)
TEXT_MID = (120, 120, 130)
TEXT_LIGHT = (180, 180, 185)


def create_vertical_gradient(width, height, top_color, bottom_color):
    """Create smooth vertical gradient."""
    img = Image.new('RGBA', (width, height))
    pixels = img.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        for x in range(width):
            pixels[x, y] = (r, g, b, 255)
    return img


def create_dotted_texture(width, height, spacing=10, dot_alpha=5):
    """Create ultra-subtle staggered dot pattern."""
    texture = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    pixels = texture.load()
    for y in range(0, height, spacing):
        offset = (spacing // 2) if (y // spacing) % 2 else 0
        for x in range(offset, width, spacing):
            if 0 <= x < width and 0 <= y < height:
                pixels[x, y] = (0, 0, 0, dot_alpha)
    return texture


def soft_glow(img, cx, cy, rx, ry, color, intensity=12, blur=20):
    """Add a soft elliptical glow."""
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(intensity, 0, -1):
        alpha = int(intensity * (1 - i / intensity))
        scale = 1 + i * 0.08
        gd.ellipse(
            (int(cx - rx * scale), int(cy - ry * scale),
             int(cx + rx * scale), int(cy + ry * scale)),
            fill=(*color[:3], alpha)
        )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=blur))
    return Image.alpha_composite(img, glow)


def draw_iisu_logo_v2(img, cx, cy, scale=1.0):
    """
    Draw refined iiSU logo using anti-aliased rendering at 4x then downscale.
    """
    # Render at 4x for smooth edges
    SS = 4
    logo_w = int(180 * scale)
    logo_h = int(80 * scale)
    buf_w = logo_w * SS
    buf_h = (logo_h + 30) * SS  # Extra room for dots

    buf = Image.new('RGBA', (buf_w, buf_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(buf)

    # Scaled dimensions
    stem_w = int(16 * scale * SS)
    stem_h = int(52 * scale * SS)
    stem_r = int(5 * scale * SS)
    dot_r = int(6 * scale * SS)
    dot_gap = int(14 * scale * SS)
    gap = int(8 * scale * SS)

    # S dimensions
    s_w = int(36 * scale * SS)
    s_h = stem_h
    s_thick = int(13 * scale * SS)
    s_r = int(7 * scale * SS)

    # U dimensions
    u_w = int(36 * scale * SS)
    u_h = stem_h
    u_thick = int(13 * scale * SS)
    u_r = int(7 * scale * SS)

    # Total width
    total = stem_w + gap + stem_w + gap * 2 + s_w + gap * 2 + u_w
    sx = (buf_w - total) // 2
    base_y = dot_r * 2 + dot_gap + int(4 * SS)

    # === 'i' (first) ===
    x = sx
    # dot
    dcx = x + stem_w // 2
    dcy = base_y - dot_gap - dot_r
    d.ellipse((dcx - dot_r, dcy - dot_r, dcx + dot_r, dcy + dot_r), fill=ACCENT_1)
    # stem
    d.rounded_rectangle((x, base_y, x + stem_w, base_y + stem_h), radius=stem_r, fill=ACCENT_1)

    # === 'i' (second) ===
    x += stem_w + gap
    dcx2 = x + stem_w // 2
    d.ellipse((dcx2 - dot_r, dcy - dot_r, dcx2 + dot_r, dcy + dot_r), fill=ACCENT_2)
    d.rounded_rectangle((x, base_y, x + stem_w, base_y + stem_h), radius=stem_r, fill=ACCENT_2)

    # === 'S' ===
    x += stem_w + gap * 2

    # Build S using overlapping rounded rects for smooth curves
    # Outer rounded rect
    d.rounded_rectangle((x, base_y, x + s_w, base_y + s_h), radius=s_r, fill=ACCENT_1)

    # Cut top-right inner (creates top opening of S)
    inner_r = max(s_r - 4, 2)
    d.rounded_rectangle(
        (x + s_thick, base_y + s_thick, x + s_w + s_thick, base_y + s_h // 2 - s_thick // 4),
        radius=inner_r, fill=(0, 0, 0, 0)
    )
    # Re-overlay: actually let me use a cleaner approach with masks

    # Clear and redo S with proper construction
    # Erase current S area
    d.rectangle((x - 2, base_y - 2, x + s_w + 2, base_y + s_h + 2), fill=(0, 0, 0, 0))

    # S - three horizontal bars + two vertical connectors
    bar_h = s_thick
    mid_y = base_y + s_h // 2 - bar_h // 2

    # Top bar
    d.rounded_rectangle((x, base_y, x + s_w, base_y + bar_h), radius=s_r, fill=ACCENT_1)
    # Middle bar
    d.rounded_rectangle((x, mid_y, x + s_w, mid_y + bar_h), radius=s_r, fill=ACCENT_1)
    # Bottom bar
    d.rounded_rectangle((x, base_y + s_h - bar_h, x + s_w, base_y + s_h), radius=s_r, fill=ACCENT_1)
    # Left vertical connector (top to mid)
    d.rounded_rectangle((x, base_y, x + s_thick, mid_y + bar_h), radius=s_r, fill=ACCENT_1)
    # Right vertical connector (mid to bottom)
    d.rounded_rectangle((x + s_w - s_thick, mid_y, x + s_w, base_y + s_h), radius=s_r, fill=ACCENT_1)

    # === 'U' ===
    x += s_w + gap * 2

    # Left vertical
    d.rounded_rectangle((x, base_y, x + u_thick, base_y + u_h), radius=u_r, fill=ACCENT_2)
    # Right vertical
    d.rounded_rectangle((x + u_w - u_thick, base_y, x + u_w, base_y + u_h), radius=u_r, fill=ACCENT_2)
    # Bottom connector
    d.rounded_rectangle((x, base_y + u_h - u_thick, x + u_w, base_y + u_h), radius=u_r, fill=ACCENT_2)

    # Downscale with LANCZOS for anti-aliasing
    small = buf.resize((buf_w // SS, buf_h // SS), Image.LANCZOS)

    # Paste onto main image
    paste_x = cx - small.width // 2
    paste_y = cy - small.height // 2
    img.paste(small, (paste_x, paste_y), small)

    return img


def generate_top_screen():
    """Generate top.png (412x240) - premium white console top screen."""
    W, H = 412, 240

    # Gradient base
    img = create_vertical_gradient(W, H, (255, 255, 255, 255), (242, 242, 245, 255))

    # Soft center glow
    img = soft_glow(img, W // 2, H // 2 - 8, 140, 70, ACCENT_3, intensity=15, blur=25)

    # Dotted texture
    tex = create_dotted_texture(W, H, spacing=10, dot_alpha=4)
    img = Image.alpha_composite(img, tex)

    draw = ImageDraw.Draw(img)

    # Thin decorative lines
    line_alpha = 25
    draw.line([(50, 28), (W - 50, 28)], fill=(*ACCENT_3[:3], line_alpha), width=1)
    draw.line([(50, H - 28), (W - 50, H - 28)], fill=(*ACCENT_3[:3], line_alpha), width=1)

    # Small corner accents
    corner_size = 12
    ca = (*ACCENT_3[:3], 20)
    # Top-left
    draw.line([(20, 20), (20 + corner_size, 20)], fill=ca, width=1)
    draw.line([(20, 20), (20, 20 + corner_size)], fill=ca, width=1)
    # Top-right
    draw.line([(W - 20, 20), (W - 20 - corner_size, 20)], fill=ca, width=1)
    draw.line([(W - 20, 20), (W - 20, 20 + corner_size)], fill=ca, width=1)
    # Bottom-left
    draw.line([(20, H - 20), (20 + corner_size, H - 20)], fill=ca, width=1)
    draw.line([(20, H - 20), (20, H - 20 - corner_size)], fill=ca, width=1)
    # Bottom-right
    draw.line([(W - 20, H - 20), (W - 20 - corner_size, H - 20)], fill=ca, width=1)
    draw.line([(W - 20, H - 20), (W - 20, H - 20 - corner_size)], fill=ca, width=1)

    # Subtle floating diamonds
    diamonds = [(80, 60), (340, 55), (65, 180), (350, 175), (200, 30), (210, 210)]
    for dx, dy in diamonds:
        s = 3
        draw.polygon([(dx, dy - s), (dx + s, dy), (dx, dy + s), (dx - s, dy)],
                     fill=(*ACCENT_3[:3], 18))

    # Small circles
    circles = [(100, 100), (320, 140), (55, 130), (360, 100)]
    for ccx, ccy in circles:
        cr = 6
        draw.ellipse((ccx - cr, ccy - cr, ccx + cr, ccy + cr),
                     outline=(*ACCENT_3[:3], 15), width=1)

    # Draw iiSU logo
    img = draw_iisu_logo_v2(img, W // 2, H // 2 - 16, scale=1.2)
    draw = ImageDraw.Draw(img)

    # Subtitle
    try:
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Light.ttf", 12)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    except:
        font_sub = font_tiny = ImageFont.load_default()

    subtitle = "W H I T E   U I"
    bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text((W // 2 - tw // 2, H // 2 + 42), subtitle, fill=(*TEXT_MID[:3], 110), font=font_sub)

    ver = "v1.0"
    bbox2 = draw.textbbox((0, 0), ver, font=font_tiny)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((W // 2 - tw2 // 2, H // 2 + 60), ver, fill=(*TEXT_LIGHT[:3], 70), font=font_tiny)

    # Finalize
    final = Image.new('RGB', (W, H), WHITE)
    final.paste(img, (0, 0), img)
    final.save(os.path.join(OUTPUT_DIR, "top.png"), "PNG")
    print(f"  top.png ({W}x{H}) saved")
    return final


def generate_bottom_screen():
    """Generate bottom.png (320x240) - white dashboard bottom screen."""
    W, H = 320, 240

    img = create_vertical_gradient(W, H, (253, 253, 255, 255), (244, 244, 247, 255))
    tex = create_dotted_texture(W, H, spacing=12, dot_alpha=3)
    img = Image.alpha_composite(img, tex)
    draw = ImageDraw.Draw(img)

    # === Icon grid ===
    cols, rows = 5, 3
    icon_sz = 40
    icon_r = 7
    margin_x = 16
    margin_top = 18
    gap_x = 8
    gap_y = 8
    toolbar_h = 26

    # Calculate total grid width and center it
    grid_w = cols * icon_sz + (cols - 1) * gap_x
    grid_start_x = (W - grid_w) // 2
    grid_start_y = margin_top

    sel_row, sel_col = 1, 2  # Center-ish selection

    for row in range(rows):
        for col in range(cols):
            x = grid_start_x + col * (icon_sz + gap_x)
            y = grid_start_y + row * (icon_sz + gap_y)
            is_sel = (row == sel_row and col == sel_col)

            # Shadow
            shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            sd.rounded_rectangle(
                (x + 1, y + 2, x + icon_sz + 1, y + icon_sz + 2),
                radius=icon_r, fill=(0, 0, 0, 10 if not is_sel else 15)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=2))
            img = Image.alpha_composite(img, shadow)
            draw = ImageDraw.Draw(img)

            if is_sel:
                # Selection glow
                for g in range(8, 0, -1):
                    alpha = int(22 * (1 - g / 8))
                    draw.rounded_rectangle(
                        (x - 3 - g, y - 3 - g, x + icon_sz + 3 + g, y + icon_sz + 3 + g),
                        radius=icon_r + g, fill=(*ACCENT_1[:3], alpha)
                    )
                # Selected border
                draw.rounded_rectangle(
                    (x - 2, y - 2, x + icon_sz + 2, y + icon_sz + 2),
                    radius=icon_r + 1, outline=ACCENT_1, width=2
                )
                fill = (*ACCENT_5[:3], 240)
            else:
                fill = (255, 255, 255, 230)

            # Icon body
            draw.rounded_rectangle(
                (x, y, x + icon_sz, y + icon_sz),
                radius=icon_r, fill=fill,
                outline=(*BASE_2[:3], 160 if not is_sel else 0), width=1
            )

            # Inner minimal pattern
            pad = 9
            ix1, iy1, ix2, iy2 = x + pad, y + pad, x + icon_sz - pad, y + icon_sz - pad
            idx = row * cols + col
            mc = ACCENT_1 if is_sel else ACCENT_3  # Main color for patterns

            if idx == 0:
                # Circle
                r = 8
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*mc[:3], 50))
            elif idx == 1:
                # Lines
                for i in range(3):
                    w = (ix2 - ix1) - i * 5
                    draw.rounded_rectangle((ix1, iy1 + i * 8, ix1 + w, iy1 + i * 8 + 3),
                                           radius=1, fill=(*mc[:3], 35 + i * 8))
            elif idx == 2:
                # Rounded square
                s = 9
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                draw.rounded_rectangle((cx - s, cy - s, cx + s, cy + s),
                                       radius=3, fill=(*mc[:3], 40))
            elif idx == 3:
                # Triangle
                cx = (ix1 + ix2) // 2
                draw.polygon([(cx, iy1), (ix2, iy2), (ix1, iy2)], fill=(*mc[:3], 30))
            elif idx == 4:
                # 3x3 dots
                for dx in range(3):
                    for dy in range(3):
                        px = ix1 + 2 + dx * 9
                        py = iy1 + 2 + dy * 9
                        draw.ellipse((px, py, px + 4, py + 4), fill=(*mc[:3], 45))
            elif idx == 5:
                # Diamond
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                s = 9
                draw.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                            fill=(*mc[:3], 40))
            elif idx == 6:
                # Ring
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9),
                            outline=(*mc[:3], 55), width=2)
            elif idx == 7:  # Selected
                # Star burst
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    ex = cx + int(9 * math.cos(rad))
                    ey = cy + int(9 * math.sin(rad))
                    draw.line((cx, cy, ex, ey), fill=(*ACCENT_1[:3], 90), width=2)
                draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(*ACCENT_1[:3], 120))
            elif idx == 8:
                # Plus
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                draw.rounded_rectangle((cx - 1, cy - 9, cx + 2, cy + 9), radius=1, fill=(*mc[:3], 50))
                draw.rounded_rectangle((cx - 9, cy - 1, cx + 9, cy + 2), radius=1, fill=(*mc[:3], 50))
            elif idx == 9:
                # 2x2 grid
                for gx in range(2):
                    for gy in range(2):
                        sx = ix1 + gx * 12
                        sy = iy1 + gy * 12
                        draw.rounded_rectangle((sx, sy, sx + 9, sy + 9), radius=2, fill=(*mc[:3], 35))
            elif idx == 10:
                # Hexagon shape
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                pts = []
                for a in range(6):
                    rad = math.radians(a * 60 - 30)
                    pts.append((cx + int(9 * math.cos(rad)), cy + int(9 * math.sin(rad))))
                draw.polygon(pts, fill=(*mc[:3], 35))
            elif idx == 11:
                # Concentric circles
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                for r in [10, 6, 3]:
                    alpha = 20 + (10 - r) * 5
                    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*mc[:3], alpha), width=1)
            elif idx == 12:
                # Arrow right
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                draw.polygon([(ix1 + 2, cy - 6), (ix2 - 2, cy), (ix1 + 2, cy + 6)],
                            fill=(*mc[:3], 40))
            elif idx == 13:
                # Wave
                points = []
                for px in range(ix1, ix2 + 1, 2):
                    py = (iy1 + iy2) // 2 + int(5 * math.sin((px - ix1) * 0.4))
                    points.append((px, py))
                if len(points) > 1:
                    draw.line(points, fill=(*mc[:3], 50), width=2)
            elif idx == 14:
                # Heart-ish
                cx, cy = (ix1 + ix2) // 2, (iy1 + iy2) // 2
                draw.ellipse((cx - 7, cy - 5, cx - 1, cy + 1), fill=(*mc[:3], 40))
                draw.ellipse((cx + 1, cy - 5, cx + 7, cy + 1), fill=(*mc[:3], 40))
                draw.polygon([(cx - 7, cy - 1), (cx, cy + 8), (cx + 7, cy - 1)], fill=(*mc[:3], 35))

    # === Bottom Toolbar ===
    tb_y = H - toolbar_h - 6
    tb_h = toolbar_h

    # Toolbar background with subtle top border
    draw.rounded_rectangle(
        (10, tb_y, W - 10, tb_y + tb_h),
        radius=8, fill=(255, 255, 255, 210),
        outline=(*BASE_2[:3], 100), width=1
    )

    try:
        font_tb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    except:
        font_tb = ImageFont.load_default()

    # Left items
    draw.text((22, tb_y + 9), "(Y) Edit", fill=(*TEXT_MID[:3], 130), font=font_tb)
    draw.text((76, tb_y + 9), "(O) Details", fill=(*TEXT_MID[:3], 130), font=font_tb)

    # Center page dots
    dot_count = 5
    dot_gap = 10
    dots_total = dot_count * dot_gap
    dot_sx = W // 2 - dots_total // 2
    for i in range(dot_count):
        dx = dot_sx + i * dot_gap + 2
        dy = tb_y + 11
        if i == 1:
            draw.ellipse((dx, dy, dx + 5, dy + 5), fill=(*ACCENT_1[:3], 200))
        else:
            draw.ellipse((dx, dy, dx + 4, dy + 4), fill=(*TEXT_LIGHT[:3], 50))

    # Right items
    draw.text((W - 120, tb_y + 9), "(A) Select", fill=(*TEXT_MID[:3], 130), font=font_tb)
    draw.text((W - 62, tb_y + 9), "(+) Menu", fill=(*TEXT_MID[:3], 130), font=font_tb)

    # Finalize
    final = Image.new('RGB', (W, H), WHITE)
    final.paste(img, (0, 0), img)
    final.save(os.path.join(OUTPUT_DIR, "bottom.png"), "PNG")
    print(f"  bottom.png ({W}x{H}) saved")
    return final


def generate_preview(top_img, bottom_img):
    """Generate preview.png - dual screen mockup."""
    pad = 10
    bezel = 6
    gap = 8
    top_w, top_h = 412, 240
    bot_w, bot_h = 320, 240

    canvas_w = max(top_w, bot_w) + (pad + bezel) * 2
    canvas_h = top_h + bot_h + gap + (pad + bezel) * 2 + bezel * 2 + 20  # extra for label

    img = Image.new('RGBA', (canvas_w, canvas_h), (*BASE_1[:3], 255))
    draw = ImageDraw.Draw(img)

    # Top screen frame
    tx = (canvas_w - top_w) // 2
    ty = pad + bezel
    frame_pad = bezel

    # Frame shadow
    for g in range(6, 0, -1):
        a = int(8 * (1 - g / 6))
        draw.rounded_rectangle(
            (tx - frame_pad - g, ty - frame_pad - g + 1,
             tx + top_w + frame_pad + g, ty + top_h + frame_pad + g + 1),
            radius=10 + g, fill=(0, 0, 0, a)
        )

    # Frame
    draw.rounded_rectangle(
        (tx - frame_pad, ty - frame_pad, tx + top_w + frame_pad, ty + top_h + frame_pad),
        radius=10, fill=(238, 238, 242, 255), outline=(*BASE_2[:3], 180), width=1
    )

    # Paste top
    img.paste(top_img.convert('RGBA'), (tx, ty))

    # Bottom screen frame
    bx = (canvas_w - bot_w) // 2
    by = ty + top_h + frame_pad + gap + bezel

    for g in range(6, 0, -1):
        a = int(8 * (1 - g / 6))
        draw.rounded_rectangle(
            (bx - frame_pad - g, by - frame_pad - g + 1,
             bx + bot_w + frame_pad + g, by + bot_h + frame_pad + g + 1),
            radius=10 + g, fill=(0, 0, 0, a)
        )

    draw.rounded_rectangle(
        (bx - frame_pad, by - frame_pad, bx + bot_w + frame_pad, by + bot_h + frame_pad),
        radius=10, fill=(238, 238, 242, 255), outline=(*BASE_2[:3], 180), width=1
    )

    img.paste(bottom_img.convert('RGBA'), (bx, by))

    # Label
    try:
        font_l = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
    except:
        font_l = ImageFont.load_default()

    label = "iiSU White UI  |  Nintendo 3DS Theme  |  v1.0"
    lb = draw.textbbox((0, 0), label, font=font_l)
    lw = lb[2] - lb[0]
    draw.text((canvas_w // 2 - lw // 2, canvas_h - 16), label, fill=(*TEXT_MID[:3], 100), font=font_l)

    final = Image.new('RGB', (canvas_w, canvas_h), BASE_1)
    final.paste(img, (0, 0), img)
    final.save(os.path.join(OUTPUT_DIR, "preview.png"), "PNG")
    print(f"  preview.png ({canvas_w}x{canvas_h}) saved")


def generate_body_lz():
    """Generate body_LZ.bin placeholder."""
    filepath = os.path.join(OUTPUT_DIR, "body_LZ.bin")
    data = bytearray()
    data.extend(b'PLACEHOLDER_BODY_LZ\x00')
    meta = (
        "iiSU White UI Theme - body_LZ Configuration\n"
        "=============================================\n"
        "PLACEHOLDER FILE - Generate real body_LZ.bin using:\n"
        "  YATA+ / 3DS Theme Editor / Usagi Theme Editor\n\n"
        "Theme Customization Values:\n"
        "  Folder Selection Highlight: #7C8CFF (pastel violet)\n"
        "  Text Color: #333333 (dark gray)\n"
        "  Selection Border Glow: #9FAAFF\n"
        "  Background Base: #F8F8F8\n"
        "  Highlight Borders: Rounded, soft\n"
        "  Remove default harsh blue highlights\n"
        "  Clean selection animation style\n"
    ).encode('utf-8')
    data.extend(meta)
    data.extend(b'\x00' * (512 - len(data)))
    with open(filepath, 'wb') as f:
        f.write(data)
    print(f"  body_LZ.bin (placeholder, {len(data)} bytes)")


def generate_info_smdh():
    """Generate info.smdh structured placeholder (0x36C0 bytes)."""
    filepath = os.path.join(OUTPUT_DIR, "info.smdh")
    SMDH_SIZE = 0x36C0
    data = bytearray(SMDH_SIZE)

    data[0:4] = b'SMDH'
    struct.pack_into('<H', data, 4, 0)

    title = "iiSU White UI"
    short_desc = "Minimal iiSU-inspired white interface theme."
    long_desc = (
        "A fully custom Nintendo 3DS theme inspired by the iiSU network interface. "
        "Modern white base, soft pastel gradients, rounded UI elements, subtle shadows. "
        "White Edition."
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

    with open(filepath, 'wb') as f:
        f.write(data)
    print(f"  info.smdh ({len(data)} bytes, SMDH structure)")


def main():
    print("=" * 50)
    print("  iiSU White UI — 3DS Theme Asset Generator v2")
    print("=" * 50)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n[1/5] top.png")
    top = generate_top_screen()
    print("[2/5] bottom.png")
    bottom = generate_bottom_screen()
    print("[3/5] preview.png")
    generate_preview(top, bottom)
    print("[4/5] body_LZ.bin")
    generate_body_lz()
    print("[5/5] info.smdh")
    generate_info_smdh()

    print("\n" + "=" * 50)
    print(f"  Output: {OUTPUT_DIR}/")
    print("=" * 50)
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f == 'index.html':
            continue
        fpath = os.path.join(OUTPUT_DIR, f)
        sz = os.path.getsize(fpath)
        print(f"  {f:20s} {sz:>10,} bytes")
    print()


if __name__ == "__main__":
    main()
