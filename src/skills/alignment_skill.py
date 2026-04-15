import os
from openai import OpenAI
from src.config.settings import settings
from src.core.logging import get_logger

logger = get_logger("skills.alignment")

class AlignmentSkill:
    """Uses Whisper-1 to get word-level timestamps for audio-text synchronization."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_word_timestamps(self, audio_path: str) -> list:
        """
        Transcribes audio and returns a list of dictionaries: 
        [{'word': 'Hello', 'start': 0.1, 'end': 0.5}, ...]
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found for alignment: {audio_path}")
            return []

        try:
            logger.info(f"[Alignment] Analyzing audio for timestamps: {audio_path}")
            with open(audio_path, "rb") as audio_file:
                # Use Whisper-1 with word-level granularity
                transcript = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["word"]
                )
            
            # Extract words from the verbose response
            words = []
            if hasattr(transcript, 'words'):
                for w in transcript.words:
                    words.append({
                        "word": w.word,
                        "start": w.start,
                        "end": w.end
                    })
            elif isinstance(transcript, dict) and "words" in transcript:
                 for w in transcript["words"]:
                    words.append({
                        "word": w["word"],
                        "start": w["start"],
                        "end": w["end"]
                    })
            
            logger.info(f"[Alignment] Extracted {len(words)} word timestamps.")
            return words

        except Exception as e:
            logger.error(f"Alignment failed: {e}")
            return []

    def generate_ass_subtitles(self, words: list, max_chars_per_line: int = 15) -> str:
        """Generates an Advanced Substation Alpha (.ass) string for perfect centering and styling."""
        if not words: return ""
        
        def format_time_ass(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = seconds % 60
            return f"{h:1d}:{m:02d}:{s:05.2f}"

        header = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            # Alignment 5 = Middle Center
            "Style: Default,Arial,68,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,0,2,5,30,30,30,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Text"
        ]

        events = []
        cumulative_list = []
        for i, word_data in enumerate(words):
            word = word_data["word"].strip()
            cumulative_list.append(word)
            
            start = format_time_ass(word_data["start"])
            end_sec = words[i+1]["start"] if i+1 < len(words) else word_data["start"] + 3.0
            end = format_time_ass(end_sec)
            
            # Word wrapping
            text = " ".join(cumulative_list)
            lines, current_line = [], []
            for w in text.split():
                if len(" ".join(current_line + [w])) <= max_chars_per_line:
                    current_line.append(w)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [w]
            if current_line: lines.append(" ".join(current_line))
            
            display_text = "\\N".join(lines[-2:]) # Max 2 lines
            events.append(f"Dialogue: 0,{start},{end},Default,{display_text}")
            
        return "\n".join(header + events)

# Static instance
alignment_service = AlignmentSkill()
