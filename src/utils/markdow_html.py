import re


def markdown_to_blocks(md_text):
    """Split markdown text into blocks separated by one or more blank lines.

    Returns a list of non-empty, stripped block strings. Empty/whitespace
    input returns an empty list.
    """
    if not md_text or not md_text.strip():
        return []

    # split on one or more blank lines (handles spaces/tabs on blank lines)
    parts = re.split(r"\n\s*\n", md_text.strip())
    blocks = [part.strip() for part in parts if part.strip()]
    return blocks