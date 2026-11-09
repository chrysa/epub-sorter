# epub-sorter — Design contract

> Contract for the two front-ends over the shared engine: a Tkinter desktop window (default)
> and an interactive terminal mode (`--cli`). Rule:
> [standards/rules/design.md](standards/rules/design.md); method and acceptance criteria:
> the shared-standards *DESIGN-CONTRACT* guide. Read it before changing a window, a prompt or
> the wording; update it in the same change.
>
> Status: **[implemented]** links the code · **[decided]** names the decision · **[proposed]**
> is not agreed. This file documents the current surfaces; it does not redesign them.

## 1. Surface and status

- **Surfaces:** native desktop window built with the standard-library `tkinter`
  ([gui.py](gui.py)), and an interactive CLI with progress bars and yes/no prompts
  ([cli.py](cli.py)). Both are selected in [main.py](main.py) and share [common.py](common.py).
  **[implemented]**
- **Lifecycle:** shipped as version `0.1.0`, personal tool; a one-file executable can be built
  with PyInstaller ([build.ps1](build.ps1)). [README.md](README.md),
  [ARCHITECTURE.md](ARCHITECTURE.md).
- **Detailed specs:** none.

## 2. Users, devices and priority tasks

| User | Context and device | Priority tasks |
| ---- | ------------------ | -------------- |
| Owner of an EPUB library | Desktop (Windows build script; Linux/macOS with Tk), occasional bulk runs on one folder | 1. choose the library folder · 2. run the sort (duplicates, rename, group by author) · 3. know what happened to each file |

Primary action: **Run Processing** in the window; in the CLI, the command line itself.

## 3. Journeys and navigation

- **J1 — Sort a library (GUI):** start `python main.py --epub-path <folder>` → window shows the
  path, output CSV and four output folders, three option checkboxes → **Run Processing** →
  step label, file index and progress bar update → "Processing Complete" dialog.
  **[implemented]** Failure: no EPUB found → warning dialog. **[implemented]**
- **J2 — Sort with prompts (CLI):** `python main.py --cli …` → one progress bar per phase →
  with `--update-author` / `--update-title`, a prompt per book → summary printed at the end.
  **[implemented]**
- **J3 — Pick another folder in the window:** **Browse** fills the path field, but processing
  still uses the `--epub-path` argument (see §11). **[known gap]**
- **Information architecture:** one fixed window, a single grid of labelled rows; no menus or
  tabs. Output folders are created relative to the working directory. **[implemented]**
- **Density:** compact form; fits a one-shot batch tool.

## 4. Identity

No identity of its own: native Tk widgets with the platform's default look, window title
"Epub Orderer". **[implemented]** Keep the host look; no palette, logo or custom font.

## 5. Tokens and components (owned elsewhere)

| Concern | Source of truth | Rules of use |
| ------- | --------------- | ------------ |
| Colours, fonts | the platform Tk theme | do not set literal colours or fonts |
| Window size | `geometry("800x400")`, `resizable(0, 0)` in [gui.py](gui.py) | fixed today, see §11 |
| Components | `tk.Label`, `tk.Entry`, `tk.Button`, `tk.Checkbutton`, `ttk.Progressbar`, `messagebox`, `filedialog` | prefer `ttk` widgets for the native theme |
| CLI progress format | `progress_suffix` in [common.py](common.py), `IncrementalBar` in [cli.py](cli.py) | `[index/max] - [percent%]` |

- **Shared contract:** not applicable (no web content).
- **Design debt and drift:** the window title "Epub Orderer" differs from the product name; an
  *Update Title Metadata* checkbox is commented out although `--update-title` exists.

## 6. Interaction and states

- **Action feedback:** step text, file index and progress bar during the run; a dialog at the
  end. **[implemented]** The run executes on the UI thread, so the window does not respond until
  it ends and cannot be cancelled. **[known gap]**
- **Forms:** six text fields; only the path field is wired to a variable that **Browse** updates.
  The CSV and folder fields are bound to throwaway variables and edits are ignored.
  **[known gap]**
- **Data states:**

  | State | Where it appears | Behaviour |
  | ----- | ---------------- | --------- |
  | Loading / progress | progress bar, step label | determinate bar per file **[implemented]** |
  | Empty | dialog | "No EPUB files were found in the specified path." **[implemented]** |
  | Error | — | failed files go to `[failed]`; no per-file message in the window **[known gap]** |
  | Offline, stale, reconnect | — | not applicable (local files) |

- **Destructive actions:** files are moved and renamed immediately, without a preview or a
  confirmation in the GUI. **[known gap]**
- **Motion:** none beyond the progress bar.

## 7. Responsive and support conventions

Native desktop window at a fixed 800 × 400 px; large system font scaling or high DPI may clip
rows because the window cannot be resized. Follow Tk/OS conventions (native dialogs for folders
and messages); no browser layout. CLI output assumes an interactive terminal.

## 8. Accessibility

- **Target:** the platform accessibility API through Tk; no web criteria. Tk exposes little to
  screen readers on most platforms — no screen-reader pass was run.
- **Keyboard:** Tk default traversal only — Tab follows creation order, Space activates a
  focused button; no shortcut and no default button (Enter does not run). Not verified by hand.
- **Perception:** no colour carries meaning. CLI prompts read `[Y/n] [n]`, which suggests *yes*
  as the default while the default is *no* **[known gap]**.

## 9. Assets

None: no icon, font or image is shipped; the PyInstaller build sets no icon. Code licence: MIT
([LICENSE](LICENSE)).

## 10. Acceptance criteria and evidence

- **Criteria:** the folder chosen in the window is the one processed; every text field is
  honoured or removed; the window stays responsive with a visible way to stop; moved, skipped,
  duplicate and failed counts are shown at the end; prompts state their real default.
- **Tests:** [tests/test_common.py](tests/test_common.py) covers the engine only; `gui.py`,
  `cli.py` and `main.py` are excluded from coverage ([ARCHITECTURE.md](ARCHITECTURE.md)).
- **Evidence log:**

  | Date | Change | Checks run (tool, sizes, modes) | Result | Not run, and why |
  | ---- | ------ | ------------------------------- | ------ | ---------------- |
  | 2026-11-08 | contract written from the code | source review | gaps listed in §11 | no window run: documentation-only change |

## 11. Open choices, known gaps and maintenance

- **Known gaps:** **Browse** and the path field do not change the processed folder (the engine
  keeps `args.epub_path`); CSV and folder fields are ignored; work runs on the UI thread with no
  cancel; no preview or confirmation before moves; no per-file error report; fixed window size;
  misleading `[Y/n] [n]` prompts; no UI test.
- **Open choices:** **[proposed]** read the field values at **Run Processing** and run the work
  in a thread with `after()` updates; **[proposed]** a dry-run summary before moving files.
- **Maintenance:** the maintainer updates this file with any change to `gui.py`, `cli.py` or the
  options in `main.py`.
