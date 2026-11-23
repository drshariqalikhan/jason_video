import os
import subprocess
from pathlib import Path
from PIL import ImageFont

# Root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Asset Paths
ASSETS_DIR = ROOT_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
AUDIO_DIR = ASSETS_DIR / "audio"
TEMP_DIR = ROOT_DIR / "temp"
OUTPUT_DIR = ROOT_DIR / "output"

for d in [TEMP_DIR, OUTPUT_DIR, FONTS_DIR, AUDIO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Video Specs
WIDTH = 1920
HEIGHT = 1080
FPS = 30

# Style Sheet Tokens (From Jason Explains README)
BG = (8, 12, 22)             # #080C16 Dark navy
TEXT = (226, 232, 240)       # #E2E8F0 Primary text
MUTED = (148, 163, 184)      # #94A3B8 Secondary text
RED = (242, 54, 69)          # #F23645 Danger/Drops
GREEN = (34, 197, 94)        # #22C55E Gains/Go
CYAN = (56, 189, 248)        # #38BDF8 Accents/Links
AMBER = (245, 158, 11)       # #F59E0B Warnings
GOLD = (252, 211, 77)        # #FCD34D Highlights
WHITE = (255, 255, 255)

# FFmpeg Audio Loudnorm Standards
LOUDNORM_TARGET = "loudnorm=I=-14:TP=-1.5:LRA=11"
SILENCE_GAP_SEC = 0.25

# Font Resolvers
def get_font(bold: bool = False, size: int = 36) -> ImageFont.FreeTypeFont:
    clamped_size = max(1, int(size))
    font_file = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    font_path = FONTS_DIR / font_file
    if not font_path.exists():
        return ImageFont.load_default()
    return ImageFont.truetype(str(font_path), clamped_size)

# Easing Helpers
def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - pow(1.0 - t, 3)

def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1.0 - pow(-2 * t + 2, 3) / 2

# Dynamic FFmpeg Video Encoder Resolver
def get_ffmpeg_video_encoder_flags(fast_preset: bool = True):
    """Detects supported H.264 encoder in the local FFmpeg build."""
    candidates = [
        ("h264_nvenc", ["-c:v", "h264_nvenc", "-preset", "p1" if fast_preset else "p4", "-cq", "19", "-pix_fmt", "yuv420p"]),
        ("libopenh264", ["-c:v", "libopenh264", "-b:v", "12M", "-pix_fmt", "yuv420p"]),
        ("h264_mf", ["-c:v", "h264_mf", "-b:v", "12M", "-pix_fmt", "yuv420p"]),
        ("libx264", ["-c:v", "libx264", "-preset", "ultrafast" if fast_preset else "medium", "-crf", "18", "-pix_fmt", "yuv420p"]),
        ("mpeg4", ["-c:v", "mpeg4", "-q:v", "2", "-pix_fmt", "yuv420p"])
    ]
    for enc_name, flags in candidates:
        test_cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "nullsrc=s=64x64:d=0.04", "-c:v", enc_name, "-f", "null", "-"]
        res = subprocess.run(test_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return enc_name, flags
    return "mpeg4", ["-c:v", "mpeg4", "-q:v", "2", "-pix_fmt", "yuv420p"]
