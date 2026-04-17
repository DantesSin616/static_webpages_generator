import os
import shutil
import logging
import sys
from src.nodes.textnode import TextNode
from src.utils.markdown_html import markdown_to_html_node

logging.basicConfig(level=logging.INFO)


def main():
    # Generate the `public/` directory by copying from `static/`.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    static_dir = os.path.join(repo_root, "static")
    content_dir = os.path.join(repo_root, "content")
    template_path = os.path.join(repo_root, "src/template.html")
    public_dir = os.path.join(repo_root, "public")

    try:
        logging.info(f"Copying site from {static_dir} to {public_dir}")
        copy_from_source_to_new_destination(static_dir, public_dir)

        if os.path.exists(content_dir):
            logging.info(f"Generating pages from {content_dir} to {public_dir}")
            generate_pages_recursive(content_dir, template_path, public_dir)
        else:
            logging.warning(f"Content directory {content_dir} not found; skipping page generation.")

        logging.info(f"Site generated at: {public_dir}")
    except Exception:
        logging.exception("Failed to generate public directory")
        sys.exit(1)


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    if not os.path.exists(from_path):
        raise FileNotFoundError(f"Source markdown file not found: {from_path}")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    with open(from_path, "r") as f:
        md_content = f.read()

    with open(template_path, "r") as f:
        template = f.read()

    html_node = markdown_to_html_node(md_content)
    content_html = html_node.to_html()

    title = extract_title(md_content)
    final_html = template.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", content_html)

    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(final_html)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for name in os.listdir(dir_path_content):
        path = os.path.join(dir_path_content, name)
        if os.path.isfile(path):
            if name.endswith(".md"):
                # replace .md with .html
                dest_path = os.path.join(dest_dir_path, name[:-3] + ".html")
                generate_page(path, template_path, dest_path)
        else:
            new_dest_dir = os.path.join(dest_dir_path, name)
            generate_pages_recursive(path, template_path, new_dest_dir)


def copy_from_source_to_new_destination(source, destination):

    """Recursively copy contents from `source` to `destination`.

    Behavior:
    - If `destination` exists, its contents are removed first to ensure
      a clean copy.
    - All files and subdirectories are copied recursively.
    - Symbolic links are recreated as links.
    - Uses recursion via this same function for subdirectories.

    Raises ValueError if `source` is inside `destination` or vice versa
    to avoid infinite recursion / accidental removal of the source.
    """

    src = os.path.abspath(source)
    dst = os.path.abspath(destination)

    # Prevent pathological cases that could cause infinite recursion or
    # accidental deletion of the source while cleaning the destination.
    if os.path.commonpath([src, dst]) == src:
        raise ValueError("destination directory is inside source; aborting to avoid recursion")
    if os.path.commonpath([src, dst]) == dst:
        raise ValueError("source directory is inside destination; aborting to avoid recursion")

    if not os.path.exists(src):
        raise FileNotFoundError(f"source not found: {src}")

    # Ensure destination exists and is empty
    if os.path.exists(dst):
        failures = []
        for name in os.listdir(dst):
            path = os.path.join(dst, name)
            try:
                if os.path.islink(path) or os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception as e:
                logging.exception(f"Failed to remove {path}: {e}")
                failures.append((path, str(e)))

        if failures:
            # Summarize and raise a single error so caller can handle it.
            summary_lines = [f"{p}: {err}" for p, err in failures]
            summary = "; ".join(summary_lines)
            raise RuntimeError(f"Failed to clean destination directory {dst}: {summary}")
    else:
        os.makedirs(dst, exist_ok=True)

    # Copy entries from source to destination
    copy_failures = []
    for name in os.listdir(src):
        s = os.path.join(src, name)
        d = os.path.join(dst, name)

        # If s is a directory, recurse
        if os.path.isdir(s) and not os.path.islink(s):
            os.makedirs(d, exist_ok=True)
            try:
                copy_from_source_to_new_destination(s, d)
            except Exception as e:
                logging.exception(f"Failed to copy directory {s} -> {d}: {e}")
                copy_failures.append((s, d, str(e)))

        # If s is a symlink, recreate the symlink at destination
        elif os.path.islink(s):
            target = os.readlink(s)
            try:
                os.symlink(target, d)
                logging.info(f"symlinked {s} -> {d}")
            except Exception as e:
                logging.exception(f"Failed to create symlink {d} -> {target}: {e}")
                copy_failures.append((s, d, str(e)))

        # Otherwise it's a file: copy metadata-preserving
        else:
            try:
                shutil.copy2(s, d)
                logging.info(f"copied {s} -> {d}")
            except Exception as e:
                logging.exception(f"Failed to copy file {s} -> {d}: {e}")
                copy_failures.append((s, d, str(e)))

    if copy_failures:
        summary_lines = [f"{s} -> {d}: {err}" for s, d, err in copy_failures]
        summary = "; ".join(summary_lines)
        raise RuntimeError(f"One or more copy operations failed: {summary}")

    return dst


def extract_title(markdown):
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("No H1 header found in markdown")


if __name__ == "__main__":
    main()

