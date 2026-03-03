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
        # check for required value
        if self.value is None:
            raise ValueError("LeafNode must have a value")

        # if tag is None, returns it as flat text
        if self.tag is None:
            return self.value

        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"


    def __repr__(self):
        return (
            f"LeafNode(tag={self.tag!r}, value={self.value!r}, "
            f"props={self.props!r})"
        )