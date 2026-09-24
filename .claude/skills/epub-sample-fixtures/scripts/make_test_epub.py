"""Generate a minimal EPUB file with controlled metadata, for tests.

Uses only the stdlib (zipfile) — no dependency on ebookmeta to *write* files,
only to read them (as the app under test does).
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

CONTAINER_XML = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

OPF_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{title}</dc:title>
    {author_tag}
    {identifier_tag}
  </metadata>
  <manifest/>
  <spine/>
</package>
"""


def build_epub(
    out_path: Path,
    title: str,
    author: str | None,
    identifier: str | None,
) -> None:
    """Write a minimal EPUB zip with the given metadata to out_path."""
    author_tag = f"<dc:creator>{author}</dc:creator>" if author else ""
    identifier_tag = f'<dc:identifier id="bookid">{identifier}</dc:identifier>' if identifier else ""
    opf = OPF_TEMPLATE.format(title=title, author_tag=author_tag, identifier_tag=identifier_tag)

    with zipfile.ZipFile(out_path, "w") as epub:
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        epub.writestr("META-INF/container.xml", CONTAINER_XML)
        epub.writestr("content.opf", opf)


def main() -> None:
    """Parse CLI args and generate the sample EPUB."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--title", default="Sample Book")
    parser.add_argument("--author", default=None)
    parser.add_argument("--identifier", default=None)
    args = parser.parse_args()
    build_epub(args.out, args.title, args.author, args.identifier)


if __name__ == "__main__":
    main()
