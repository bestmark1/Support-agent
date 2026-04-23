from __future__ import annotations

import re


SUPPORTED_LANGUAGES = {"ru", "en"}
_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def normalize_language(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    return None


def detect_language(text: str) -> str:
    cyrillic_count = len(_CYRILLIC_RE.findall(text))
    latin_count = len(_LATIN_RE.findall(text))
    if cyrillic_count > latin_count:
        return "ru"
    return "en"
