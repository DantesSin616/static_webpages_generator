from src.textnode import TextType


class HtmlNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    

    def to_html(self):
        raise NotImplementedError("Subclasses must implement to_html method")
    

    def props_to_html(self):
        # convert dictionary of props into HTML attributes string
        # e.g. {'id': 'main', 'class': 'foo'} -> ' id="main" class="foo"'
        if not self.props:
            return ""

        html_props = ""
        for prop, val in self.props.items():
            html_props += f' {prop}="{val}"'
        return html_props


    def __repr__(self):
        # return a descriptive representation of what was inputed 
        return (
            f"HtmlNode(tag={self.tag!r}, value={self.value!r}, "
            f"children={self.children!r}, props={self.props!r})"
        )


class LeafNode(HtmlNode):
    def __init__(self, tag, value, props=None):

        super().__init__(tag, value, None, props) 
        # we use the super() function to call the father's constructor
        # so we inherited the attributes without repeting yourself 


    def to_html(self):
        # check for required value unless tag is a void element
        void_elements = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
        if self.tag is None:
            if self.value is None:
                raise ValueError("LeafNode must have a value")
            return self.value

        if self.tag in void_elements:
            return f"<{self.tag}{self.props_to_html()} />"

        if self.value is None:
            raise ValueError("LeafNode must have a value")

        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"


    def __repr__(self):
        return (
            f"LeafNode(tag={self.tag!r}, value={self.value!r}, "
            f"props={self.props!r})"
        )


class ParentNode(HtmlNode):
    def __init__(self, tag, children, props=None):
        if tag is None:
            raise ValueError("ParentNode must have a tag")
        if children is None:
            raise ValueError("ParentNode must have children")
        super().__init__(tag, None, children, props)


    def to_html(self):
        if not self.tag:
            raise ValueError("ParentNode requires a tag")
        if not self.children:
            raise ValueError("ParentNode requires at least one child")
        children_html = ""
        for child in self.children:
            children_html += child.to_html()
        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"


    def __repr__(self):
        return (
            f"ParentNode(tag={self.tag!r}, children={self.children!r}, "
            f"props={self.props!r})"
        )


def text_node_to_html_node(text_node):
    import html

    # If not a TextNode, just escape and return as text
    if not hasattr(text_node, "text_type"):
        return LeafNode(None, html.escape(str(getattr(text_node, "text", text_node))))

    ttype = text_node.text_type

    if ttype == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if ttype == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if ttype == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if ttype == TextType.CODE:
        return LeafNode("code", text_node.text)
    if ttype == TextType.LINK:
        return LeafNode("a", text_node.text, props={"href": getattr(text_node, "url") or ""})
    if ttype == TextType.IMAGE:
        return LeafNode("img", "", props={
            "src": getattr(text_node, "url") or "",
            "alt": text_node.text,
        })
    # Raise exception for unknown types
    raise ValueError(f"Unknown TextType: {ttype}")
