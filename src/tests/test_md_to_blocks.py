import os
import sys
import unittest

# ensure project root is on import path (like other tests)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.markdow_html import markdown_to_blocks


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


if __name__ == "__main__":
	unittest.main()
