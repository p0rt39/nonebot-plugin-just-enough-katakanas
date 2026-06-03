import re
from itertools import product
from pathlib import Path

import nltk
from e2k import P2K
from g2p_en import G2p

from .dictionary import database

NLTK_DATA_DIR = Path(__file__).parent / "assets" / "nltk_data"
if NLTK_DATA_DIR.exists():
    nltk.data.path.insert(0, str(NLTK_DATA_DIR))

WORD_RE = re.compile(r"[A-Za-z']+")
VALID_WORD_RE = re.compile(r"^[A-Za-z']+$")
TOKEN_RE = re.compile(r"[A-Za-z']+|[^A-Za-z']+")


class English2KatakanaEngine:
    def __init__(self) -> None:
        self.g2p = G2p()
        self.p2k = P2K()

    def extract_words(self, text: str) -> list[str]:
        return WORD_RE.findall(text)

    def lookup_in_dict(self, word: str) -> list[str]:
        normalized_word = word.strip()

        if not normalized_word:
            return [] # Never reached, reserved for built-in debug (WIP)

        conn = database.get_connection()

        if conn is None:
            return []   # No database connection, empty result for fallback
                        # Maybe a FIXME for better fallback mechanism

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT katakana
            FROM loanwords
            WHERE english = ?
            ORDER BY common DESC, id ASC
            """,
            (normalized_word,),
        )

        return [row[0] for row in cursor.fetchall()]

    def convert_word(self, word: str) -> tuple[str, list[str]]:
        normalized_word = word.strip()

        if not normalized_word:
            return "empty", []  # Never reached, reserved for built-in debug (WIP)

        if not VALID_WORD_RE.fullmatch(normalized_word):
            return "passthrough", [normalized_word]  # Illegal input, return as-is

        if results := self.lookup_in_dict(normalized_word):
            return "dictionary", results

        return "phonetic", [self.phonetic_convert(normalized_word)]

    # Universal phonetic convert engine
    def phonetic_convert(self, word: str) -> str:
        try:
            return self.p2k(self.g2p(word))
        except LookupError:
            return self._phonetic_convert_without_tagger(word)
            # Fallback if NLTK data missing, never reached

    # Fallback if NLTK data missing, never reached
    def _phonetic_convert_without_tagger(self, text: str) -> str:
        parts: list[str] = []

        for token in re.findall(r"[A-Za-z']+|[^A-Za-z']+", text):
            if re.search(r"[A-Za-z]", token):
                parts.append(self.p2k(self.g2p.predict(token.lower())))
            else:
                parts.append(token)

        return "".join(parts)

    def english_to_katakana(self, text: str) -> tuple[str, list[str]]:

        normalized_text = text.strip()
        words = self.extract_words(normalized_text)

        if len(words) <= 1:
            if not VALID_WORD_RE.fullmatch(normalized_text):
                return "passthrough", [normalized_text]

            return self.convert_word(words[0] if words else normalized_text)

        token_groups: list[list[str]] = []
        source = "phonetic"

        for token in TOKEN_RE.findall(text):
            if WORD_RE.fullmatch(token):
                token_source, token_results = self.convert_word(token)
                if token_source == "dictionary":
                    source = "dictionary"
                # Unused since source is ignored in sentence conversion now
                # Maybe a FIXME in future for detailed logger/debug info

                token_groups.append(token_results[0:1])
            else:
                token_groups.append([token])

        return source, ["".join(parts) for parts in product(*token_groups)]


engine = English2KatakanaEngine()
