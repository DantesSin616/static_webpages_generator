from htmlnode import HtmlNode
from src.textnode import TextNode, TextType


def split_nodes_delimeter(old_nodes, delimeter, text_type):
    new_nodes = []

    for node in old_nodes:
        # Skip non-text nodes (HTML nodes, etc.)
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        # Empty text nodes produce no output
        if not node.text:
            continue

        # split the text by the delimiter
        parts = node.text.split(delimeter)

        # check for unclosed delimiters
        if len(parts) % 2 == 0:
            raise Exception("Invalid delimeter syntax: unclosed delimeter")

        # Process each part
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Even index: normal text
                new_nodes.append(TextNode(part, text_type))
            else:
                # Odd index: delimited text (e.g., bold)
                new_nodes.append(TextNode(part, TextType.BOLD))

    return new_nodes
