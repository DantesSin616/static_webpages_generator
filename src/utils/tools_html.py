import re

from src.nodes.textnode import TextNode, TextType


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
                new_nodes.append(TextNode(part, node.text_type))
            else:
                # Odd index: delimited text (e.g., bold)
                new_nodes.append(TextNode(part, text_type))
    return new_nodes


def extract_markdown_images(text):
    # regex pattern for images files with its alt text
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    img_matches = re.findall(pattern, text)
    return img_matches


def extract_markdown_links(text):
    # regex patter for regular links
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    link_matches = re.findall(pattern, text)
    return link_matches
