import csv
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

import ebookmeta


@dataclass
class Common:
    epub_path: Path
    epub_list: list[Path] = field(default_factory=list)
    csv_exclude_header: list[str] = field(default_factory=list)
    csv_header: list[str] = field(default_factory=list)
    csv_output: Path = Path() / "epub_metadata.csv"
    data: list[dict] = field(default_factory=list)
    duplicates: list[tuple[Path, str]] = field(default_factory=list)
    identifier_list: list[str] = field(default_factory=list)
    progress_suffix: str = "[%(index)d/%(max)d] - [%(percent)d%%]"

    def __post_init__(self):
        self.csv_header = [
            "is_duplicate",
            "is_failed",
            "path",
            "identifier",
            "title",
            "file",
            "author",
        ]
        self.data = []
        self.duplicates = []
        self.identifier_list = []
        self.duplicate_folder: Path = Path() / self.args.duplicate_folder
        self.failed_folder: Path = Path() /  self.args.failed_folder
        self.processed_folder: Path = Path() /  self.args.processed_folder
        self.skipped_folder: Path = Path() /  self.args.skipped_folder

    @staticmethod
    def _find_empty_folders():
        directory_path = Path()
        return [
            folder
            for folder in directory_path.rglob("*")
            if folder.is_dir() and not any(folder.iterdir())
        ]

    @staticmethod
    def get_metadata(*, epub):
        return ebookmeta.get_metadata(epub.as_posix())

    def detect_epubs(self):
        self.epub_list = list(self.epub_path.rglob("*.epub"))
        # print(f"{len(self.epub_list):,} epubs founds")

    def extract_metadata(self,*,epub):
        if epub.is_file() and epub.parent not in [
            self.duplicate_folder,
            self.failed_folder,
            self.processed_folder,
        ]:
            is_duplicate: bool = False
            is_failed: bool = False
            try:
                metadata = ebookmeta.get_metadata(epub.as_posix())
            except:
                path = self.failed_folder / epub.name
                self.failed_folder.mkdir(parents=True, exist_ok=True)
                epub.rename(path)
                is_failed = True
            else:
                self.identifier_list.append(metadata.identifier)
                is_failed = False
                self.processed_folder.mkdir(parents=True, exist_ok=True)
                path = self.processed_folder / epub.name
                epub.rename(path)
            self.data.append(
                {
                    "is_duplicate": is_duplicate,
                    "is_failed": is_failed,
                    "metadata": metadata,
                    "path": path,
                },
            )

    def generate_csv(self):
        # print("Generating CSV")
        content = []
        for data in self.data:
            row = {
                "author": data["metadata"].author_list_to_string(),
                "file": data["metadata"].file,
                "identifier": data["metadata"].identifier,
                "is_duplicate": data["is_duplicate"],
                "is_failed": data["is_failed"],
                "path": data["path"],
                "title": data["metadata"].title,
            }
            content.append(row)
        with open(self.csv_output, "w", encoding="UTF8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(self.csv_header))
            writer.writeheader()
            writer.writerows(content)

    def get_processed_epub(self):
        return list(self.processed_folder.rglob("*.epub"))

    def rename_author(self, *, epub, metadata):
        author_name = "-".join(metadata.author_list).replace(",", "_").replace(" ", "_")
        author_folder = self.args.processed_folder / author_name
        if not author_folder.exists():
            author_folder.mkdir(parents=True, exist_ok=True)
        epub.rename(author_folder / epub.name)
        self.update_data(identifier=metadata.identifier, path=author_folder / epub.name)

    def rename_file(self,*, epub):
        metadata = ebookmeta.get_metadata(epub.as_posix())
        if (self.processed_folder / f"{metadata.title.replace(',','_').replace(' ','_')}.{epub.suffix}").exists():
            self.processed_skipped.mkdir(parents=True, exist_ok=True)
            epub.rename(
                self.processed_skipped / f"{metadata.title.replace(',','_').replace(' ','_')}.{epub.suffix}",
            )
        else:
            self.processed_folder.mkdir(parents=True, exist_ok=True)
            epub.rename(
                self.processed_folder
                / f"{metadata.title.replace(',','_').replace(' ','_')}.{epub.suffix}",
            )

    def update_data(self, *, identifier, metadata=None, path=None):
        for data in self.data:
            if identifier == data["metadata"].identifier:
                if metadata is not None:
                    ebookmeta.set_metadata(data["path"].as_posix(), metadata)
                    data["metadata"] = metadata
                if path is not None:
                    data["path"] = path
