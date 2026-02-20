from enum import Enum


def main():
    return True

class TextType(Enum):

    BOLD_TEXT = "**Bold text**"
    ITALIC_TEXT = "_Italic text_"
    CODE_TEXT = `Code Text`
    LINK = "[anchor](url)"
    IMAGES = "![alt text](url)"



class TextNode(text, text_type, url):

    self.text = text 
    self.text_type = text_type
    self.url = url

    def __eq__(self):
        if self == TextNode()
            return True

    def __repr__(self):
        return 

main()
