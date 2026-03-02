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
        # return a descriptive representation instead of printing
        return (
            f"HtmlNode(tag={self.tag!r}, value={self.value!r}, "
            f"children={self.children!r}, props={self.props!r})"
        )