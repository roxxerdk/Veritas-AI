import re
import unicodedata

# Define regex patterns for cleaning
MULTIPLE_SPACES_RE = re.compile(r"[ \t]+")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
HYPHEN_NEWLINE_RE = re.compile(r"(\w+)-\n+(\w+)")

# Standard ligature mapping
LIGATURE_MAP = {
    "ﬀ": "ff",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "st",
    "ﬆ": "st"
}


class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        """Cleans and normalizes raw text extracted from documents for embeddings quality."""
        if not text:
            return ""

        # 1. Unicode Normalization (compatibility decomposition NFKC)
        cleaned = unicodedata.normalize("NFKC", text)

        # 2. Translate ligatures
        for ligature, replacement in LIGATURE_MAP.items():
            cleaned = cleaned.replace(ligature, replacement)

        # 3. Join hyphenated words split by line endings (e.g. multi-\nagent -> multi-agent)
        cleaned = HYPHEN_NEWLINE_RE.sub(r"\1\2", cleaned)

        # 4. Remove control characters
        cleaned = CONTROL_CHARS_RE.sub("", cleaned)

        # 5. Collapse duplicate whitespaces while preserving double newlines (paragraphs)
        lines = cleaned.splitlines()
        normalized_lines = []
        for line in lines:
            # Strip trailing/leading spaces, collapse duplicate inner spaces
            stripped = line.strip()
            collapsed = MULTIPLE_SPACES_RE.sub(" ", stripped)
            normalized_lines.append(collapsed)

        # Re-join lines and collapse consecutive empty paragraphs
        joined = "\n".join(normalized_lines)
        # Replaces 3 or more consecutive newlines with exactly 2 newlines (double newlines)
        cleaned_paragraphs = re.sub(r"\n{3,}", "\n\n", joined)

        return cleaned_paragraphs.strip()
