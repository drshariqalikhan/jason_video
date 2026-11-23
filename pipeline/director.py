import json
import re
from typing import List, Dict, Any, Optional
import requests

from pipeline.config import TEMP_DIR


DIRECTOR_SYSTEM_PROMPT = """
You are the Animation Director for the "Jason Explains" YouTube finance channel.
Your role: Convert a timed transcript into a synchronized sequence of visual animation beats.

STYLE RULES:
1. STRICT RULE: ABSOLUTELY NO CHARACTERS, NO STICK FIGURES, NO HUMANOID SHAPES.
2. Visuals must be dark navy, sleek, data-driven, and kinetic (like WhySector / Money Modeled).
3. 4 Scene Types available:
   - "area_chart": Use when discussing market growth, drops, stock trends, history, or dollar amounts over time.
     Parameters: {"title": str, "start_val": float, "end_val": float, "prefix": "$", "suffix": "", "color": "cyan"|"green"|"red"}
   - "stat_callout": Use when highlighting a single crucial stat, percentage, shock number, or rule.
     Parameters: {"title": str, "stat": str (e.g. "+10.4%", "-34%", "30 YEARS"), "subtitle": str, "badge": str, "color": "green"|"red"|"amber"|"cyan"}
   - "card_grid": Use when listing 2 or 3 rules, steps, pitfalls, or comparisons.
     Parameters: {"title": str, "cards": [{"title": str, "desc": str, "tag": str, "color": str}]}
   - "text_kinetic": Use for impactful statements, hooks, disclaimers, or narrative transitions.
     Parameters: {"tag": str, "headline": str, "subtext": str, "color": "cyan"|"gold"|"amber"}

Output MUST be a valid JSON array of scenes matching the sentence IDs.
Example Output Format:
[
  {
    "sentence_id": 0,
    "scene_type": "text_kinetic",
    "params": {
      "tag": "THE BIG QUESTION",
      "headline": "Is Investing Too Risky?",
      "subtext": "What beginners actually need to know.",
      "color": "cyan"
    }
  }
]
"""

class StoryboardDirector:
    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "gemma2:9b"):
        self.ollama_url = ollama_url.rstrip("/")
        self.model_name = model_name

    def call_ollama(self, prompt: str) -> str:
        """Sends request to local Ollama API in JSON mode."""
        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": DIRECTOR_SYSTEM_PROMPT,
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "[]")
        except Exception as e:
            print(f"Warning: Failed to communicate with Ollama ({e}). Triggering fallback director.")
            return "[]"

    def create_fallback_scene(self, sentence: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a safe, attractive text_kinetic scene if the LLM output is missing."""
        text = sentence.get("text", "")
        # Extract first 4-5 words as headline
        words = text.split()
        headline = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
        subtext = " ".join(words[5:]) if len(words) > 5 else ""

        # Auto-detect numbers for quick stat detection
        has_num = re.search(r'(\d+[\d,\.]*%?|\$\d+)', text)
        if has_num:
            stat_val = has_num.group(1)
            return {
                "sentence_id": sentence["id"],
                "scene_type": "stat_callout",
                "params": {
                    "title": "KEY DATA POINT",
                    "stat": stat_val,
                    "subtitle": text,
                    "badge": "VERIFIED DATA",
                    "color": "cyan"
                }
            }

        return {
            "sentence_id": sentence["id"],
            "scene_type": "text_kinetic",
            "params": {
                "tag": "MARKET INSIGHT",
                "headline": headline,
                "subtext": subtext,
                "color": "cyan"
            }
        }

    def direct(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Converts Whisper-timed sentences into a complete, executable storyboard."""
        print(f"Directing {len(sentences)} scenes using Ollama model '{self.model_name}'...")
        
        transcript_prompt = "Generate a scene for each of the following sentences by sentence_id:\n\n"
        for s in sentences:
            transcript_prompt += f"ID {s['id']}: \"{s['text']}\"\n"

        response_raw = self.call_ollama(transcript_prompt)
        
        # Parse JSON
        parsed_scenes = []
        try:
            parsed = json.loads(response_raw)
            if isinstance(parsed, list):
                parsed_scenes = parsed
            elif isinstance(parsed, dict) and "scenes" in parsed:
                parsed_scenes = parsed["scenes"]
        except Exception:
            print("Notice: Parsing LLM response failed, using smart fallback generator.")

        # Map by sentence_id
        scene_by_id = {}
        for sc in parsed_scenes:
            if isinstance(sc, dict) and "sentence_id" in sc:
                scene_by_id[sc["sentence_id"]] = sc

        # Build final validated timeline
        final_storyboard = []
        for s in sentences:
            sid = s["id"]
            if sid in scene_by_id:
                candidate = scene_by_id[sid]
                # Inject timing bounds from Whisper
                candidate["start"] = s["start"]
                candidate["end"] = s["end"]
                candidate["duration"] = s["duration"]
                final_storyboard.append(candidate)
            else:
                fallback = self.create_fallback_scene(s)
                fallback["start"] = s["start"]
                fallback["end"] = s["end"]
                fallback["duration"] = s["duration"]
                final_storyboard.append(fallback)

        storyboard_path = TEMP_DIR / "storyboard.json"
        with open(storyboard_path, "w", encoding="utf-8") as f:
            json.dump(final_storyboard, f, indent=2)

        print(f"Storyboard compiled successfully: {storyboard_path}")
        return final_storyboard
