from src.nodes.htmlnode import HtmlNode, LeafNode, ParentNode

def markdown_to_blocks(md_text: Optional[str]) -> List[str]:
    """Split markdown text into blocks separated by one or more blank lines.

    Args:
        md_text: Raw markdown text or ``None``.

    Returns:
        A list of non-empty, stripped block strings. Empty/whitespace
        input returns an empty list.
    """
    if not md_text or not md_text.strip():
        return []

    parts = _SPLIT_RE.split(md_text.strip())
    blocks = [part.strip() for part in parts if part.strip()]
    return blocks


# Mapping from `BlockType` to a representative Markdown marker.
# Keep this mapping handy for parsing/serialization.
MARKDOWN_BLOCK_MARKERS: Dict[BlockType, str] = {
    BlockType.HEADING: "#",
    BlockType.UNORDERED_LIST: "-",
    BlockType.ORDERED_LIST: "1.",
    BlockType.CODE: "```",
    BlockType.QUOTE: ">",
    BlockType.PARAGRAPH: "",
}


def block_to_block_type(md_block: Optional[str]) -> BlockType:
    """Return a ``BlockType`` for a single markdown block string.

    Heuristic rules (simple, explicit) are used to identify the block
    type. This function is intentionally conservative to avoid false
    positives.

    Args:
        md_block: A single markdown block string.

    Returns:
        A ``BlockType`` value.
    """
    if not md_block or not md_block.strip():
        return BlockType.PARAGRAPH

    s = md_block.lstrip()
    if s.startswith("#"):
        return BlockType.HEADING
    if s.startswith("```"):
        return BlockType.CODE
    if s.startswith(">"):
        return BlockType.QUOTE
    if _ORDERED_LIST_RE.match(s):
        return BlockType.ORDERED_LIST
    if _UNORDERED_LIST_RE.match(s):
        return BlockType.UNORDERED_LIST
    return BlockType.PARAGRAPH


def makdown_to_html_node():
    return 1