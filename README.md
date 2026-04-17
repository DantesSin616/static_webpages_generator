# static_webpages_generator

A simple static webpage generator built in Python. This project converts markdown content into a structured static website.

## Features

- **Markdown to HTML**: Converts markdown files (`.md`) into full HTML pages.
- **Recursive Generation**: Crawls the `content/` directory and preserves the directory structure in the output.
- **Template System**: Uses a base HTML template (`src/template.html`) for consistent page design.
- **Automatic Asset Copying**: Copies all static files (CSS, images, etc.) from `static/` to `public/`.
- **Robust Text Processing**: Handles bold, italic (both `*` and `_`), code blocks, links, and images.

## Usage

### Prerequisites
- Python 3.10 or higher.

### Generating the Site
To generate the static site, run the provided shell script from the repository root:

```bash
./main.sh
```

This script will:
1.  Clean the `public/` directory.
2.  Copy all static assets from `static/` to `public/`.
3.  Recursively crawl the `content/` directory and convert all `.md` files into `.html` files using the template at `src/template.html`.
4.  Write the generated HTML files to `public/` while maintaining the original directory structure.

### Running Tests

To run the project's unit tests:

```bash
./test.sh
```

## Project Structure

- `src/main.py`: The entry point for the site generator.
- `src/nodes/`: Contains the `HTMLNode` and `TextNode` classes for processing markdown and HTML.
- `src/utils/`: Helper functions for parsing markdown and converting it to HTML.
- `content/`: Place your markdown files here for page generation.
- `static/`: Place your images, CSS, and other static assets here.
- `public/`: The output directory for the generated static site.

## Implementation Details

### Recursive Page Generation
The generator uses `generate_pages_recursive(dir_path_content, template_path, dest_dir_path)` to walk through the `content/` directory. For every `.md` file found, it:
1.  Extracts the title (the first H1 header found in the file).
2.  Converts the markdown content into HTML using `markdown_to_html_node`.
3.  Injects the title and content into the `src/template.html` placeholders (`{{ Title }}` and `{{ Content }}`).
4.  Saves the resulting HTML file in the corresponding location within the `public/` directory.

### Asset Copying
The `copy_from_source_to_new_destination` function ensures that the `public/` directory is a fresh copy of `static/` before any pages are generated, preventing old assets from lingering.

## Developer Notes

- **.gitignore**: The `public/` directory is ignored by git to keep the repository clean of generated artifacts.
- **Safety**: The generator removes the existing `public/` directory before starting. Do not store unique files in `public/`.
