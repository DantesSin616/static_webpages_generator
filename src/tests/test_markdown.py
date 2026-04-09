import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.markdown_html import (
    markdown_to_blocks,
    block_to_block_type,
    MARKDOWN_BLOCK_MARKERS,
)
from src.nodes.textnode import BlockType


class TestMarkdownToBlocks(unittest.TestCase):
    def test_empty_none(self):
        self.assertEqual(markdown_to_blocks(None), [])

    def test_empty_whitespace(self):
        self.assertEqual(markdown_to_blocks("   \n  \t\n"), [])

    def test_single_paragraph(self):
        text = "This is a single paragraph without blank lines."
        self.assertEqual(markdown_to_blocks(text), [text])

    def test_multiple_paragraphs(self):
        text = "First paragraph.\n\nSecond paragraph."
        self.assertEqual(markdown_to_blocks(text), ["First paragraph.", "Second paragraph."])

    def test_multiple_blank_lines_and_spaces(self):
        text = "\nFirst paragraph.\n\n  \nSecond paragraph.\n\n\nThird paragraph.\n"
        self.assertEqual(
            markdown_to_blocks(text),
            ["First paragraph.", "Second paragraph.", "Third paragraph."],
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_code_fence(self):
        self.assertEqual(block_to_block_type("```\ncode\n```"), BlockType.CODE)

    def test_quote(self):
        self.assertEqual(block_to_block_type("> a quote"), BlockType.QUOTE)

    def test_ordered_list(self):
        self.assertEqual(block_to_block_type("1. First item"), BlockType.ORDERED_LIST)

    def test_unordered_list(self):
        self.assertEqual(block_to_block_type("- item"), BlockType.UNORDERED_LIST)

    def test_paragraph(self):
        self.assertEqual(block_to_block_type("Just a paragraph."), BlockType.PARAGRAPH)


class TestMarkersMapping(unittest.TestCase):
    def test_all_blocktypes_present(self):
        keys = set(MARKDOWN_BLOCK_MARKERS.keys())
        self.assertTrue(all(bt in keys for bt in BlockType))

    def test_values_are_strings(self):
        for v in MARKDOWN_BLOCK_MARKERS.values():
            self.assertIsInstance(v, str)


class TestRoundtrip(unittest.TestCase):
    def test_roundtrip_various_blocks(self):
        md = """
# Title

This is a paragraph.

- item one
- item two

1. first
2. second

> a quote

```
code
```
"""
        blocks = markdown_to_blocks(md)
        types = [block_to_block_type(b) for b in blocks]
        expected = [
            BlockType.HEADING,
            BlockType.PARAGRAPH,
            BlockType.UNORDERED_LIST,
            BlockType.ORDERED_LIST,
            BlockType.QUOTE,
            BlockType.CODE,
        ]
        self.assertEqual(types, expected)


if __name__ == "__main__":
    unittest.main()
