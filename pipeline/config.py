import os
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
    """Safely loads DejaVu font with clamped size > 0 to prevent PIL crashes."""
    clamped_size = max(1, int(size))
    font_file = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    font_path = FONTS_DIR / font_file
    if not font_path.exists():
        # Fallback to default PIL if file not yet downloaded
        return ImageFont.load_default()
    return ImageFont.truetype(str(font_path), clamped_size)

# Easing Helpers
def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - pow(1.0 - t, 3)

def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1.0 - pow(-2 * t + 2, 3) / 2
