import unittest
from textnode import TextNode, TextType

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def not_eq_type(self):
        node = TextNode("This is a node", TextType.BOLD)
        node2 = TextNode("This is a node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_url(self):
        node = TextNode("This is a node", TextType.LINK, "https://ignotus.dev")
        node2 = TextNode("This is a node", TextType.LINK, None)
        self.assertNotEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("This is a node", TextType.LINK, "https://ignotus.dev/logo.png")
        node2 = TextNode("This is a node", TextType.LINK, "https://ignotus.dev/logo.png")
        self.assertEqual(node, node2)

    def test_not_eq_text(self):
        node = TextNode("Text A", TextType.TEXT)
        node2 = TextNode("Text B", TextType.TEXT)
        self.assertNotEqual(node, node2)


if __name__ == "__main__":
    unittest.main()
