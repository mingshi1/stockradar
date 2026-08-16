from __future__ import annotations

import hashlib
from dataclasses import dataclass


# Characters that commonly sneak into copied secrets on mobile.
# Removing these is safe for normal API keys and avoids silently
# authenticating with a visually identical but byte-different value.
_INVISIBLE_CHARS = (
    "\ufeff",  # BOM / zero-width no-break space
    "\u200b",  # zero-width space
    "\u200c",  # zero-width non-joiner
    "\u200d",  # zero-width joiner
    "\u2060",  # word joiner
    "\u00ad",  # soft hyphen
)


@dataclass(frozen=True, slots=True)
class KeyDiagnostic:
    length: int
    fingerprint: str
    last4: str
    ascii_only: bool

    def compact(self) -> str:
        if self.length == 0:
            return "Key为空"

        ascii_text = (
            "ASCII"
            if self.ascii_only
            else "含非ASCII字符"
        )

        return (
            f"{self.length}字符 · "
            f"指纹 {self.fingerprint} · "
            f"末尾 {self.last4} · "
            f"{ascii_text}"
        )


def normalize_api_key(
    value: str | None,
) -> str:
    """
    Normalize a copied API key without changing normal visible ASCII.

    - removes leading/trailing whitespace
    - removes common invisible Unicode characters anywhere
    - removes CR/LF/TAB that can be introduced by clipboard copy
    """
    if not value:
        return ""

    normalized = str(value)

    for char in _INVISIBLE_CHARS:
        normalized = normalized.replace(
            char,
            "",
        )

    normalized = (
        normalized
        .replace("\r", "")
        .replace("\n", "")
        .replace("\t", "")
        .strip()
    )

    return normalized


def key_diagnostic(
    value: str | None,
) -> KeyDiagnostic:
    normalized = normalize_api_key(
        value
    )

    fingerprint = (
        hashlib.sha256(
            normalized.encode("utf-8")
        )
        .hexdigest()[:12]
        if normalized
        else "EMPTY"
    )

    return KeyDiagnostic(
        length=len(normalized),
        fingerprint=fingerprint,
        last4=(
            normalized[-4:]
            if normalized
            else "EMPTY"
        ),
        ascii_only=(
            normalized.isascii()
            if normalized
            else True
        ),
    )
