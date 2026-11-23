import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from multiprocessing import Pool, cpu_count
from PIL import Image, ImageDraw

from pipeline.config import (
    WIDTH, HEIGHT, FPS, BG, TEXT, WHITE, TEMP_DIR,
    get_font, get_ffmpeg_video_encoder_flags
)
from pipeline.scene_templates import create_scene


def _draw_caption_overlay(base_img: Image.Image, caption: str) -> Image.Image:
    """Burns subtitles directly onto the frame with dark navy translucent backdrop."""
    if not caption.strip():
        return base_img

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = get_font(bold=True, size=42)

    # Word wrap
    words = caption.split()
    lines, current_line = [], []
    for w in words:
        current_line.append(w)
        bbox = draw.textbbox((0, 0), " ".join(current_line), font=font)
        if (bbox[2] - bbox[0]) > 1400:
            lines.append(" ".join(current_line[:-1]))
            current_line = [w]
    if current_line:
        lines.append(" ".join(current_line))

    # Calculate bounding box for the background pill
    line_height = 54
    total_text_h = len(lines) * line_height
    max_line_w = 0
    for l in lines:
        bb = draw.textbbox((0, 0), l, font=font)
        max_line_w = max(max_line_w, bb[2] - bb[0])

    padding_x = 36
    padding_y = 18
    pill_w = max_line_w + padding_x * 2
    pill_h = total_text_h + padding_y * 2
    pill_x = (WIDTH - pill_w) // 2
    pill_y = HEIGHT - 140 - pill_h

    # Rounded translucent pill
    draw.rounded_rectangle(
        [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
        radius=14,
        fill=(8, 12, 22, 210)
    )

    # Draw centered text lines
    for idx, line in enumerate(lines):
        bb = draw.textbbox((0, 0), line, font=font)
        lw = bb[2] - bb[0]
        tx = (WIDTH - lw) // 2
        ty = pill_y + padding_y + idx * line_height
        draw.text((tx, ty), line, fill=TEXT, font=font)

    return Image.alpha_composite(base_img.convert("RGBA"), overlay).convert("RGB")


def _render_single_frame(task: Tuple[int, float, Dict[str, Any], str]) -> bytes:
    frame_idx, t, scene_data, caption_text = task
    start = scene_data["start"]
    end = scene_data["end"]
    duration = max(0.001, end - start)
    
    t_norm = max(0.0, min(1.0, (t - start) / duration))
    scene = create_scene(scene_data["scene_type"], scene_data["params"])
    frame_img = scene.render(t_norm)

    # Burn subtitle directly
    if caption_text:
        frame_img = _draw_caption_overlay(frame_img, caption_text)

    return frame_img.tobytes()


class MultiCoreRenderer:
    def __init__(self, fps: int = FPS, width: int = WIDTH, height: int = HEIGHT):
        self.fps = fps
        self.width = width
        self.height = height

    def find_scene_for_time(self, t: float, storyboard: List[Dict[str, Any]]) -> Dict[str, Any]:
        for sc in storyboard:
            if sc["start"] <= t <= sc["end"]:
                return sc
        if t < storyboard[0]["start"]:
            return storyboard[0]
        return storyboard[-1]

    def find_caption_for_time(self, t: float, sentences: List[Dict[str, Any]]) -> str:
        for s in sentences:
            if s["start"] <= t <= s["end"]:
                return s["text"]
        return ""

    def render(self, storyboard: List[Dict[str, Any]], sentences: List[Dict[str, Any]], total_duration: float, output_mp4: str) -> str:
        total_frames = int(total_duration * self.fps)
        num_cores = max(1, cpu_count() - 1)
        
        enc_name, enc_flags = get_ffmpeg_video_encoder_flags(fast_preset=True)
        print(f"Detected FFmpeg video encoder: '{enc_name}'")
        print(f"Rendering {total_frames} frames ({total_duration:.2f}s) across {num_cores} CPU cores with burned captions...")

        tasks = []
        for f in range(total_frames):
            t = f / self.fps
            active_scene = self.find_scene_for_time(t, storyboard)
            active_caption = self.find_caption_for_time(t, sentences)
            tasks.append((f, t, active_scene, active_caption))

        log_file = TEMP_DIR / "ffmpeg_render.log"
        log_handle = open(log_file, "w", encoding="utf-8")

        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-pixel_format", "rgb24",
            "-video_size", f"{self.width}x{self.height}",
            "-framerate", str(self.fps),
            "-i", "pipe:0"
        ] + enc_flags + [str(output_mp4)]

        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=log_handle
        )

        chunk_size = 20
        completed = 0
        try:
            with Pool(processes=num_cores) as pool:
                for frame_bytes in pool.imap(_render_single_frame, tasks, chunksize=chunk_size):
                    if proc.poll() is not None:
                        raise BrokenPipeError(f"FFmpeg exited early with code {proc.poll()}")
                    proc.stdin.write(frame_bytes)
                    completed += 1
                    if completed % 90 == 0 or completed == total_frames:
                        pct = (completed / total_frames) * 100
                        print(f"Render progress: {completed}/{total_frames} frames ({pct:.1f}%)", end="\r", flush=True)

            proc.stdin.close()
            proc.wait()
            log_handle.close()
            print(f"\nVisual stream rendered successfully: {output_mp4}")
            return output_mp4

        except Exception as e:
            log_handle.close()
            error_details = log_file.read_text(encoding="utf-8", errors="ignore")
            print(f"\n[!] Render error: {e}")
            if error_details.strip():
                print("================ FFmpeg Diagnostic Output ================")
                print(error_details[-1500:])
                print("==========================================================")
            raise
