import re
import os
import shutil
import socket
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

import whisper
from gradio_client import Client, handle_file

from pipeline.config import AUDIO_DIR, TEMP_DIR, SILENCE_GAP_SEC, TEXT, BG


def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def find_gradio_port(default_port: int = 7860) -> Optional[int]:
    """Checks ports 7860 to 7865 for active F5-TTS WebUI."""
    for p in range(default_port, default_port + 6):
        if is_port_open("127.0.0.1", p):
            return p
    return None


class AudioAligner:
    def __init__(self, gradio_url: str = "http://127.0.0.1:7860", whisper_model: str = "base"):
        self.gradio_url = gradio_url
        self.whisper_model_name = whisper_model
        self.ref_audio_path = AUDIO_DIR / "ref_voice.wav"
        self.ref_text_path = AUDIO_DIR / "ref_text.txt"
        self.silence_wav = AUDIO_DIR / "silence025.wav"

    def parse_script_segments(self, script_text: str) -> List[str]:
        # Split on [SEG n]
        raw_segs = re.split(r'\[SEG\s*\d+\]', script_text, flags=re.IGNORECASE)
        cleaned = []
        for s in raw_segs:
            text = s.strip()
            # Remove isolated punctuation and empty strings
            text = re.sub(r'^[^\w]+|[^\w]+$', '', text)
            if len(text) > 3:
                cleaned.append(text)
        if not cleaned:
            cleaned = [p.strip() for p in script_text.split("\n\n") if len(p.strip()) > 3]
        return cleaned

    def synthesize_windows_native_tts(self, text: str, output_path: Path):
        """Uses Windows 11 built-in offline Speech Engine (100% offline, zero network)."""
        clean_text = re.sub(r'\[pause\]', '', text, flags=re.IGNORECASE).strip()
        # Clean text for safe speech
        clean_text = clean_text.replace('"', ' ').replace("'", " ")

        temp_text_file = TEMP_DIR / "tts_input.txt"
        temp_text_file.write_text(clean_text, encoding="utf-8")

        ps_script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Rate = 0
$synth.SetOutputToWaveFile('{output_path.resolve().as_posix()}')
$text = Get-Content -Path '{temp_text_file.resolve().as_posix()}' -Raw -Encoding UTF8
$synth.Speak($text)
$synth.Dispose()
"""
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def synthesize_segment_f5(self, text: str, output_path: Path, active_port: int) -> Path:
        url = f"http://127.0.0.1:{active_port}"
        ref_text = self.ref_text_path.read_text(encoding="utf-8").strip() if self.ref_text_path.exists() else ""

        print(f"Connecting to F5-TTS WebUI at {url}...")
        client = Client(url)
        result = client.predict(
            ref_audio=handle_file(str(self.ref_audio_path)),
            ref_text=ref_text,
            gen_text=text,
            remove_silence=False,
            api_name="/predict"
        )
        generated_file = result[0] if isinstance(result, (tuple, list)) else result
        shutil.copy(generated_file, str(output_path))
        return output_path

    def stitch_segments_with_silence(self, seg_paths: List[Path], output_wav: Path) -> Path:
        concat_txt = TEMP_DIR / "concat_audio.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for i, p in enumerate(seg_paths):
                f.write(f"file '{p.resolve().as_posix()}'\n")
                if i < len(seg_paths) - 1:
                    f.write(f"file '{self.silence_wav.resolve().as_posix()}'\n")

        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "pcm_s16le", str(output_wav)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output_wav

    def extract_sentence_timestamps(self, audio_wav: Path) -> List[Dict[str, Any]]:
        print(f"Loading Whisper model '{self.whisper_model_name}' for speech alignment...")
        model = whisper.load_model(self.whisper_model_name)
        result = model.transcribe(str(audio_wav), word_timestamps=True, language="en")
        
        sentences = []
        sentence_id = 0
        for seg in result.get("segments", []):
            text = seg.get("text", "").strip()
            if not text:
                continue
            sentences.append({
                "id": sentence_id,
                "text": text,
                "start": round(seg["start"], 3),
                "end": round(seg["end"], 3),
                "duration": round(seg["end"] - seg["start"], 3)
            })
            sentence_id += 1
        return sentences

    def generate_ass_subtitles(self, sentences: List[Dict[str, Any]], output_ass: Path):
        def sec_to_ass_time(seconds: float) -> str:
            hrs = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            secs = seconds % 60
            centis = int(round((secs - int(secs)) * 100))
            return f"{hrs:01d}:{mins:02d}:{int(secs):02d}.{centis:02d}"

        ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: JasonCaptions,DejaVu Sans,48,&H00F0E8E2,&H000000FF,&H00160C08,&H80000000,-1,0,0,0,100,100,0,0,1,3,0,2,80,80,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        for s in sentences:
            start_str = sec_to_ass_time(s["start"])
            end_str = sec_to_ass_time(s["end"])
            clean_text = re.sub(r'\[pause\]', '', s["text"], flags=re.IGNORECASE).strip()
            ass_content += f"Dialogue: 0,{start_str},{end_str},JasonCaptions,,0,0,0,,{clean_text}\n"

        output_ass.write_text(ass_content, encoding="utf-8")
        print(f"Generated ASS subtitles: {output_ass}")

    def process(self, script_text: str, pre_existing_audio: Optional[Path] = None) -> Dict[str, Any]:
        final_audio_wav = TEMP_DIR / "final_voiceover.wav"
        
        if pre_existing_audio and Path(pre_existing_audio).exists():
            print(f"Using provided audio file: {pre_existing_audio}")
            cmd = ["ffmpeg", "-y", "-i", str(pre_existing_audio), "-c:a", "pcm_s16le", str(final_audio_wav)]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            segments = self.parse_script_segments(script_text)
            print(f"Found {len(segments)} segments in script.")
            
            active_port = find_gradio_port()
            if active_port:
                print(f"[+] Found active F5-TTS WebUI on port {active_port}")
            else:
                print("[!] F5-TTS WebUI not detected on 7860-7865.")
                print("[!] Using Windows 11 Native Offline TTS so pipeline runs without internet.")

            seg_files = []
            for idx, seg in enumerate(segments):
                seg_path = TEMP_DIR / f"segment_{idx:02d}.wav"
                if active_port:
                    print(f"Synthesizing Segment {idx+1}/{len(segments)} via F5-TTS...")
                    self.synthesize_segment_f5(seg, seg_path, active_port)
                else:
                    print(f"Synthesizing Segment {idx+1}/{len(segments)} via Windows Native TTS...")
                    self.synthesize_windows_native_tts(seg, seg_path)
                seg_files.append(seg_path)

            print("Stitching segments with 0.25s silence beats...")
            self.stitch_segments_with_silence(seg_files, final_audio_wav)

        print("Aligning speech with Whisper to generate sentence timestamps...")
        sentences = self.extract_sentence_timestamps(final_audio_wav)
        
        ass_path = TEMP_DIR / "captions.ass"
        self.generate_ass_subtitles(sentences, ass_path)

        return {
            "audio_wav": final_audio_wav,
            "sentences": sentences,
            "ass_path": ass_path
        }
