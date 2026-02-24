from textnode import TextNode

def main():
    new_node = TextNode(
        "this is some anchor text",
        "link",
        "https://www.boot.dev"
    )
    print(new_node)

main()
