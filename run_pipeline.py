import sys
import argparse
from pathlib import Path

from pipeline.config import TEMP_DIR, OUTPUT_DIR
from pipeline.audio_aligner import AudioAligner
from pipeline.director import StoryboardDirector
from pipeline.renderer import MultiCoreRenderer
from pipeline.assembler import VideoAssembler


def main():
    parser = argparse.ArgumentParser(description="Jason Explains: Automated Narration-to-Video Pipeline (Windows 11)")
    parser.add_argument("--script", type=str, required=True, help="Path to narration script (.txt)")
    parser.add_argument("--audio", type=str, default=None, help="Optional: Path to pre-generated voice audio (.wav/.mp3)")
    parser.add_argument("--model", type=str, default="gemma4:e4b", help="Ollama model name (default: gemma4:e4b)")
    parser.add_argument("--whisper", type=str, default="base", help="Whisper model size: tiny, base, small, medium (default: base)")
    parser.add_argument("--output", type=str, default=None, help="Optional: Custom final output video path")
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.exists():
        print(f"Error: Script file not found at {script_path}")
        sys.exit(1)

    script_text = script_path.read_text(encoding="utf-8").strip()
    video_title = script_path.stem
    final_output_path = Path(args.output) if args.output else OUTPUT_DIR / f"{video_title}.mp4"

    print("==================================================")
    print(f"Starting Pipeline for: {video_title}")
    print("==================================================")

    # 1. Audio Generation & Alignment
    aligner = AudioAligner(whisper_model=args.whisper)
    audio_data = aligner.process(script_text, pre_existing_audio=args.audio)
    
    # 2. LLM Storyboard Directing
    director = StoryboardDirector(model_name=args.model)
    storyboard = director.direct(audio_data["sentences"])

    total_duration = audio_data["sentences"][-1]["end"] + 0.5

    # 3. Parallel Frame Rendering (with burned-in captions)
    silent_video_path = TEMP_DIR / "silent_render.mp4"
    renderer = MultiCoreRenderer()
    renderer.render(storyboard, audio_data["sentences"], total_duration, str(silent_video_path))

    # 4. Final Assembly & Loudnorm
    assembler = VideoAssembler()
    assembler.assemble(
        silent_video=silent_video_path,
        audio_wav=audio_data["audio_wav"],
        final_output=final_output_path
    )

    # 5. Quality Verification Gate
    assembler.verify_quality(final_output_path)

    print("==================================================")
    print(f"Done! Final video ready: {final_output_path}")
    print("==================================================")


if __name__ == "__main__":
    main()
