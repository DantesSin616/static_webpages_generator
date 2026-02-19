from enum import Enum

class TextType(Enum):

    BOLD_TEXT = **Bold text**
    ITALIC_TEXT = _Italic text_
    CODE_TEXT = `Code Text`
    LINK = "[anchor](url)"
    IMAGES = "![alt text](url)"



class TextNode():

