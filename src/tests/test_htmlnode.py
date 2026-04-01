import os
import sys
import unittest

# make sure the directory above src (project root) is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.tools_html import (
    split_nodes_delimeter,
    split_nodes_images,
    split_nodes_link,
    text_to_textnodes,
    extract_markdown_images,
    extract_markdown_links,
)
from src.nodes.htmlnode import HtmlNode, LeafNode, ParentNode, text_node_to_html_node
from src.nodes.textnode import TextNode, TextType


class TestHtmlNode(unittest.TestCase):
    def test_props_to_html_none(self):
        node = HtmlNode(tag="div")
        # props default to None, should return empty string
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty_dict(self):
        node = HtmlNode(tag="span", props={})
        # empty props should also produce empty string
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single(self):
        node = HtmlNode(tag="img", props={"src": "foo.png"})
        # note leading space is added before each attribute
        self.assertEqual(node.props_to_html(), ' src="foo.png"')

    def test_props_to_html_multiple(self):
        # order of attributes in a dict is insertion order, so we can rely on it here
        props = {"id": "main", "class": "container"}
        node = HtmlNode(tag="div", props=props)
        self.assertEqual(node.props_to_html(), ' id="main" class="container"')

    def test_repr(self):
        node = HtmlNode(
            tag="p", value="hello", children=[], props={"style": "color:red"}
        )
        expected = "HtmlNode(tag='p', value='hello', children=[], props={'style': 'color:red'})"
        self.assertEqual(repr(node), expected)

    def test_leafnode_to_html_text_only(self):
        leaf = LeafNode(tag=None, value="just text")
        self.assertEqual(leaf.to_html(), "just text")

    def test_leafnode_to_html_with_tag_and_props(self):
        leaf = LeafNode(tag="span", value="hi", props={"class": "greet"})
        self.assertEqual(leaf.to_html(), '<span class="greet">hi</span>')

    def test_leafnode_to_html_missing_value_raises(self):
        leaf = LeafNode(tag="div", value=None)
        with self.assertRaises(ValueError) as cm:
            leaf.to_html()
        self.assertEqual(str(cm.exception), "LeafNode must have a value")

    def test_leafnode_repr(self):
        leaf = LeafNode(tag="b", value="bold", props={"id": "x"})
        expected = "LeafNode(tag='b', value='bold', props={'id': 'x'})"
        self.assertEqual(repr(leaf), expected)

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(), "<div><span><b>grandchild</b></span></div>"
        )

    def test_parentnode_no_tag_raises(self):
        with self.assertRaises(ValueError) as cm:
            parent = ParentNode(None, [LeafNode("p", "test")])
        self.assertEqual(str(cm.exception), "ParentNode must have a tag")

    def test_parentnode_no_children_raises(self):
        with self.assertRaises(ValueError) as cm:
            parent = ParentNode("div", None)
        self.assertEqual(str(cm.exception), "ParentNode must have children")

    def test_parentnode_empty_children_list(self):
        parent = ParentNode("div", [])
        with self.assertRaises(ValueError) as cm:
            parent.to_html()
        self.assertEqual(str(cm.exception), "ParentNode requires at least one child")

    def test_parentnode_multiple_children(self):
        child1 = LeafNode("p", "first")
        child2 = LeafNode("p", "second")
        parent = ParentNode("div", [child1, child2])
        self.assertEqual(parent.to_html(), "<div><p>first</p><p>second</p></div>")

    def test_parentnode_nested(self):
        inner = ParentNode("span", [LeafNode("b", "bold")])
        outer = ParentNode("div", [inner])
        self.assertEqual(outer.to_html(), "<div><span><b>bold</b></span></div>")

    def test_parentnode_with_props(self):
        child = LeafNode("p", "content")
        parent = ParentNode("div", [child], props={"class": "container", "id": "main"})
        self.assertEqual(
            parent.to_html(), '<div class="container" id="main"><p>content</p></div>'
        )

    def test_parentnode_mixed_children(self):
        leaf = LeafNode("span", "text")
        parent_child = ParentNode("p", [LeafNode("em", "emphasis")])
        parent = ParentNode("div", [leaf, parent_child])
        self.assertEqual(
            parent.to_html(), "<div><span>text</span><p><em>emphasis</em></p></div>"
        )

    def test_parentnode_repr(self):
        child = LeafNode("b", "bold")
        parent = ParentNode("div", [child], props={"id": "test"})
        expected = "ParentNode(tag='div', children=[LeafNode(tag='b', value='bold', props=None)], props={'id': 'test'})"
        self.assertEqual(repr(parent), expected)

    def test_text_node_to_html_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_text_node_to_html_bold(self):
        node = TextNode("bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold text")

    def test_text_node_to_html_italic(self):
        node = TextNode("italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italic text")

    def test_text_node_to_html_code(self):
        node = TextNode("code text", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "code text")

    def test_text_node_to_html_link(self):
        node = TextNode("link text", TextType.LINK, "http://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "link text")
        self.assertEqual(html_node.props, {"href": "http://example.com"})

    def test_text_node_to_html_image(self):
        node = TextNode("alt text", TextType.IMAGE, "http://example.com/img.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props, {"src": "http://example.com/img.png", "alt": "alt text"}
        )

    def test_text_node_to_html_unknown_type_raises(self):
        node = TextNode("text", "unknown")
        with self.assertRaises(ValueError) as cm:
            text_node_to_html_node(node)
        self.assertIn("Unknown TextType", str(cm.exception))

    def test_text_node_to_html_non_textnode(self):
        html_node = text_node_to_html_node("plain string")
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "plain string")

    def test_text_node_to_html_none_input(self):
        html_node = text_node_to_html_node(None)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "None")

    def test_text_node_to_html_link_no_url(self):
        node = TextNode("link text", TextType.LINK, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.props, {"href": ""})

    def test_text_node_to_html_image_no_url(self):
        node = TextNode("alt text", TextType.IMAGE, None)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.props, {"src": "", "alt": "alt text"})

    # Tests for split_nodes_delimeter
    def test_split_nodes_valid_delimiter(self):
        old_nodes = [TextNode("Hello, **world**!", TextType.TEXT)]
        delimiter = "**"
        result = split_nodes_delimeter(old_nodes, delimiter, TextType.BOLD)
        expected = [
            TextNode("Hello, ", TextType.TEXT),
            TextNode("world", TextType.BOLD),
            TextNode("!", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_unclosed_delimiter(self):
        old_nodes = [TextNode("Hello, **world!", TextType.TEXT)]
        delimiter = "**"
        with self.assertRaises(Exception) as context:
            split_nodes_delimeter(old_nodes, delimiter, TextType.TEXT)
        self.assertEqual(
            str(context.exception), "Invalid delimeter syntax: unclosed delimeter"
        )

    def test_split_nodes_empty_text(self):
        old_nodes = [TextNode("", TextType.TEXT)]
        delimiter = "**"
        result = split_nodes_delimeter(old_nodes, delimiter, TextType.BOLD)
        self.assertEqual(result, [])

    def test_split_nodes_no_delimiter(self):
        old_nodes = [TextNode("Hello, world!", TextType.TEXT)]
        delimiter = "**"
        result = split_nodes_delimeter(old_nodes, delimiter, TextType.BOLD)
        self.assertEqual(result, [TextNode("Hello, world!", TextType.TEXT)])

    def test_split_nodes_multiple_delimiters(self):
        old_nodes = [TextNode("**Hello**, **world**!", TextType.TEXT)]
        delimiter = "**"
        result = split_nodes_delimeter(old_nodes, delimiter, TextType.BOLD)
        expected = [
            TextNode("", TextType.TEXT),
            TextNode("Hello", TextType.BOLD),
            TextNode(", ", TextType.TEXT),
            TextNode("world", TextType.BOLD),
            TextNode("!", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_different_delimiter(self):
        old_nodes = [TextNode("Hello, __world__!", TextType.TEXT)]
        delimiter = "__"
        result = split_nodes_delimeter(old_nodes, delimiter, TextType.BOLD)
        expected = [
            TextNode("Hello, ", TextType.TEXT),
            TextNode("world", TextType.BOLD),
            TextNode("!", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_mixed_content(self):
        old_nodes = [
            TextNode("Hello, **world**!", TextType.TEXT),
            TextNode("This is plain text.", TextType.TEXT),
        ]
        delimiter = "**"
        result = split_nodes_delimeter(old_nodes, delimiter, TextType.BOLD)
        expected = [
            TextNode("Hello, ", TextType.TEXT),
            TextNode("world", TextType.BOLD),
            TextNode("!", TextType.TEXT),
            TextNode("This is plain text.", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_non_text_nodes(self):
        old_nodes = [
            HtmlNode("<div>"),
            TextNode("Hello, **world**!", TextType.TEXT),
            HtmlNode("</div>"),
        ]
        delimiter = "**"
        result = split_nodes_delimeter(old_nodes, delimiter, TextType.BOLD)
        expected = [
            HtmlNode("<div>"),
            TextNode("Hello, ", TextType.TEXT),
            TextNode("world", TextType.BOLD),
            TextNode("!", TextType.TEXT),
            HtmlNode("</div>"),
        ]
        self.assertEqual(result, expected)

    # Tests for extract_markdown_images
    def test_extract_markdown_images_basic(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("image", "https://i.imgur.com/zjjcJKZ.png")])

    def test_extract_markdown_images_multiple(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)"
        matches = extract_markdown_images(text)
        self.assertEqual(
            matches,
            [
                ("image", "https://i.imgur.com/zjjcJKZ.png"),
                ("second image", "https://i.imgur.com/3elNhQu.png"),
            ],
        )

    def test_extract_markdown_images_none(self):
        text = "This is simply some text without images."
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [])

    def test_extract_markdown_images_empty(self):
        text = ""
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [])

    def test_extract_markdown_images_with_links(self):
        text = "This is a link [link text](https://www.google.com) and an image ![img](https://i.imgur.com/123.png)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("img", "https://i.imgur.com/123.png")])

    def test_extract_markdown_images_no_url(self):
        text = "An image with no url ![alt]()"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("alt", "")])

    def test_extract_markdown_images_no_alt(self):
        text = "An image with no alt text ![](https://url.com)"
        matches = extract_markdown_images(text)
        self.assertEqual(matches, [("", "https://url.com")])

    # Tests for extract_markdown_links
    def test_extract_markdown_links_basic(self):
        text = "This is text with a [link](https://boot.dev)"
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [("link", "https://boot.dev")])

    def test_extract_markdown_links_multiple(self):
        text = "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertEqual(
            matches,
            [
                ("link", "https://boot.dev"),
                ("another link", "https://blog.boot.dev"),
            ],
        )

    def test_extract_markdown_links_none(self):
        text = "Text without any links here."
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [])

    def test_extract_markdown_links_empty(self):
        text = ""
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [])

    def test_extract_markdown_links_with_images(self):
        text = "Here is an image ![img](url) and a [link](url2)"
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [("link", "url2")])

    def test_extract_markdown_links_no_url(self):
        text = "Here is a [link]() with no URL"
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [("link", "")])

    def test_extract_markdown_links_no_text(self):
        text = "Here is a link with no text [](https://boot.dev)"
        matches = extract_markdown_links(text)
        self.assertEqual(matches, [("", "https://boot.dev")])

    # Tests for split_nodes_images
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_images([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_images_no_images(self):
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_images([node])
        self.assertEqual(new_nodes, [TextNode("Just plain text", TextType.TEXT)])

    def test_split_images_empty_text(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_images([node])
        self.assertEqual(new_nodes, [])

    def test_split_images_mixed_nodes(self):
        old_nodes = [HtmlNode("<div>"), TextNode("A ![img](url)", TextType.TEXT), HtmlNode("</div>")]
        new_nodes = split_nodes_images(old_nodes)
        expected = [HtmlNode("<div>"), TextNode("A ", TextType.TEXT), TextNode("img", TextType.IMAGE, "url"), HtmlNode("</div>")]
        self.assertEqual(new_nodes, expected)

    # Tests for split_nodes_link
    def test_split_links_basic(self):
        node = TextNode("This is a [link](https://boot.dev) here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This is a ", TextType.TEXT), TextNode("link", TextType.LINK, "https://boot.dev"), TextNode(" here", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_split_links_no_links(self):
        node = TextNode("No links here", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(new_nodes, [TextNode("No links here", TextType.TEXT)])

    def test_split_links_multiple(self):
        node = TextNode("One [a](u1) and [b](u2)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("One ", TextType.TEXT), TextNode("a", TextType.LINK, "u1"), TextNode(" and ", TextType.TEXT), TextNode("b", TextType.LINK, "u2")]
        self.assertEqual(new_nodes, expected)

    def test_split_links_with_image_present(self):
        node = TextNode("Image ![img](url) and a [link](url2)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("Image ![img](url) and a ", TextType.TEXT), TextNode("link", TextType.LINK, "url2")]
        self.assertEqual(new_nodes, expected)

    def test_split_links_empty_text(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertEqual(new_nodes, [])

    def test_split_links_already_link_node(self):
        node = TextNode("link text", TextType.LINK, "http://example.com")
        new_nodes = split_nodes_link([node])
        self.assertEqual(new_nodes, [node])

    # Additional tests for edge cases and combined parsing
    def test_split_images_adjacent(self):
        node = TextNode("![a](u1)![b](u2)", TextType.TEXT)
        new_nodes = split_nodes_images([node])
        expected = [
            TextNode("a", TextType.IMAGE, "u1"),
            TextNode("b", TextType.IMAGE, "u2"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_empty_url(self):
        node = TextNode("A ![alt]() end", TextType.TEXT)
        new_nodes = split_nodes_images([node])
        expected = [
            TextNode("A ", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, ""),
            TextNode(" end", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_split_images_only_image(self):
        node = TextNode("![img](url)", TextType.TEXT)
        new_nodes = split_nodes_images([node])
        expected = [TextNode("img", TextType.IMAGE, "url")]
        self.assertEqual(new_nodes, expected)

    def test_split_links_adjacent(self):
        node = TextNode("[a](u1)[b](u2)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("a", TextType.LINK, "u1"), TextNode("b", TextType.LINK, "u2")]
        self.assertEqual(new_nodes, expected)

    def test_split_links_empty_url(self):
        node = TextNode("Here is a [link]() end", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("Here is a ", TextType.TEXT), TextNode("link", TextType.LINK, ""), TextNode(" end", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_text_to_textnodes_complex(self):
        text = "Hello **bold** *italic* `code` [link](u) ![img](v)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Hello ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("link", TextType.LINK, "u"),
            TextNode("img", TextType.IMAGE, "v"),
        ]
        self.assertEqual(nodes, expected)

    def test_text_to_textnodes_none(self):
        self.assertEqual(text_to_textnodes(None), [])
