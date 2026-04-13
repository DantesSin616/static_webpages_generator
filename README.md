# static_webpages_generator

A simple static webpage generator built in Python. This project converts structured text content into HTML markup.

## Features

- TextNode class for representing text with types (bold, italic, code, links, images)
- HtmlNode classes (LeafNode, ParentNode) for generating HTML elements
- Conversion functions to transform text nodes to HTML
- Unit tests for validation

## Usage

Run the main script:
```
./main.sh
```

Run tests:
```
./test.sh
```

## Generate public/

The project can generate a `public/` directory by copying the contents of
the `static/` directory. Important notes and safety guidelines:

- **What it does:** `src/main.py` will recursively copy everything from
	`static/` into `public/` and overwrite/clear any existing contents in
	`public/` before copying.
- **Preconditions:** Make sure `static/` exists and contains the files you
	want to publish. Do **not** place important data inside `public/` because
	its contents will be removed when the generator runs.
- **How to run:**

	```bash
	./main.sh      # executes python3 src/main.py
	# or
	python3 src/main.py
	```

- **Safety warning:** Running the generator deletes the existing contents
	of `public/`. If `public/` contains anything you care about, back it up
	first.
- **Logging:** The script logs copied paths and errors to stdout/stderr.
- **Why no unit test for this:** File-system integration tests are useful
	but optional here — manual checks are sufficient. If you later want an
	automated integration test, use pytest with `tmp_path` to create temporary
	source/destination directories.

If you want, I can add a short integration test scaffold using `tmp_path`.

## Implementation details & developer notes

- **Copy function**: `copy_from_source_to_new_destination(source, destination)` — recursively copies `source` → `destination`.
	- Clears `destination` contents before copying.
	- Copies files with metadata preserved (`shutil.copy2`).
	- Recurses into subdirectories using the same function (no `shutil.copytree`).
	- Recreates symbolic links using `os.symlink`.
	- Returns the absolute `destination` path on success.
	- Raises `FileNotFoundError` if `source` doesn't exist and `ValueError` if `source`/`destination` are nested (to avoid infinite recursion).

- **Main entrypoint**: running `./main.sh` or `python3 src/main.py` will call the above function and generate `public/` from `static/`.

- **.gitignore**: `public/` is already added to `.gitignore` so generated output won't be committed.

- **Logging & troubleshooting**:
	- The script logs copied paths and errors to stdout/stderr. If you see permission errors, check file ownership and write permissions for `public/` and its parent.
	- If generation fails with a `ValueError` complaining about nested paths, ensure `static/` and `public/` are not nested inside one another (this is a protective check).

- **Why no unit test for filesystem copy**: filesystem operations are integration-level work — we recommend manual verification, or a small pytest integration using `tmp_path` if you later want CI coverage.

## Quick verification steps (manual)

1. Create a small `static/` sample:

```bash
mkdir -p static/css static/images
echo "body{}" > static/css/style.css
echo "hello" > static/index.html
```

2. Run the generator:

```bash
./main.sh
```

3. Confirm results:

```bash
ls -R public
cat public/index.html
```

4. If anything unexpected happens, back up `public/`, fix `static/`, and re-run.