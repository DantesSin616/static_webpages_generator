from typing import Optional, List, Dict
import re

from src.nodes.htmlnode import HtmlNode, LeafNode, ParentNode, text_node_to_html_node
from src.nodes.textnode import BlockType, TextNode, TextType


_SPLIT_RE = re.compile(r"\n\s*\n+")
_ORDERED_LIST_RE = re.compile(r"^\d+\.\s+")
_UNORDERED_LIST_RE = re.compile(r"^[-+*]\s+")


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


def markdown_to_html_node(markdown):
    """Convert markdown text into a single ParentNode('div', [...]).

    This function converts the given markdown string into a tree of
    `HtmlNode` objects. It returns a single `ParentNode` with tag
    `div` whose children are the top-level block nodes.
    """

    def text_to_children(text: str):
        # Convert a plain text string into a list of HtmlNode children.

        # Inline parsing for **bold**, _italic_, and `code` spans.
        # This is a simple left-to-right non-recursive parser.
        nodes = []
        if not text:
            return nodes

        # Collapse newlines into spaces for inline content
        text = text.replace("\n", " ")
        while "  " in text:
            text = text.replace("  ", " ")

        # Patterns for inline elements
        bold_re = re.compile(r"\*\*(.+?)\*\*")
        italic_re = re.compile(r"(\*|_)(.+?)\1")
        code_re = re.compile(r"`([^`]+?)`")

        s = text
        while s:
            # Find next match among patterns
            next_match = None
            next_kind = None
            for kind, pattern in (("bold", bold_re), ("italic", italic_re), ("code", code_re)):
                m = pattern.search(s)
                if m:
                    if next_match is None or m.start() < next_match.start():
                        next_match = m
                        next_kind = kind

            if not next_match:
                # remainder is plain text
                tn = TextNode(s, TextType.TEXT)
                nodes.append(text_node_to_html_node(tn))
                break

            # text before match
            if next_match.start() > 0:
                pre = s[: next_match.start()]
                tn = TextNode(pre, TextType.TEXT)
                nodes.append(text_node_to_html_node(tn))

            if next_kind == "italic":
                inner = next_match.group(2)
            else:
                inner = next_match.group(1)

            if next_kind == "bold":
                tn = TextNode(inner, TextType.BOLD)
                nodes.append(text_node_to_html_node(tn))
            elif next_kind == "italic":
                tn = TextNode(inner, TextType.ITALIC)
                nodes.append(text_node_to_html_node(tn))
            elif next_kind == "code":
                tn = TextNode(inner, TextType.CODE)
                nodes.append(text_node_to_html_node(tn))

            s = s[next_match.end() :]

        return nodes

    blocks = markdown_to_blocks(markdown)
    nodes = []

    for block in blocks:
        bt = block_to_block_type(block)

        # Heading
        if bt == BlockType.HEADING:
            s = block.lstrip()
            m = re.match(r"^(#+)\s*(.*)$", s)
            level = len(m.group(1)) if m else 1
            text = m.group(2).strip() if m else s
            tag = f"h{min(level, 6)}"
            children = text_to_children(text)
            nodes.append(ParentNode(tag, children))

        # Code fence: do NOT perform inline parsing of its contents
        elif bt == BlockType.CODE:
            lines = block.splitlines()
            first = lines[0].strip() if lines else "`````"
            if len(lines) >= 3 and lines[-1].strip().startswith("```"):
                content = "\n".join(lines[1:-1])
            else:
                content = "\n".join(lines[1:])
            # Ensure trailing newline if not present, to match tests
            if content and not content.endswith("\n"):
                content += "\n"
            # create a TextNode with CODE type and convert to HtmlNode using helper
            txt_node = TextNode(content, TextType.CODE)
            code_html_node = text_node_to_html_node(txt_node)
            # wrap code element in a pre tag
            nodes.append(ParentNode("pre", [code_html_node]))

        # Quote
        elif bt == BlockType.QUOTE:
            qlines = [re.sub(r"^\s*>\s?", "", l) for l in block.splitlines()]
            inner = "\n".join(qlines).strip()
            children = text_to_children(inner)
            nodes.append(ParentNode("blockquote", children))

        # Ordered / unordered lists
        elif bt in (BlockType.ORDERED_LIST, BlockType.UNORDERED_LIST):
            lines = [l for l in block.splitlines() if l.strip()]
            items = []
            for line in lines:
                if bt == BlockType.ORDERED_LIST:
                    item_text = _ORDERED_LIST_RE.sub("", line)
                else:
                    item_text = _UNORDERED_LIST_RE.sub("", line)
                item_children = text_to_children(item_text.strip())
                items.append(ParentNode("li", item_children))
            container = "ol" if bt == BlockType.ORDERED_LIST else "ul"
            nodes.append(ParentNode(container, items))

        # Paragraph / fallback
        else:
            children = text_to_children(block)
            nodes.append(ParentNode("p", children))

    # Wrap all block nodes in a single div parent and return it
    return ParentNode("div", nodes)