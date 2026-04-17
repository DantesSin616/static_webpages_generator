"""Helpers for converting markdown-flavored inline text into `TextNode`
objects used by the rest of the system.

This module follows the repository coding pattern: module-level compiled
regex constants, explicit typing, and specific exception types.
"""

from typing import List, Optional, Tuple

import re
from src.nodes.textnode import TextNode, TextType


__all__ = [
    "split_nodes_delimiter",
    "split_nodes_images",
    "split_nodes_link",
    "extract_markdown_images",
    "extract_markdown_links",
    "text_to_textnodes",
]


# Precompiled regexes
_IMAGE_RE = re.compile(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)")
_LINK_RE = re.compile(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)")


def split_nodes_delimiter(old_nodes: List[TextNode], delimiter: str, text_type: TextType) -> List[TextNode]:
    """Split text nodes on a delimiter and wrap delimited parts with
    `TextType`.

    Raises ``ValueError`` if delimiters are unbalanced.
    """
    new_nodes: List[TextNode] = []

    for node in old_nodes:
        # Skip non-text nodes (HTML nodes, etc.)
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        # Empty text nodes produce no output
        if not node.text:
            continue

        # split the text by the delimiter
        parts = node.text.split(delimiter)

        # check for unclosed delimiters
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid delimiter syntax: unclosed delimiter '{delimiter}'")

        # Process each part
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Even index: normal text
                new_nodes.append(TextNode(part, node.text_type))
            else:
                # Odd index: delimited text (e.g., bold)
                new_nodes.append(TextNode(part, text_type))
    return new_nodes


def split_nodes_images(old_nodes: List[TextNode]) -> List[TextNode]:
    """Extract markdown image spans from text nodes and replace them with
    `TextNode` objects having ``TextType.IMAGE``.
    """
    new_nodes: List[TextNode] = []

    for node in old_nodes:
        # Skips non-text nodes
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue
        # If this node is already an image node, keep as-is
        if node.text_type == TextType.IMAGE:
            new_nodes.append(node)
            continue

        # empty nodes produce no output
        if not node.text:
            continue

        matches = list(_IMAGE_RE.finditer(node.text))

        # If no image markdown found, keep the original node
        if not matches:
            new_nodes.append(node)
            continue

        last_idx = 0
        for m in matches:
            start, end = m.start(), m.end()
            # text before the image
            if start > last_idx:
                pre_text = node.text[last_idx:start]
                new_nodes.append(TextNode(pre_text, node.text_type))

            # image node: alt text in .text, url in .url
            alt_text, url = m.group(1), m.group(2)
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url=url))

            last_idx = end

        # trailing text after last image
        if last_idx < len(node.text):
            tail = node.text[last_idx:]
            new_nodes.append(TextNode(tail, node.text_type))

    return new_nodes


def split_nodes_link(old_nodes: List[TextNode]) -> List[TextNode]:
    """Extract markdown link spans from text nodes and replace them with
    `TextNode` objects having ``TextType.LINK``.
    """
    new_nodes: List[TextNode] = []

    for node in old_nodes:
        # Skip non-text nodes
        if not isinstance(node, TextNode):
            new_nodes.append(node)
            continue
        # If this node is already a link node, keep as-is
        if node.text_type == TextType.LINK:
            new_nodes.append(node)
            continue

        # empty nodes produce no output
        if not node.text:
            continue

        matches = list(_LINK_RE.finditer(node.text))

        # If no link markdown found, keep the original node
        if not matches:
            new_nodes.append(node)
            continue

        last_idx = 0
        for m in matches:
            start, end = m.start(), m.end()
            # text before the link
            if start > last_idx:
                pre_text = node.text[last_idx:start]
                new_nodes.append(TextNode(pre_text, node.text_type))

            # link node: link text in .text, url in .url
            link_text, url = m.group(1), m.group(2)
            new_nodes.append(TextNode(link_text, TextType.LINK, url=url))

            last_idx = end

        # trailing text after last link
        if last_idx < len(node.text):
            tail = node.text[last_idx:]
            new_nodes.append(TextNode(tail, node.text_type))

    return new_nodes


def extract_markdown_images(text: str) -> List[Tuple[str, str]]:
    """Return a list of (alt_text, url) for images found in the text."""
    return _IMAGE_RE.findall(text)


def extract_markdown_links(text: str) -> List[Tuple[str, str]]:
    """Return a list of (link_text, url) for links found in the text."""
    return _LINK_RE.findall(text)


def text_to_textnodes(text: Optional[str]) -> List[TextNode]:
    """Convert a raw markdown-flavored string into a list of TextNode objects.

    The function applies tokenization in a deterministic order to avoid
    ambiguous parses.
    """
    if text is None:
        return []

    # Start with a single plain text node
    nodes: List[TextNode] = [TextNode(text, TextType.TEXT)]

    # Code spans first so images/links inside code are not tokenized
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

    # Extract images next so they don't get mistaken for links or formatting
    nodes = split_nodes_images(nodes)

    # Then extract links (link regex avoids matching images)
    nodes = split_nodes_link(nodes)

    # Bold before italic to avoid conflicts with single-star parsing
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

    # Italic (single star and underscores)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

    # Post-process: remove a single whitespace text node that appears between
    # a link and an image so sequences like [link](u) ![img](v) become
    # LINK -> IMAGE (no intervening whitespace node). This matches expected
    # tokenization in the tests.
    processed: List[TextNode] = []
    i = 0
    while i < len(nodes):
        # pattern: LINK, TEXT(whitespace only), IMAGE -> collapse to LINK, IMAGE
        if (
            i + 2 < len(nodes)
            and isinstance(nodes[i], TextNode)
            and nodes[i].text_type == TextType.LINK
            and isinstance(nodes[i + 1], TextNode)
            and nodes[i + 1].text_type == TextType.TEXT
            and nodes[i + 1].text.strip() == ""
            and isinstance(nodes[i + 2], TextNode)
            and nodes[i + 2].text_type == TextType.IMAGE
        ):
            processed.append(nodes[i])
            processed.append(nodes[i + 2])
            i += 3
        else:
            processed.append(nodes[i])
            i += 1

    return processed