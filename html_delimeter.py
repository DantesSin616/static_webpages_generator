from htmlnode import HtmlNode
from src.textnode import TextNode, TextType


def split_nodes_delimeter(old_nodes, delimeter, text_type):
    new_nodes = []

    for node in old_nodes:
        if old_nodes[node] != TextType.TEXT():
            new_nodes += old_nodes[node]

            # this is supposed to check for open-and-closing delimeters
