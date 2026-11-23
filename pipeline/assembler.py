import re
import subprocess
from pathlib import Path
from typing import Dict, Any

from pipeline.config import LOUDNORM_TARGET, OUTPUT_DIR, get_ffmpeg_video_encoder_flags


class VideoAssembler:
    def __init__(self, loudnorm: str = LOUDNORM_TARGET):
        self.loudnorm = loudnorm

    def assemble(self, silent_video: Path, audio_wav: Path, final_output: Path) -> Path:
        print("Assembling final video with audio normalization...")

        # Mux video with audio and apply loudnorm
        cmd = [
            "ffmpeg", "-y",
            "-i", str(silent_video.resolve()),
            "-i", str(audio_wav.resolve()),
            "-c:v", "copy",
            "-af", self.loudnorm,
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(final_output.resolve())
        ]

        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
        if result.returncode != 0:
            # If stream copy fails for any container reason, transcode audio and video
            enc_name, enc_flags = get_ffmpeg_video_encoder_flags(fast_preset=False)
            cmd = [
                "ffmpeg", "-y",
                "-i", str(silent_video.resolve()),
                "-i", str(audio_wav.resolve()),
                "-af", self.loudnorm
            ] + enc_flags + [
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                str(final_output.resolve())
            ]
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
            if result.returncode != 0:
                print(f"Assembler warning/error:\n{result.stderr}")
                raise RuntimeError("FFmpeg assembly failed.")

        print(f"Assembly complete: {final_output}")
        return final_output

    def verify_quality(self, final_video: Path) -> Dict[str, Any]:
        print("Running quality verification gate...")
        
        audit_cmd = [
            "ffmpeg", "-i", str(final_video.resolve()),
            "-af", "volumedetect",
            "-f", "null", "-"
        ]
        audit_res = subprocess.run(audit_cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, encoding="utf-8", errors="ignore")
        
        mean_vol = re.search(r'mean_volume:\s*([-\d\.]+\s*dB)', audit_res.stderr)
        max_vol = re.search(r'max_volume:\s*([-\d\.]+\s*dB)', audit_res.stderr)

        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate,duration",
            "-of", "default=noprint_wrappers=1",
            str(final_video.resolve())
        ]
        probe_res = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="ignore")

        report = {
            "mean_volume": mean_vol.group(1) if mean_vol else "N/A",
            "max_volume": max_vol.group(1) if max_vol else "N/A",
            "probe_info": probe_res.stdout.strip().replace("\n", ", ")
        }

        print("Verification Report:")
        print(f"  * Loudness: Mean = {report['mean_volume']}, Peak = {report['max_volume']}")
        print(f"  * Video Stream: {report['probe_info']}")
        return report
