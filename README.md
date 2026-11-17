# TextAllFiles
*A small, dependency-free Python 3 script that converts any file into a printable base64.txt file and back again. It works interactively (with native file dialogs on macOS/Windows/Linux where Tkinter is available) or from the command line.*


## What it does

### Encoding: any file to base64 text

Takes any binary or text file (photo, PDF, zip, executable, …) and writes a plain-ASCII \*.txt file containing its base64 representation.

- Output is wrapped at 76 characters per line (the classic MIME width, so it prints cleanly on paper).
- The data is streamed in chunks (768 KB at a time, a multiple of 3 bytes), so large files won't blow up memory.
- Default output name: original-name+extension.base64.txt (e.g. photo.png -> photo.png.base64.txt).
- The original filename is preserved in the output name, so you can tell what it came from.

Example:

```
photo.png  ->  photo.png.base64.txt
```

### Decoding — base64 text to original file

Takes a base64 .txt file and writes back the original binary file.

- Tolerant of any line wrapping or whitespace: newlines, spaces, tabs, form feeds, CRLF/LF, etc. are all stripped before decoding.
- Tolerates missing padding: if the = padding characters were lost, they're added back automatically.
- Rejects invalid base64 with a clear error message (Not valid base64: …).
- Default output name: if the input ends in .base64.txt, that suffix is stripped (photo.png.base64.txt -> photo.png). Otherwise the extension is replaced with .decoded.

Example:

```
photo.png.base64.txt  →  photo.png
```

---

## Usage

Simple:

1. Install Python from python.org
2. Run it with IDLE.

### Interactive menu (no arguments)

```bash
python3 b64tool.py
```

```
Base64 file tool
  1) Any file  ->  base64 .txt
  2) base64 .txt  ->  original/any binary file
Choose 1 or 2:
```

- **Choosing a file:** a native "Open" dialog appears if Tkinter is available. Otherwise you're prompted in the terminal. You can type a path or drag-and-drop a file into the Terminal window (quotes and backslash-escaped spaces are handled).
- **Saving a file:** a native "Save as" dialog appears if Tkinter is available; otherwise you're prompted in the terminal with a suggested default. You can change the name, and you're asked before overwriting an existing file.
- Pressing **Cancel** in a dialog, or entering nothing, cancels cleanly.

### Command line

```bash
# Encode
python3 b64tool.py encode <file> [out.base64.txt]

# Decode
python3 b64tool.py decode <file.base64.txt> [output_file]
```

- The output argument is **optional**; the sensible default is used if omitted.
- If the output file **already exists**, you're asked Overwrite? [y/N] before it's replaced.
- `e` and `d` work as short aliases for encode and decode.
- Running with no recognized command prints the built-in help text.

Examples:

```bash
python3 b64tool.py encode photo.png
python3 b64tool.py encode photo.png my_photo.txt
python3 b64tool.py decode photo.png.base64.txt
python3 b64tool.py decode photo.png.base64.txt restored.png
```

---

## Requirements

- **Python 3** (standard library only).
- Optional: **Tkinter** for native file dialogs. If it's missing or there's no GUI (e.g. over SSH), the script automatically falls back to terminal prompts.

---

## Notes & behavior details

- **Output encoding** is pure ASCII with Unix (`\n`) line endings, so the `.txt` file is portable and safe to email, paste into documents, or print.
- **Nothing is ever silently overwritten** in interactive mode or on the command line — you're always asked first (the native save dialog may also ask, e.g. on macOS).
- The tool is **streaming on encode** but reads the whole input file into memory on decode (base64 text is small, and this makes the whitespace/padding tolerance simple).
- File sizes are reported after each operation, e.g. Done: photo.png.base64.txt  (1,234,567 bytes).
- The default suffix -.base64.txt is used both for suggesting output names and for recognizing inputs when guessing the decoded filename.

---

## Quick reference

| Action | Command | Default output |
|---|---|---|
| Encode a file | `python3 b64tool.py encode <file>` | `<file>.base64.txt` |
| Decode a file | `python3 b64tool.py decode <file>.base64.txt` | `<file>` (suffix stripped) |
| Interactive | `python3 b64tool.py` | prompted |

---

## License

MIT
