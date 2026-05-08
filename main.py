import argparse
from pathlib import Path

from cli import Cli
from gui import Gui


def main():
    parser = argparse.ArgumentParser(description="Epub Orderer")
    parser.add_argument(
        "--epub-path",
        type=Path,
        help="Path to the epub folder",
        default=Path().cwd(),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default="epub_metadata.csv",
        help="Output CSV file path",
    )
    parser.add_argument(
        "--processed-folder",
        type=Path,
        default="[processed]",
        help="Processed folder path",
    )
    parser.add_argument(
        "--duplicate-folder",
        type=Path,
        default="[duplicates]",
        help="Duplicate folder path",
    )
    parser.add_argument(
        "--skipped-folder",
        type=Path,
        default="[skipped]",
        help="Skipped folder path",
    )
    parser.add_argument(
        "--failed-folder",
        type=Path,
        default="[failed]",
        help="Failed folder path",
    )
    parser.add_argument(
        "--cli", action="store_true", help="Launch cli interface (override --gui)"
    )
    parser.add_argument(
        "--gui", action="store_true", help="Launch GUI interface (default)"
    )
    parser.add_argument("-r", "--rename-file", action="store_true", dest="rename_file")
    parser.add_argument("--update-all", action="store_true", dest="update")
    parser.add_argument(
        "-a",
        "--update-author",
        action="store_true",
        dest="update_author",
    )
    parser.add_argument(
        "-t",
        "--update-title",
        action="store_true",
        dest="update_title",
    )

    args = parser.parse_args()
    if args.cli:
        instance = Cli(args)
    elif args.gui:
        instance = Gui(args)
    instance.run()


if __name__ == "__main__":
    main()
