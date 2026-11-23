import math
from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw

from pipeline.config import (
    WIDTH, HEIGHT, BG, TEXT, MUTED, RED, GREEN, CYAN, AMBER, GOLD, WHITE,
    get_font, ease_out_cubic
)

COLOR_MAP = {
    "cyan": CYAN,
    "green": GREEN,
    "red": RED,
    "amber": AMBER,
    "gold": GOLD,
    "white": WHITE
}

class BaseScene:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def render(self, t_norm: float) -> Image.Image:
        """t_norm is normalized scene progress from 0.0 to 1.0."""
        raise NotImplementedError


class AreaChartScene(BaseScene):
    """
    Reference glowing area chart:
    - Glowing multi-layered line
    - Gradient vertical fill fading to dark navy
    - Glowing head dot tracking the animated tip
    - Synchronized counting number
    """
    def render(self, t_norm: float) -> Image.Image:
        img = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
        draw = ImageDraw.Draw(img)

        title = self.data.get("title", "MARKET PERFORMANCE")
        start_val = float(self.data.get("start_val", 10000))
        end_val = float(self.data.get("end_val", 14500))
        prefix = self.data.get("prefix", "$")
        suffix = self.data.get("suffix", "")
        color_name = self.data.get("color", "cyan")
        theme_color = COLOR_MAP.get(color_name.lower(), CYAN)

        # Title at top-left
        title_font = get_font(bold=True, size=40)
        draw.text((120, 90), title.upper(), fill=MUTED, font=title_font)

        # Animated Counter
        ease_p = ease_out_cubic(t_norm)
        current_val = start_val + (end_val - start_val) * ease_p
        val_str = f"{prefix}{current_val:,.0f}{suffix}"
        val_font = get_font(bold=True, size=84)
        draw.text((120, 145), val_str, fill=theme_color, font=val_font)

        # Chart bounds
        left, right = 120, WIDTH - 120
        top, bottom = 320, HEIGHT - 180
        chart_w = right - left
        chart_h = bottom - top

        # Subtle horizontal gridlines
        grid_font = get_font(bold=False, size=22)
        for i in range(4):
            gy = top + i * (chart_h / 3)
            draw.line([(left, gy), (right, gy)], fill=(20, 30, 48), width=1)
            grid_val = end_val - i * ((end_val - start_val) / 3)
            draw.text((right - 100, gy - 25), f"{prefix}{grid_val:,.0f}", fill=(60, 75, 100), font=grid_font)

        # Curve data points (normalized 0 to 1)
        raw_curve = self.data.get("curve_points", [0.05, 0.15, 0.10, 0.35, 0.30, 0.65, 0.55, 0.85, 0.78, 1.0])
        num_points = len(raw_curve)

        # Compute point coordinates
        points = []
        for idx, val in enumerate(raw_curve):
            px = left + (idx / (num_points - 1)) * chart_w
            py = bottom - (val * chart_h)
            points.append((px, py))

        # Animated progress curve
        visible_limit = max(2, int(len(points) * t_norm) + 1)
        active_points = points[:visible_limit]

        if len(active_points) >= 2:
            # Interpolate exact tip position
            tip_x = left + (t_norm * chart_w)
            # Find interpolated tip_y
            segment_idx = min(int(t_norm * (num_points - 1)), num_points - 2)
            seg_p = (t_norm * (num_points - 1)) - segment_idx
            p1 = points[segment_idx]
            p2 = points[segment_idx + 1]
            tip_y = p1[1] + (p2[1] - p1[1]) * seg_p

            render_pts = [p for p in active_points if p[0] < tip_x] + [(tip_x, tip_y)]

            # 1. Gradient Fill Under Line
            fill_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            fill_draw = ImageDraw.Draw(fill_overlay)
            poly = [(render_pts[0][0], bottom)] + render_pts + [(render_pts[-1][0], bottom)]
            fill_color = theme_color + (40,)
            fill_draw.polygon(poly, fill=fill_color)
            img = Image.alpha_composite(img, fill_overlay)

            # 2. Glowing Line (Layered translucent strokes)
            glow_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_overlay)
            for width, alpha in [(14, 25), (8, 60), (4, 150), (2, 255)]:
                c = theme_color + (alpha,)
                glow_draw.line(render_pts, fill=c, width=width, joint="curve")
            img = Image.alpha_composite(img, glow_overlay)

            # 3. Glowing Head Dot
            dot_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            dot_draw = ImageDraw.Draw(dot_overlay)
            for rad, alpha in [(24, 30), (14, 90), (6, 255)]:
                dot_c = (255, 255, 255) + (alpha,) if rad == 6 else theme_color + (alpha,)
                dot_draw.ellipse([(tip_x - rad, tip_y - rad), (tip_x + rad, tip_y + rad)], fill=dot_c)
            img = Image.alpha_composite(img, dot_overlay)

        return img.convert("RGB")


class StatCalloutScene(BaseScene):
    """
    Big kinetic metric with pill badge and smooth camera zoom-in:
    e.g. +10.2%, -$1,000, 30 YEARS
    """
    def render(self, t_norm: float) -> Image.Image:
        img = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
        draw = ImageDraw.Draw(img)

        title = self.data.get("title", "").upper()
        stat_text = self.data.get("stat", "+0.0%")
        subtitle = self.data.get("subtitle", "")
        badge = self.data.get("badge", "VERIFIED DATA")
        color_name = self.data.get("color", "green")
        theme_color = COLOR_MAP.get(color_name.lower(), GREEN)

        # Subtle camera push-in scale
        zoom = 1.0 + 0.04 * ease_out_cubic(t_norm)
        
        # Pill Badge at top
        badge_font = get_font(bold=True, size=24)
        bx, by = 160, 260
        bw, bh = 240, 48
        radius = max(1, int(10 * zoom))
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=radius, fill=(20, 30, 48))
        draw.text((bx + 20, by + 12), badge.upper(), fill=theme_color, font=badge_font)

        # Title
        if title:
            t_font = get_font(bold=True, size=max(1, int(38 * zoom)))
            draw.text((160, 340), title, fill=MUTED, font=t_font)

        # Massive Stat Callout with Glow
        stat_size = max(1, int(130 * zoom))
        s_font = get_font(bold=True, size=stat_size)

        # Glow layer
        glow_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_overlay)
        glow_draw.text((160, 410), stat_text, fill=theme_color + (40,), font=s_font)
        img = Image.alpha_composite(img, glow_overlay)
        draw = ImageDraw.Draw(img)

        # Sharp top text
        draw.text((160, 410), stat_text, fill=theme_color, font=s_font)

        # Subtitle explanation
        if subtitle:
            sub_font = get_font(bold=False, size=max(1, int(34 * zoom)))
            draw.text((160, 590), subtitle, fill=TEXT, font=sub_font)

        return img.convert("RGB")


class CardGridScene(BaseScene):
    """
    2 to 3 Comparison cards popping in sequentially with ease-out cubic.
    """
    def render(self, t_norm: float) -> Image.Image:
        img = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
        draw = ImageDraw.Draw(img)

        title = self.data.get("title", "KEY TAKEAWAYS").upper()
        cards: List[Dict[str, Any]] = self.data.get("cards", [])

        # Header
        draw.text((120, 100), title, fill=TEXT, font=get_font(bold=True, size=46))

        num_cards = min(3, len(cards))
        if num_cards == 0:
            return img.convert("RGB")

        spacing = 40
        total_w = WIDTH - 240
        card_w = (total_w - (num_cards - 1) * spacing) / num_cards
        card_h = 580
        top_y = 230

        for i, card in enumerate(cards[:num_cards]):
            # Staggered pop-in timing
            stagger_start = i * 0.18
            raw_p = max(0.0, min(1.0, (t_norm - stagger_start) / 0.55))
            e = ease_out_cubic(raw_p)

            if e <= 0:
                continue

            cx = 120 + i * (card_w + spacing)
            cy = top_y + (1.0 - e) * 40  # Pop up from bottom
            
            c_color = COLOR_MAP.get(card.get("color", "cyan").lower(), CYAN)

            # Defensive clamped radius per README gotcha
            radius = max(1, int(16 * e))
            
            # Card background
            draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=radius, fill=(14, 21, 37))
            # Border
            draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=radius, outline=(30, 42, 68), width=2)

            # Top Accent Pill
            tag = card.get("tag", f"STEP {i+1}").upper()
            tag_font = get_font(bold=True, size=max(1, int(22 * e)))
            draw.rounded_rectangle([cx + 30, cy + 30, cx + 160, cy + 68], radius=max(1, int(8 * e)), fill=(20, 32, 54))
            draw.text((cx + 45, cy + 38), tag, fill=c_color, font=tag_font)

            # Card Title
            c_title = card.get("title", "")
            title_font = get_font(bold=True, size=max(1, int(32 * e)))
            draw.text((cx + 30, cy + 90), c_title, fill=WHITE, font=title_font)

            # Card Body Text
            desc = card.get("desc", "")
            body_font = get_font(bold=False, size=max(1, int(24 * e)))
            
            # Basic word wrap for body
            words = desc.split()
            lines, current_line = [], []
            for w in words:
                current_line.append(w)
                if len(" ".join(current_line)) > 26:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [w]
            if current_line:
                lines.append(" ".join(current_line))

            for l_idx, line in enumerate(lines[:8]):
                draw.text((cx + 30, cy + 160 + l_idx * 34), line, fill=MUTED, font=body_font)

        return img.convert("RGB")


class TextKineticScene(BaseScene):
    """
    High-impact statement with tracking zoom-in.
    """
    def render(self, t_norm: float) -> Image.Image:
        img = Image.new("RGBA", (WIDTH, HEIGHT), BG + (255,))
        draw = ImageDraw.Draw(img)

        tag = self.data.get("tag", "CORE PRINCIPLE").upper()
        headline = self.data.get("headline", "")
        subtext = self.data.get("subtext", "")
        color_name = self.data.get("color", "cyan")
        theme_color = COLOR_MAP.get(color_name.lower(), CYAN)

        zoom = 1.0 + 0.05 * ease_out_cubic(t_norm)

        # Tag
        draw.text((160, 280), tag, fill=theme_color, font=get_font(bold=True, size=max(1, int(26 * zoom))))

        # Headline
        h_font = get_font(bold=True, size=max(1, int(64 * zoom)))
        draw.text((160, 340), headline, fill=WHITE, font=h_font)

        # Accent Line
        line_w = int(120 * zoom)
        draw.line([(160, 440), (160 + line_w, 440)], fill=theme_color, width=4)

        # Subtext
        if subtext:
            s_font = get_font(bold=False, size=max(1, int(34 * zoom)))
            draw.text((160, 480), subtext, fill=MUTED, font=s_font)

        return img.convert("RGB")


def create_scene(scene_type: str, data: Dict[str, Any]) -> BaseScene:
    """Factory mapping scene type string to Scene instance."""
    st = scene_type.lower()
    if "chart" in st:
        return AreaChartScene(data)
    elif "stat" in st or "number" in st:
        return StatCalloutScene(data)
    elif "card" in st or "grid" in st or "list" in st:
        return CardGridScene(data)
    else:
        return TextKineticScene(data)
