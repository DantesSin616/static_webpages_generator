import os
import sys
import unittest

# make sure the directory above src (project root) is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from htmlnode import HtmlNode, LeafNode, ParentNode, text_node_to_html_node
from src.textnode import TextNode, TextType


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
        node = HtmlNode(tag="p", value="hello", children=[], props={"style": "color:red"})
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
        self.assertEqual(parent_node.to_html(), "<div><span><b>grandchild</b></span></div>")


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
        self.assertEqual(parent.to_html(), '<div class="container" id="main"><p>content</p></div>')


    def test_parentnode_mixed_children(self):
        leaf = LeafNode("span", "text")
        parent_child = ParentNode("p", [LeafNode("em", "emphasis")])
        parent = ParentNode("div", [leaf, parent_child])
        self.assertEqual(parent.to_html(), "<div><span>text</span><p><em>emphasis</em></p></div>")


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
        self.assertEqual(html_node.props, {"src": "http://example.com/img.png", "alt": "alt text"})


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
