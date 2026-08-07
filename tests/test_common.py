"""Tests for epub-sorter common module."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING

from common import Common

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def _make_args(mocker: MockerFixture, tmp_path: Path):
    args = mocker.MagicMock()
    args.epub_path = tmp_path
    args.duplicate_folder = str(tmp_path / "duplicates")
    args.failed_folder = str(tmp_path / "failed")
    args.processed_folder = str(tmp_path / "processed")
    args.skipped_folder = str(tmp_path / "skipped")
    return args


def _make_common(mocker: MockerFixture, tmp_path: Path) -> Common:
    """Create a Common instance bypassing __post_init__."""
    args = _make_args(mocker, tmp_path)
    instance = Common.__new__(Common)
    instance.args = args
    instance.epub_path = tmp_path
    instance.epub_list = []
    instance.csv_exclude_header = []
    instance.csv_header = [
        "is_duplicate",
        "is_failed",
        "path",
        "identifier",
        "title",
        "file",
        "author",
    ]
    instance.csv_output = tmp_path / "epub_metadata.csv"
    instance.data = []
    instance.duplicates = []
    instance.identifier_list = []
    instance.progress_suffix = "[%(index)d/%(max)d] - [%(percent)d%%]"
    instance.duplicate_folder = Path(args.duplicate_folder)
    instance.failed_folder = Path(args.failed_folder)
    instance.processed_folder = Path(args.processed_folder)
    instance.skipped_folder = Path(args.skipped_folder)
    return instance


class TestPostInit:
    def test_post_init_sets_folders(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        args = _make_args(mocker, tmp_path)
        instance = Common.__new__(Common)
        instance.args = args
        instance.epub_path = tmp_path
        instance.epub_list = []
        instance.csv_exclude_header = []
        instance.csv_header = []
        instance.csv_output = tmp_path / "out.csv"
        instance.data = []
        instance.duplicates = []
        instance.identifier_list = []
        instance.progress_suffix = ""
        instance.__post_init__()
        assert instance.duplicate_folder == Path(args.duplicate_folder)
        assert instance.failed_folder == Path(args.failed_folder)
        assert instance.processed_folder == Path(args.processed_folder)
        assert instance.skipped_folder == Path(args.skipped_folder)

    def test_post_init_sets_csv_header(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        args = _make_args(mocker, tmp_path)
        instance = Common.__new__(Common)
        instance.args = args
        instance.epub_path = tmp_path
        instance.epub_list = []
        instance.csv_exclude_header = []
        instance.csv_header = []
        instance.csv_output = tmp_path / "out.csv"
        instance.data = []
        instance.duplicates = []
        instance.identifier_list = []
        instance.progress_suffix = ""
        instance.__post_init__()
        assert "is_duplicate" in instance.csv_header
        assert "author" in instance.csv_header


class TestFindEmptyFolders:
    def test_empty_directory_detected(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        mocker.patch("common.Path", return_value=tmp_path)
        result = Common._find_empty_folders()
        assert isinstance(result, list)

    def test_non_empty_folder_excluded(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        non_empty = tmp_path / "non_empty"
        non_empty.mkdir()
        (non_empty / "file.epub").touch()
        mocker.patch("common.Path", return_value=tmp_path)
        result = Common._find_empty_folders()
        assert not any(p.name == "non_empty" for p in result)

    def test_returns_list(self, mocker: MockerFixture, tmp_path: Path) -> None:
        mocker.patch("common.Path", return_value=tmp_path)
        result = Common._find_empty_folders()
        assert isinstance(result, list)


class TestDetectEpubs:
    def test_finds_epub_files(self, mocker: MockerFixture, tmp_path: Path) -> None:
        (tmp_path / "book1.epub").touch()
        (tmp_path / "book2.epub").touch()
        common = _make_common(mocker, tmp_path)
        common.detect_epubs()
        assert len(common.epub_list) == 2

    def test_ignores_non_epub(self, mocker: MockerFixture, tmp_path: Path) -> None:
        (tmp_path / "book1.epub").touch()
        (tmp_path / "readme.txt").touch()
        common = _make_common(mocker, tmp_path)
        common.detect_epubs()
        assert all(p.suffix == ".epub" for p in common.epub_list)

    def test_empty_directory(self, mocker: MockerFixture, tmp_path: Path) -> None:
        common = _make_common(mocker, tmp_path)
        common.detect_epubs()
        assert common.epub_list == []

    def test_recursive_detection(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "nested.epub").touch()
        common = _make_common(mocker, tmp_path)
        common.detect_epubs()
        assert len(common.epub_list) == 1


class TestExtractMetadata:
    def test_failed_epub_moves_to_failed_folder(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        epub = tmp_path / "bad.epub"
        epub.touch()
        mocker.patch(
            "common.ebookmeta.get_metadata", side_effect=Exception("parse error")
        )
        common.extract_metadata(epub=epub)
        assert len(common.data) == 1
        assert common.data[0]["is_failed"] is True

    def test_successful_epub_processed(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        epub = tmp_path / "good.epub"
        epub.touch()
        mock_meta = mocker.MagicMock()
        mock_meta.identifier = "isbn:good"
        mocker.patch("common.ebookmeta.get_metadata", return_value=mock_meta)
        common.extract_metadata(epub=epub)
        assert len(common.data) == 1
        assert common.data[0]["is_failed"] is False
        assert "isbn:good" in common.identifier_list

    def test_skips_epub_in_processed_folder(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        processed = tmp_path / "processed"
        processed.mkdir()
        epub = processed / "already.epub"
        epub.touch()
        common.extract_metadata(epub=epub)
        assert len(common.data) == 0


class TestGenerateCsv:
    def test_csv_created_with_correct_columns(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        mock_meta = mocker.MagicMock()
        mock_meta.author_list_to_string.return_value = "Author"
        mock_meta.file = "file.epub"
        mock_meta.identifier = "isbn:1"
        mock_meta.title = "Title"
        common.data = [
            {
                "is_duplicate": False,
                "is_failed": False,
                "metadata": mock_meta,
                "path": tmp_path / "file.epub",
            },
        ]
        common.generate_csv()
        assert common.csv_output.exists()
        with open(common.csv_output) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["title"] == "Title"

    def test_csv_empty_data(self, mocker: MockerFixture, tmp_path: Path) -> None:
        common = _make_common(mocker, tmp_path)
        common.data = []
        common.generate_csv()
        assert common.csv_output.exists()


class TestGetProcessedEpub:
    def test_returns_epubs_in_processed(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        processed = tmp_path / "processed"
        processed.mkdir()
        (processed / "book.epub").touch()
        common = _make_common(mocker, tmp_path)
        result = common.get_processed_epub()
        assert len(result) == 1

    def test_empty_processed_folder(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        processed = tmp_path / "processed"
        processed.mkdir()
        common = _make_common(mocker, tmp_path)
        result = common.get_processed_epub()
        assert result == []

    def test_processed_folder_not_exist(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        result = common.get_processed_epub()
        assert result == []


class TestUpdateData:
    def test_updates_path_when_found(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        mock_meta = mocker.MagicMock()
        mock_meta.identifier = "isbn:123"
        common.data = [{"metadata": mock_meta, "path": Path("/old")}]
        new_path = Path("/new")
        common.update_data(identifier="isbn:123", path=new_path)
        assert common.data[0]["path"] == new_path

    def test_no_update_when_identifier_not_found(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        mock_meta = mocker.MagicMock()
        mock_meta.identifier = "isbn:123"
        original_path = Path("/old")
        common.data = [{"metadata": mock_meta, "path": original_path}]
        common.update_data(identifier="isbn:999", path=Path("/new"))
        assert common.data[0]["path"] == original_path

    def test_updates_metadata_when_provided(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        mock_meta = mocker.MagicMock()
        mock_meta.identifier = "isbn:123"
        common.data = [{"metadata": mock_meta, "path": tmp_path / "f.epub"}]
        new_meta = mocker.MagicMock()
        new_meta.identifier = "isbn:123"
        mocker.patch("common.ebookmeta.set_metadata")
        common.update_data(identifier="isbn:123", metadata=new_meta)
        assert common.data[0]["metadata"] == new_meta


class TestGetMetadata:
    def test_delegates_to_ebookmeta(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        sentinel = mocker.MagicMock()
        get_meta = mocker.patch(
            "common.ebookmeta.get_metadata", return_value=sentinel
        )
        epub = tmp_path / "book.epub"
        epub.touch()
        result = Common.get_metadata(epub=epub)
        assert result is sentinel
        get_meta.assert_called_once_with(epub.as_posix())


class TestRenameAuthor:
    def test_moves_epub_into_author_folder(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        common.args.processed_folder = tmp_path / "processed"
        epub = tmp_path / "book.epub"
        epub.touch()
        metadata = mocker.MagicMock()
        metadata.author_list = ["Jane Doe"]
        metadata.identifier = "isbn:1"
        mocker.patch.object(common, "update_data")
        common.rename_author(epub=epub, metadata=metadata)
        author_folder = tmp_path / "processed" / "Jane_Doe"
        assert (author_folder / "book.epub").exists()
        assert not epub.exists()


class TestRenameFile:
    def test_renames_into_processed_when_no_collision(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        epub = tmp_path / "raw.epub"
        epub.touch()
        metadata = mocker.MagicMock()
        metadata.title = "My Book"
        mocker.patch("common.ebookmeta.get_metadata", return_value=metadata)
        common.rename_file(epub=epub)
        assert (common.processed_folder / "My_Book..epub").exists()

    def test_moves_to_skipped_on_title_collision(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        common = _make_common(mocker, tmp_path)
        common.processed_folder.mkdir(parents=True, exist_ok=True)
        (common.processed_folder / "My_Book..epub").touch()
        epub = tmp_path / "raw.epub"
        epub.touch()
        metadata = mocker.MagicMock()
        metadata.title = "My Book"
        mocker.patch("common.ebookmeta.get_metadata", return_value=metadata)
        common.rename_file(epub=epub)
        assert (common.skipped_folder / "My_Book..epub").exists()
        assert not epub.exists()


class TestProgressSuffix:
    def test_default_suffix(self, mocker: MockerFixture, tmp_path: Path) -> None:
        common = _make_common(mocker, tmp_path)
        assert "%" in common.progress_suffix
