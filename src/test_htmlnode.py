import os
import sys

# make sure the directory above src (project root) is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from htmlnode import HtmlNode


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


if __name__ == "__main__":
    test_props_to_html_none()
    test_props_to_html_empty_dict()
    test_props_to_html_single()
    test_props_to_html_multiple()
    test_repr()
    print("all htmlnode tests passed")
