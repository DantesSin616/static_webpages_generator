import os
import shutil
import logging
import sys
from src.nodes.textnode import TextNode

logging.basicConfig(level=logging.INFO)


def main():
    # Generate the `public/` directory by copying from `static/`.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    source = os.path.join(repo_root, "static")
    destination = os.path.join(repo_root, "public")

    try:
        logging.info(f"Copying site from {source} to {destination}")
        out = copy_from_source_to_new_destination(source, destination)
        logging.info(f"Site generated at: {out}")
    except Exception:
        logging.exception("Failed to generate public directory")
        sys.exit(1)


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


if __name__ == "__main__":
    main()

