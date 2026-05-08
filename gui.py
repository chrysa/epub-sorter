import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from common import Common


class Gui(Common):
    def __init__(self, args):
        self.args = args
        super().__init__(epub_path=args.epub_path)
        self.root = tk.Tk()
        self.root.title("Epub Orderer")
        self.root.geometry("800x400")
        self.root.resizable(0, 0)
        self.rename_file_var = tk.IntVar(value=1 if args.rename_file else 0)
        self.update_var = tk.IntVar(value=1 if args.update else 0)
        self.update_author_var = tk.IntVar(value=1 if args.update_author else 0)
        self.update_title_var = tk.IntVar(value=1 if args.update_title else 0)
        self.current_step = tk.StringVar(value="")
        self.files_processed = tk.StringVar(value="")
        self.files_processed_count = tk.IntVar(value=0)
        self.create_widgets()

    def create_widgets(self):
        self.epub_path_input = tk.Label(self.root, text="Epub Path:").grid(
            row=0, column=0, sticky="w"
        )
        tk.Entry(
            self.root,
            textvariable=tk.StringVar(value=str(self.args.epub_path)),
            width=50,
        ).grid(row=0, column=1, columnspan=2)
        tk.Button(self.root, text="Browse", command=self.browse_epub_path).grid(
            row=0,
            column=3,
        )
        tk.Label(self.root, text="Output CSV:").grid(row=1, column=0, sticky="w")
        tk.Entry(
            self.root,
            textvariable=tk.StringVar(value=str(self.args.output_csv)),
            width=50,
        ).grid(row=1, column=1, columnspan=2)
        tk.Label(self.root, text="Processed Folder:").grid(row=2, column=0, sticky="w")
        tk.Entry(
            self.root,
            textvariable=tk.StringVar(value=str(self.args.processed_folder)),
            width=50,
        ).grid(row=2, column=1, columnspan=2)

        tk.Label(self.root, text="Duplicate Folder:").grid(row=3, column=0, sticky="w")
        tk.Entry(
            self.root,
            textvariable=tk.StringVar(value=str(self.args.duplicate_folder)),
            width=50,
        ).grid(row=3, column=1, columnspan=2)
        tk.Label(self.root, text="Failed Folder:").grid(row=4, column=0, sticky="w")
        tk.Entry(
            self.root,
            textvariable=tk.StringVar(value=str(self.args.failed_folder)),
            width=50,
        ).grid(row=4, column=1, columnspan=2)

        tk.Label(self.root, text="Skipped Folder:").grid(row=5, column=0, sticky="w")
        tk.Entry(
            self.root,
            textvariable=tk.StringVar(value=str(self.args.skipped_folder)),
            width=50,
        ).grid(row=5, column=1, columnspan=2)
        tk.Checkbutton(
            self.root,
            text="Rename Files",
            variable=self.rename_file_var,
        ).grid(row=6, column=0, sticky="w")
        tk.Checkbutton(
            self.root,
            text="Update All Metadata",
            variable=self.update_var,
        ).grid(row=6, column=1, sticky="w")
        tk.Checkbutton(
            self.root,
            text="Update Author Metadata",
            variable=self.update_author_var,
        ).grid(row=6, column=2, sticky="w")
        # tk.Checkbutton(self.root, text="Update Title Metadata", variable=self.update_title_var).grid(row=6, column=3, sticky="w")
        tk.Label(self.root, text="Files Processed:").grid(row=7, column=0, sticky="w")
        tk.Label(self.root, textvariable=self.files_processed).grid(
            row=7,
            column=1,
            columnspan=3,
            sticky="w",
        )
        self.total_files_label = tk.Label(self.root, text="Total Files: 0")
        self.total_files_label.grid(row=8, column=0, sticky="w")
        self.current_file_index_label = tk.Label(
            self.root,
            text="Current File Index: 0",
        )
        self.current_file_index_label.grid(row=8, column=1, columnspan=3, sticky="w")

        self.current_step_label = tk.Label(self.root, textvariable=self.current_step)
        self.current_step_label.grid(row=9, column=0, columnspan=4, pady=5)

        self.progress_bar = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=400,
            mode="determinate",
        )
        self.progress_bar.grid(row=10, column=0, columnspan=4, pady=10)

        tk.Button(self.root, text="Run Processing", command=self.run_processing).grid(
            row=11,
            column=1,
            columnspan=2,
        )

    def browse_epub_path(self):
        if folder_selected := filedialog.askdirectory():
            self.epub_path_inputself.epub_path_inputself.epub_path_input.set(
                folder_selected
            )

    def find_duplicate_by_identifier(self):
        duplicate_list = []
        index = 0
        for identifier in self.identifier_list:
            self.current_step.set("find duplicate for {identifier}")
            if self.identifier_list.count(identifier) > 1:
                duplicate_list.extend(
                    [
                        epub
                        for epub in self.data
                        if epub["metadata"].identifier == identifier
                    ],
                )
            if duplicate_list:
                for duplicate in duplicate_list:
                    duplicate["is_duplicate"] = True
                    path = self.duplicate_folder / duplicate["path"].name
                    self.duplicate_folder.mkdir(parents=True, exist_ok=True)
                    duplicate["path"].rename(path)
                    duplicate["path"] = path
            self.update_progress(index=index, total_files=len(self.identifier_list))

    def remove_empty_folders(self):
        empty_folders = self._find_empty_folders()
        for folder in sorted(empty_folders, reverse=True):
            folder.rmdir()

    def run_processing(self):
        self.current_step.set("detect epubs")
        self.detect_epubs()
        total_files = len(self.epub_list)
        self.total_files_label.config(text=f"Total Files: {total_files}")
        self.progress_bar["maximum"] = total_files
        if self.epub_list:
            self.progress_bar.start()
            for index, epub in enumerate(self.epub_list):
                self.current_step.set("extract metadata")
                self.extract_metadata(epub=epub)
                self.update_progress(index=index, total_files=total_files)
            self.find_duplicate_by_identifier()
            index = 0
            if self.update_var.get() or self.rename_file_var.get():
                for epub in self.processed_folder.rglob("*.epub"):
                    self.current_step.set("rename")
                    self.rename_file(epub=epub)
                self.update_progress(index=index, total_files=total_files)
            self.generate_csv()
            self.remove_empty_folders()
            self.files_processed.set("Processed {len(self.epub_list)} files")
            self.files_processed_count.set(len(self.epub_list))
            self.progress_bar.stop()
            if self.update_var.get() or self.update_author_var.get():
                self.current_step.set("group by author")
                file_list = self.get_processed_epub()
                for epub in file_list:
                    self.group_author(epub=epub)

            messagebox.showinfo("Processing Complete", "EPUB processing is complete.")
        else:
            messagebox.showwarning(
                "No EPUBs Found",
                "No EPUB files were found in the specified path.",
            )

    def update_progress(self, index, total_files):
        self.current_file_index_label.config(
            text=f"Current File Index: {index + 1} / {total_files}",
        )
        self.progress_bar["value"] = index + 1
        self.root.update_idletasks()

    def run(self):
        self.root.mainloop()
