import os
import sys

# make sure the directory above src (project root) is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from htmlnode import HtmlNode, LeafNode, ParentNode


def test_props_to_html_none():
    node = HtmlNode(tag="div")
    # props default to None, should return empty string
    assert node.props_to_html() == ""


def test_props_to_html_empty_dict():
    node = HtmlNode(tag="span", props={})
    # empty props should also produce empty string
    assert node.props_to_html() == ""


def test_props_to_html_single():
    node = HtmlNode(tag="img", props={"src": "foo.png"})
    # note leading space is added before each attribute
    assert node.props_to_html() == ' src="foo.png"'


def test_props_to_html_multiple():
    # order of attributes in a dict is insertion order, so we can rely on it here
    props = {"id": "main", "class": "container"}
    node = HtmlNode(tag="div", props=props)
    assert node.props_to_html() == ' id="main" class="container"'


def test_repr():
    node = HtmlNode(tag="p", value="hello", children=[], props={"style": "color:red"})
    expected = "HtmlNode(tag='p', value='hello', children=[], props={'style': 'color:red'})"
    assert repr(node) == expected


def test_leafnode_to_html_text_only():
    leaf = LeafNode(tag=None, value="just text")
    assert leaf.to_html() == "just text"


def test_leafnode_to_html_with_tag_and_props():
    leaf = LeafNode(tag="span", value="hi", props={"class": "greet"})
    assert leaf.to_html() == '<span class="greet">hi</span>'


def test_leafnode_to_html_missing_value_raises():
    leaf = LeafNode(tag="div", value=None)
    try:
        leaf.to_html()
        assert False, "Expected ValueError when value is None"
    except ValueError as e:
        assert str(e) == "LeafNode must have a value"


def test_leafnode_repr():
    leaf = LeafNode(tag="b", value="bold", props={"id": "x"})
    expected = "LeafNode(tag='b', value='bold', props={'id': 'x'})"
    assert repr(leaf) == expected


def test_to_html_with_children():
    child_node = LeafNode("span", "child")
    parent_node = ParentNode("div", [child_node])
    assert parent_node.to_html() == "<div><span>child</span></div>"


def test_to_html_with_grandchildren():
    grandchild_node = LeafNode("b", "grandchild")
    child_node = ParentNode("span", [grandchild_node])
    parent_node = ParentNode("div", [child_node])
    assert parent_node.to_html() == "<div><span><b>grandchild</b></span></div>"


def test_parentnode_no_tag_raises():
    try:
        parent = ParentNode(None, [LeafNode("p", "test")])
        assert False, "Expected ValueError for no tag"
    except ValueError as e:
        assert str(e) == "ParentNode must have a tag"


def test_parentnode_no_children_raises():
    try:
        parent = ParentNode("div", None)
        assert False, "Expected ValueError for no children"
    except ValueError as e:
        assert str(e) == "ParentNode must have children"


def test_parentnode_empty_children_list():
    try:
        parent = ParentNode("div", [])
        parent.to_html()
        assert False, "Expected ValueError for empty children"
    except ValueError as e:
        assert str(e) == "ParentNode requires at least one child"


def test_parentnode_multiple_children():
    child1 = LeafNode("p", "first")
    child2 = LeafNode("p", "second")
    parent = ParentNode("div", [child1, child2])
    assert parent.to_html() == "<div><p>first</p><p>second</p></div>"


def test_parentnode_nested():
    inner = ParentNode("span", [LeafNode("b", "bold")])
    outer = ParentNode("div", [inner])
    assert outer.to_html() == "<div><span><b>bold</b></span></div>"


def test_parentnode_with_props():
    child = LeafNode("p", "content")
    parent = ParentNode("div", [child], props={"class": "container", "id": "main"})
    assert parent.to_html() == '<div class="container" id="main"><p>content</p></div>'


def test_parentnode_mixed_children():
    leaf = LeafNode("span", "text")
    parent_child = ParentNode("p", [LeafNode("em", "emphasis")])
    parent = ParentNode("div", [leaf, parent_child])
    assert parent.to_html() == "<div><span>text</span><p><em>emphasis</em></p></div>"


def test_parentnode_repr():
    child = LeafNode("b", "bold")
    parent = ParentNode("div", [child], props={"id": "test"})
    expected = "ParentNode(tag='div', children=[LeafNode(tag='b', value='bold', props=None)], props={'id': 'test'})"
    assert repr(parent) == expected


if __name__ == "__main__":
    test_props_to_html_none()
    test_props_to_html_empty_dict()
    test_props_to_html_single()
    test_props_to_html_multiple()
    test_repr()
    test_leafnode_to_html_text_only()
    test_leafnode_to_html_with_tag_and_props()
    test_leafnode_to_html_missing_value_raises()
    test_leafnode_repr()
    test_to_html_with_children()
    test_to_html_with_grandchildren()
    test_parentnode_no_tag_raises()
    test_parentnode_no_children_raises()
    test_parentnode_empty_children_list()
    test_parentnode_multiple_children()
    test_parentnode_nested()
    test_parentnode_with_props()
    test_parentnode_mixed_children()
    test_parentnode_repr()
    print("all htmlnode tests passed")
