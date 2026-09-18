#!/usr/bin/env python3
"""
Crawlspace 3-Pack Telemetry Audit Video Generator
Renders a high-definition (1080p 30fps) motion graphic video explaining:
1. Google Maps 3-Pack rank gap in Crawlspace Waterproofing & Encapsulation.
2. The Hormozi math ($8,500 ticket * 5 calls = $42,500/mo bleed).
3. The 4 Proprietary Systems of Local Dominance.
4. Call to action to view the Google Doc SOP at gslocalseo.com/doc-sales-page.
"""

import os
import sys
import subprocess
import math

# Ensure vendor libraries loaded
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_DIR = os.path.join(BASE_DIR, "vendor_py")
if os.path.exists(VENDOR_DIR) and VENDOR_DIR not in sys.path:
    sys.path.insert(0, VENDOR_DIR)

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION_SECS = 15
TOTAL_FRAMES = FPS * DURATION_SECS

# Fonts
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"
def get_font(size, bold=False):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

FONT_HERO = get_font(56, True)
FONT_TITLE = get_font(40, True)
FONT_SUBTITLE = get_font(28)
FONT_BODY = get_font(24)
FONT_BIG_METRIC = get_font(72, True)
FONT_BADGE = get_font(20, True)

# Color Palette
BG_COLOR = (11, 19, 43)        # Deep Navy / Slate
CARD_BG = (23, 37, 84, 230)    # Elevated Card Slate
ACCENT_GOLD = (245, 158, 11)   # Gold Standard Amber (#F59E0B)
ACCENT_BLUE = (59, 130, 246)   # Cobalt Blue
TEXT_WHITE = (255, 255, 255)
TEXT_MUTED = (148, 163, 184)
RED_ALERT = (239, 68, 68)
GREEN_WIN = (34, 197, 94)

def draw_header(draw, title_text="GOLD STANDARD LOCAL SEO • SACRAMENTO REGIONAL NETWORK"):
    draw.rectangle([(0, 0), (WIDTH, 90)], fill=(15, 23, 42))
    draw.rectangle([(0, 88), (WIDTH, 90)], fill=ACCENT_GOLD)
    draw.text((80, 28), title_text, fill=ACCENT_GOLD, font=FONT_BADGE)
    draw.text((WIDTH - 380, 28), "DIRECT OFFICE: (916) 234-3457", fill=TEXT_WHITE, font=FONT_BADGE)

def draw_footer(draw, progress):
    draw.rectangle([(0, HEIGHT - 50), (WIDTH, HEIGHT)], fill=(15, 23, 42))
    draw.text((80, HEIGHT - 38), "TELEMETRY BREAKDOWN: HTTPS://WWW.GSLOCALSEO.COM/DOC-SALES-PAGE", fill=TEXT_MUTED, font=FONT_BADGE)
    # Progress Bar
    bar_width = int(WIDTH * progress)
    draw.rectangle([(0, HEIGHT - 4), (bar_width, HEIGHT)], fill=ACCENT_GOLD)

def render_frame(frame_num):
    im = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(im)
    progress = frame_num / TOTAL_FRAMES
    current_sec = frame_num / FPS

    draw_header(draw)
    draw_footer(draw, progress)

    # ----------------------------------------------------
    # SCENE 1 (0s - 4s): Title & Telemetry Audit Intro
    # ----------------------------------------------------
    if current_sec < 4.0:
        alpha = min(1.0, current_sec / 0.8)
        draw.text((80, 160), "CRAWLSPACE & FOUNDATION PROXIMITY AUDIT", fill=ACCENT_GOLD, font=FONT_SUBTITLE)
        draw.text((80, 210), "Why Google Hands $42,500/Mo in High-Ticket Jobs", fill=TEXT_WHITE, font=FONT_HERO)
        draw.text((80, 280), "To Your Competitor (And How to Stop the Bleed)", fill=TEXT_WHITE, font=FONT_HERO)

        # 3 Key Facts Cards
        card_w, card_h = 540, 420
        y_pos = 400
        
        cards = [
            ("Average Ticket", "$8,500", "Vapor barrier & encapsulation jobs in Roseville / Sacramento.", ACCENT_GOLD),
            ("Search Behavior", "72% In 3-Pack", "Homeowners with standing water call exclusively from top 3 pins.", ACCENT_BLUE),
            ("The Rank Cliff", "Rank #11 = Zero", "Page 2 rank positions surrender all inbound calls to Groundworks.", RED_ALERT)
        ]

        for i, (head, val, desc, col) in enumerate(cards):
            x_pos = 80 + i * (card_w + 40)
            draw.rectangle([(x_pos, y_pos), (x_pos + card_w, y_pos + card_h)], fill=(15, 23, 42), outline=col, width=2)
            draw.text((x_pos + 30, y_pos + 35), head.upper(), fill=TEXT_MUTED, font=FONT_BADGE)
            draw.text((x_pos + 30, y_pos + 80), val, fill=col, font=FONT_BIG_METRIC)
            draw.text((x_pos + 30, y_pos + 200), desc, fill=TEXT_WHITE, font=FONT_BODY)

    # ----------------------------------------------------
    # SCENE 2 (4s - 8s): The 9x9 Radar Geo-Grid Simulator
    # ----------------------------------------------------
    elif current_sec < 8.0:
        scene_sec = current_sec - 4.0
        draw.text((80, 140), "9x9 LOCAL FALCON PROXIMITY SIMULATOR", fill=ACCENT_GOLD, font=FONT_SUBTITLE)
        draw.text((80, 190), "Roseville & Sacramento Geo-Grid Density", fill=TEXT_WHITE, font=FONT_HERO)

        # Draw Grid of 81 Pins (9x9)
        grid_origin_x = 80
        grid_origin_y = 280
        dot_spacing = 60

        for row in range(9):
            for col in range(9):
                cx = grid_origin_x + col * dot_spacing + 30
                cy = grid_origin_y + row * dot_spacing + 30
                
                # Distance from center
                dist = math.sqrt((row - 4)**2 + (col - 4)**2)
                
                # Center is green (#1-#3), edges turn red as distance grows
                if dist <= 1.8:
                    color = GREEN_WIN
                    text_rank = "1" if dist < 1 else "2"
                elif dist <= 3.2:
                    color = ACCENT_GOLD
                    text_rank = "5"
                else:
                    color = RED_ALERT
                    text_rank = "11"

                # Staggered reveal
                if (row * 9 + col) < (scene_sec / 3.0) * 81:
                    draw.ellipse([(cx - 20, cy - 20), (cx + 20, cy + 20)], fill=color)
                    draw.text((cx - 8, cy - 12), text_rank, fill=(0, 0, 0), font=FONT_BADGE)

        # Right Side Analytics Card
        rx = 720
        ry = 280
        draw.rectangle([(rx, ry), (WIDTH - 80, ry + 540)], fill=(15, 23, 42), outline=ACCENT_GOLD, width=2)
        
        draw.text((rx + 40, ry + 40), "THE TELEMETRY GAP", fill=ACCENT_GOLD, font=FONT_SUBTITLE)
        draw.text((rx + 40, ry + 90), "Critter Bros LLC & Pinnacle Home Services", fill=TEXT_WHITE, font=FONT_TITLE)
        
        draw.text((rx + 40, ry + 170), "Current Average Maps Rank:", fill=TEXT_MUTED, font=FONT_BODY)
        draw.text((rx + 400, ry + 165), "Rank #11 (Page 2)", fill=RED_ALERT, font=FONT_TITLE)

        draw.text((rx + 40, ry + 240), "Monthly Inbound Call Deficit:", fill=TEXT_MUTED, font=FONT_BODY)
        draw.text((rx + 400, ry + 235), "-5 to -9 Emergency Calls", fill=RED_ALERT, font=FONT_TITLE)

        draw.text((rx + 40, ry + 320), "Monthly Revenue Walking Out Door:", fill=TEXT_MUTED, font=FONT_BODY)
        draw.text((rx + 40, ry + 370), "$42,500 / Month", fill=ACCENT_GOLD, font=FONT_BIG_METRIC)
        draw.text((rx + 40, ry + 460), "Annual Gross Opportunity: $510,000 / Year", fill=GREEN_WIN, font=FONT_SUBTITLE)

    # ----------------------------------------------------
    # SCENE 3 (8s - 12s): The 4 Proprietary Systems
    # ----------------------------------------------------
    elif current_sec < 12.0:
        draw.text((80, 140), "THE GOLD STANDARD RECOVERY FRAMEWORK", fill=ACCENT_GOLD, font=FONT_SUBTITLE)
        draw.text((80, 190), "4 Systems to Lock Down the Top 3-Pack", fill=TEXT_WHITE, font=FONT_HERO)

        systems = [
            ("01", "GBP Category Hierarchy", "Mirroring primary and secondary categories so Google indexes 'Waterproofing' queries."),
            ("02", "15-Mile Radial KML Mesh", "Centroid anchor linking physical job locations to Roseville & Sacramento civic landmarks."),
            ("03", "Geo-Asset EXIF Pipeline", "Lossless pHash injection with authentic GPS coordinates on every crawlspace project photo."),
            ("04", "Speed-to-Lead Telemetry", "Sub-60-second automated call routing to capture calls before decay hits.")
        ]

        sy = 300
        for i, (num, name, desc) in enumerate(systems):
            sx = 80 + (i % 2) * 880
            cur_y = sy + (i // 2) * 270
            
            draw.rectangle([(sx, cur_y), (sx + 840, cur_y + 230)], fill=(15, 23, 42), outline=ACCENT_BLUE, width=2)
            draw.text((sx + 30, cur_y + 25), num, fill=ACCENT_GOLD, font=FONT_TITLE)
            draw.text((sx + 110, cur_y + 25), name, fill=TEXT_WHITE, font=FONT_TITLE)
            draw.text((sx + 110, cur_y + 85), desc, fill=TEXT_MUTED, font=FONT_BODY)

    # ----------------------------------------------------
    # SCENE 4 (12s - 15s): Call to Action & Google Doc Access
    # ----------------------------------------------------
    else:
        draw.text((80, 160), "CONFIDENTIAL CLIENT MEMORANDUM & SOP", fill=ACCENT_GOLD, font=FONT_SUBTITLE)
        draw.text((80, 220), "Read the Live 2-Page Telemetry Breakdown", fill=TEXT_WHITE, font=FONT_HERO)
        
        # Big Center CTA Box
        cx, cy = 80, 330
        cw, ch = WIDTH - 160, 480
        draw.rectangle([(cx, cy), (cx + cw, cy + ch)], fill=(15, 23, 42), outline=ACCENT_GOLD, width=3)

        draw.text((cx + 60, cy + 60), "NO SALES PITCH • NO 45-MINUTE SLIDE DECKS", fill=TEXT_MUTED, font=FONT_SUBTITLE)
        draw.text((cx + 60, cy + 120), "Visit https://www.gslocalseo.com/doc-sales-page", fill=ACCENT_GOLD, font=FONT_HERO)
        draw.text((cx + 60, cy + 210), "See the exact map cutoff points and the step-by-step 60 to 90-day recovery plan.", fill=TEXT_WHITE, font=FONT_BODY)
        
        draw.rectangle([(cx + 60, cy + 280), (cx + 600, cy + 370)], fill=ACCENT_GOLD)
        draw.text((cx + 90, cy + 305), "CALL DIRECT: (916) 234-3457", fill=(11, 19, 43), font=FONT_TITLE)

        draw.text((cx + 660, cy + 315), "Justin Davis | Founder & Lead Telemetry Architect", fill=TEXT_WHITE, font=FONT_SUBTITLE)

    return im

def main():
    output_video = "crawlspace_3pack_telemetry_audit.mp4"
    print(f"Generating {TOTAL_FRAMES} frames ({DURATION_SECS}s @ {FPS}fps)...")

    # Launch ffmpeg process reading raw frames from stdin
    cmd = [
        "/usr/local/bin/ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_video
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for i in range(TOTAL_FRAMES):
        if i % 60 == 0:
            print(f" • Rendered frame {i}/{TOTAL_FRAMES} ({i/TOTAL_FRAMES*100:.1f}%)")
        frame = render_frame(i)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()

    if proc.returncode == 0:
        print(f"\n✓ Successfully generated high-definition video: {output_video}")
        print(f"  File size: {os.path.getsize(output_video):,} bytes")
    else:
        print(f"Error generating video, return code {proc.returncode}")

if __name__ == "__main__":
    main()
