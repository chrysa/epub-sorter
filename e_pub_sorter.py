import argparse
import csv
import time
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import ebookmeta
from progress.bar import IncrementalBar


CSV_HEADER =  ["is_duplicate","is_failed","path","identifier","title","file","author"]

@dataclass
class Epub:
    csv_exclude_header: list[str] = field(default_factory=list)
    csv_header: list[str] = field(default_factory=list)
    csv_output: Path = Path() / "epub_metadata.csv"
    data: list[dict] = field(default_factory=list)
    duplicate_folder: Path = Path() / "[duplicates]"
    duplicates: list[tuple[Path, str]] = field(default_factory=list)
    epub_list: list[Path] = field(default_factory=list)
    epub_path: Path = Path()
    failed_folder: Path = Path() / "[failed]"
    processed_folder: Path = Path() / "[processed]"
    progress_suffix: str = "[%(index)d/%(max)d] - [%(percent)d%%]"

    def __post_init__(self):
        self.epub_list = []
        self.csv_header = CSV_HEADER
        self.data = []
        self.duplicates = []
        self.identifier_list = []
        self.duplicate_folder.mkdir(parents=True, exist_ok=True)
        self.failed_folder.mkdir(parents=True, exist_ok=True)
        self.processed_folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _find_empty_folders():
        directory_path = Path()
        return [
            folder
            for folder in directory_path.rglob("*")
            if folder.is_dir() and not any(folder.iterdir())
        ]

    def author_group(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Group By Author",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in file_list:
                metadata = ebookmeta.get_metadata(epub.as_posix())
                author_name = (
                    "-".join(metadata.author_list).replace(",", "_").replace(" ", "_")
                )
                author_folder = self.processed_folder / author_name
                if not author_folder.exists():
                    author_folder.mkdir(parents=True, exist_ok=True)
                epub.rename(author_folder / epub.name)
                self.update_data(
                    identifier=metadata.identifier, path=author_folder / epub.name
                )
                bar.next()

    def detect_epubs(self):
        self.epub_list = list(self.epub_path.rglob("*.epub"))
        print(f"{len(self.epub_list):,} epubs founds")

    def extract_metadata(self):
        with IncrementalBar(
            "Extract Metadata",
            max=len(self.epub_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in self.epub_list:
                if epub.is_file() and epub.parent not in [
                    self.duplicate_folder,
                    self.failed_folder,
                    self.processed_folder,
                ]:
                    # print(f"process {epub} ...")
                    is_duplicate: bool = False
                    is_failed: bool = False
                    try:
                        # print(f"|-> extract metadata from {epub} ...")
                        metadata = ebookmeta.get_metadata(epub.as_posix())
                    except:
                        # print(f"|-> FAIL {epub} ...")
                        path = self.failed_folder / epub.name
                        # print(f"|-> move `{epub}` to `{path}`")
                        epub.rename(path)
                        is_failed = True
                    else:
                        self.identifier_list.append(metadata.identifier)
                        is_failed = False
                        path = self.processed_folder / epub.name
                        epub.rename(path)
                    self.data.append(
                        {
                            "is_duplicate": is_duplicate,
                            "is_failed": is_failed,
                            "metadata": metadata,
                            "path": path,
                        }
                    )
                bar.next()

    def find_duplicate_by_identifier(self):
        duplicate_list = []
        with IncrementalBar(
            "Search Duplicates By Identifiers",
            max=len(self.identifier_list),
            suffix=self.progress_suffix,
        ) as bar:
            for identifier in self.identifier_list:
                if self.identifier_list.count(identifier) > 1:
                    duplicate_list.extend(
                        [
                            epub
                            for epub in self.data
                            if epub["metadata"].identifier == identifier
                        ]
                    )
                bar.next()
        if duplicate_list:
            with IncrementalBar(
                "Move Duplicates",
                max=len(duplicate_list),
                suffix=self.progress_suffix,
            ) as bar:
                for duplicate in duplicate_list:
                    duplicate["is_duplicate"] = True
                    path = self.duplicate_folder / duplicate["path"].name
                    # print(f"|-> move `{epub['path']}` to `{path}`")
                    duplicate["path"].rename(path)
                    duplicate["path"] = path
                bar.next()

    def generate_csv(self):
        print("generate csv")
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

    def get_summary(self):
        print(f"{len(list(self.duplicate_folder.rglob('*.epub')))} duplicates")
        print(f"{len(list(self.failed_folder.rglob('*.epub')))} failed")
        print(f"{len(list(self.processed_folder.rglob('*.epub')))} processed")
        print(f"{len(list(self.processed_folder.iterdir()))} authors in processed")

    def rename_file(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Rename File",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in self.processed_folder.rglob("*.epub"):
                metadata = ebookmeta.get_metadata(epub.as_posix())
                epub.rename(
                    self.processed_folder
                    / f"{metadata.title.replace(',','_').replace(' ','_')}.{epub.suffix}"
                )
                bar.next()

    def remove_empty_folder(self):
        empty_folders = self._find_empty_folders()
        with IncrementalBar(
            "Remove Empty Folder",
            max=len(empty_folders),
            suffix=self.progress_suffix,
        ) as bar:
            for folder in sorted(empty_folders, reverse=True):
                folder.rmdir()
                bar.next()

    def update_authors(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Update Author",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in file_list:
                metadata = ebookmeta.get_metadata(epub.as_posix())
                print(f"\n{epub} actual author list")
                for author in metadata.author_list:
                    print(f"\t - {author}")
                change_author = input("change author ? [Y/n] [n] ")
                if change_author in ["y", "Y"]:
                    # TODO: all multiple names
                    name = input("new value: ")
                    metadata.set_author_list_from_string(name)
                    self.update_data(identifier=metadata.identifier, metadata=metadata)
                bar.next()

    def update_data(self, *, identifier, metadata=None, path=None):
        for data in self.data:
            if identifier == data["metadata"].identifier:
                if metadata is not None:
                    ebookmeta.set_metadata(data["path"].as_posix(), metadata)
                    data["metadata"] = metadata
                if path is not None:
                    data["path"] = path

    def update_title(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Update Title",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in file_list:
                metadata = ebookmeta.get_metadata(epub.as_posix())
                print("\n")
                change_title = input(f"change {epub} title ? [Y/n] [n] ")
                if change_title in ["y", "Y"]:
                    title = input("new value: ")
                    metadata.title = title
                    self.update_data(identifier=metadata.identifier, metadata=metadata)
                bar.next()


def main():
    parser = argparse.ArgumentParser(description="Epub Orderer")
    parser.add_argument("--update-all", action="store_true", dest="update")
    parser.add_argument(
        "-a", "--update-author", action="store_true", dest="update_author"
    )
    parser.add_argument("-r", "--rename-file", action="store_true", dest="rename_file")
    parser.add_argument(
        "-t", "--update-title", action="store_true", dest="update_title"
    )
    args = parser.parse_args()

    instance = Epub()
    instance.detect_epubs()
    if instance.epub_list:
        instance.extract_metadata()
        instance.find_duplicate_by_identifier()
        if args.update or args.update_author:
            instance.update_authors()
        if args.update or args.update_title:
            instance.update_title()
        if args.update or args.rename_file:
            instance.rename_file()
        instance.author_group()
        instance.generate_csv()
        instance.remove_empty_folder()
        instance.get_summary()


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"execution time {end - start}")
