from progress.bar import IncrementalBar

from common import Common


class Cli(Common):
    def __init__(self, args):
        super().__init__(epub_path=args.epub_path)
        self.args = args

    def author_group(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Group By Author",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in file_list:
                metadata = self.get_metadata(epub=epub)
                self.rename_author(epub=epub, metadata=metadata)
                bar.next()

    def extract_metadata(self):
        with IncrementalBar(
            "Extract Metadata",
            max=len(self.epub_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in self.epub_list:
                super().extract_metadata()
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
                        ],
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
                    duplicate["path"].rename(path)
                    duplicate["path"] = path
                bar.next()

        def get_summary(self):
            summary_message = (
                f"{len(list(self.duplicate_folder.rglob('*.epub')))} duplicates\n"
                f"{len(list(self.failed_folder.rglob('*.epub')))} failed\n"
                f"{len(list(self.processed_folder.rglob('*.epub')))} processed\n"
                f"{len(list(self.processed_folder.iterdir()))} authors in processed"
            )
            print(summary_message)

    def rename_file(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Rename File",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in self.processed_folder.rglob("*.epub"):
                self.rename_file(epub=epub)
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
                metadata = self.get_meatadata(epub=epub)
                print(f"\n{epub} actual author list")
                for author in metadata.author_list:
                    print(f"\t - {author}")
                change_author = input("Change author? [Y/n] [n] ")
                if change_author in ["y", "Y"]:
                    name = input("New value: ")
                    metadata.set_author_list_from_string(name)
                    self.update_data(identifier=metadata.identifier, metadata=metadata)
                bar.next()

    def rename_file(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Rename File",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in self.processed_folder.rglob("*.epub"):
                metadata = self.get_metadata(epub=epub.as_posix())
                epub.rename(
                    self.processed_folder
                    / f"{metadata.title.replace(',','_').replace(' ','_')}.{epub.suffix}",
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
                metadata = self.get_metadata(epub=epub.as_posix())
                print(f"\n{epub} actual author list")
                for author in metadata.author_list:
                    print(f"\t - {author}")
                change_author = input("Change author? [Y/n] [n] ")
                if change_author in ["y", "Y"]:
                    name = input("New value: ")
                    metadata.set_author_list_from_string(name)
                    self.update_data(identifier=metadata.identifier, metadata=metadata)
                bar.next()

    def update_title(self):
        file_list = self.get_processed_epub()
        with IncrementalBar(
            "Update Title",
            max=len(file_list),
            suffix=self.progress_suffix,
        ) as bar:
            for epub in file_list:
                metadata = self.get_metadata(epub=epub.as_posix())
                print("\n")
                change_title = input(f"Change {epub} title? [Y/n] [n] ")
                if change_title in ["y", "Y"]:
                    title = input("New value: ")
                    metadata.title = title
                    self.update_data(identifier=metadata.identifier, metadata=metadata)
                bar.next()

    def run(self):
        self.detect_epubs()
        if self.epub_list:
            self.extract_metadata()
        self.find_duplicate_by_identifier()
        if self.args.update or self.args.update_author:
            self.update_authors()
        if self.args.update or self.args.update_title:
            self.update_title()
        if self.args.update or self.args.rename_file:
            self.rename_file()
        self.author_group()
        self.generate_csv()
        self.remove_empty_folder()
        self.get_summary()
