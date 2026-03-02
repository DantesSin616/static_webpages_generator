class HtmlNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
    
    def to_html(self):
        raise NotImplementedError("Subclasses must implement to_html method")
    
    def props_to_html(self):
        if self.props is None:
            return ""

        html_props = ""
        for prop in self.props:
            html_props += f'{prop} = "{self.props[prop]}"'
    
    def __repr__(self):

        print(
            self.tag,
            self.value,
            self.children,
            self.props
        )