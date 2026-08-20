"""Helpers for serializing CRLF-delimited text formats."""

from __future__ import annotations

from collections.abc import Iterable


def fold_content_line(line: str, max_octets: int = 75) -> str:
    """Fold one UTF-8 content line without splitting a multi-byte character."""
    if max_octets < 2:
        raise ValueError("max_octets must be at least 2")

    chunks: list[str] = []
    current = ""
    for character in line:
        candidate = current + character
        if current and len(candidate.encode("utf-8")) > max_octets:
            chunks.append(current)
            current = " " + character
        else:
            current = candidate
    chunks.append(current)
    return "\r\n".join(chunks)


def serialize_content_lines(lines: Iterable[str]) -> str:
    """Fold and serialize content lines with RFC-style CRLF terminators."""
    serialized = []
    for line in lines:
        serialized.append(fold_content_line(line.rstrip("\r\n")))
        serialized.append("\r\n")
    return "".join(serialized)
