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


def split_nodes_images(old_nodes):
    new_nodes = []

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

        # Find markdown image spans and split the text node into pieces
        pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
        matches = list(re.finditer(pattern, node.text))

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
            alt_text = m.group(1)
            url = m.group(2)
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url=url))

            last_idx = end

        # trailing text after last image
        if last_idx < len(node.text):
            tail = node.text[last_idx:]
            new_nodes.append(TextNode(tail, node.text_type))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

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

        # Find markdown link spans and split the text node into pieces
        pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
        matches = list(re.finditer(pattern, node.text))

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
            link_text = m.group(1)
            url = m.group(2)
            new_nodes.append(TextNode(link_text, TextType.LINK, url=url))

            last_idx = end

        # trailing text after last link
        if last_idx < len(node.text):
            tail = node.text[last_idx:]
            new_nodes.append(TextNode(tail, node.text_type))

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
