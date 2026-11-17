#!/usr/bin/env python3
"""
b64tool.py - convert any file to a printable base64 .txt file and back.

Usage:
    python3 b64tool.py                      # interactive menu
    python3 b64tool.py encode  <file>  [out.base64.txt]
    python3 b64tool.py decode  <file.base64.txt>  [output_file]

Encoding:  photo.png  ->  photo.png.base64.txt   (76 characters per line)
Decoding:  photo.png.base64.txt  ->  photo.png   (suggested name; you can change it)
"""

import base64
import binascii
import os
import re
import shlex
import sys

LINE_WIDTH = 76          # classic MIME width, prints cleanly on paper
SUFFIX = ".base64.txt"
CHUNK = 3 * 1024 * 256   # bytes read per chunk; multiple of 3 so no mid-stream padding


# ----------------------------------------------------------------- file picking
def clean_path(raw: str) -> str:
    """Handle drag-and-drop into Terminal (quotes / backslash-escaped spaces)."""
    raw = raw.strip()
    try:
        parts = shlex.split(raw)
        if len(parts) == 1:
            raw = parts[0]
    except ValueError:
        pass
    return os.path.expanduser(raw)


def ask_file(prompt: str, must_exist: bool = True) -> str:
    """Try a native file dialog; fall back to typing/dragging a path in the terminal."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.update()
        root.lift()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(title=prompt) if must_exist else ""
        root.destroy()
        if path:
            return path
    except Exception:
        pass  # tkinter missing or no GUI -> terminal prompt

    while True:
        path = clean_path(input(f"{prompt}\n(type or drag the file here, then Enter): "))
        if not must_exist or os.path.isfile(path):
            return path
        print(f"  Not found: {path}")


def ask_save(prompt: str, default_path: str) -> str:
    """Pop up a 'Save as' dialog (macOS asks about overwriting itself).
    Falls back to a terminal prompt if tkinter/GUI is unavailable. Returns '' if cancelled."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.update()
        root.lift()
        root.attributes("-topmost", True)
        path = filedialog.asksaveasfilename(
            title=prompt,
            initialdir=os.path.dirname(os.path.abspath(default_path)),
            initialfile=os.path.basename(default_path),
        )
        root.destroy()
        return path  # '' if the user pressed Cancel
    except Exception:
        pass  # no GUI -> terminal prompt

    raw = input(f"{prompt}\n[{default_path}]: ").strip()
    path = clean_path(raw) if raw else default_path
    if os.path.exists(path) and input(f"'{path}' exists. Overwrite? [y/N]: ").strip().lower() != "y":
        return ""
    return path


def confirm_overwrite(path: str) -> bool:
    """Only used for command-line (non-interactive) runs."""
    if not os.path.exists(path):
        return True
    return input(f"'{path}' already exists. Overwrite? [y/N]: ").strip().lower() == "y"


# ------------------------------------------------------------------ encode/decode
def encode_file(src: str, dst: str) -> None:
    """Binary file -> wrapped base64 text, streamed so big files are fine."""
    buf = ""
    with open(src, "rb") as fin, open(dst, "w", encoding="ascii", newline="\n") as fout:
        while True:
            chunk = fin.read(CHUNK)
            if not chunk:
                break
            buf += base64.b64encode(chunk).decode("ascii")
            while len(buf) >= LINE_WIDTH:
                fout.write(buf[:LINE_WIDTH] + "\n")
                buf = buf[LINE_WIDTH:]
        if buf:
            fout.write(buf + "\n")


def decode_file(src: str, dst: str) -> None:
    """Base64 text (any line wrapping / whitespace) -> original binary file."""
    with open(src, "r", encoding="ascii", errors="strict") as fin:
        text = fin.read()
    text = re.sub(r"\s+", "", text)  # drop newlines, spaces, tabs, page breaks
    # Tolerate missing padding
    text += "=" * (-len(text) % 4)
    try:
        data = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError) as e:
        raise SystemExit(f"Not valid base64: {e}")
    with open(dst, "wb") as fout:
        fout.write(data)


def suggest_decoded_name(src: str) -> str:
    if src.lower().endswith(SUFFIX):
        return src[: -len(SUFFIX)]
    base, _ = os.path.splitext(src)
    return base + ".decoded"


# --------------------------------------------------------------------------- main
def do_encode(src=None, dst=None):
    interactive = src is None
    src = src or ask_file("Choose the file to convert to base64")
    if not src:
        print("Cancelled.")
        return
    if interactive and not dst:
        dst = ask_save("Save the base64 text file as", src + SUFFIX)
    else:
        dst = dst or (src + SUFFIX)
        if not confirm_overwrite(dst):
            dst = ""
    if not dst:
        print("Cancelled.")
        return
    encode_file(src, dst)
    print(f"Done: {dst}  ({os.path.getsize(dst):,} bytes)")


def do_decode(src=None, dst=None):
    interactive = src is None
    src = src or ask_file("Choose the base64 .txt file to convert back")
    if not src:
        print("Cancelled.")
        return
    default = suggest_decoded_name(src)
    if interactive and not dst:
        dst = ask_save("Save the restored file as", default)
    else:
        dst = dst or default
        if not confirm_overwrite(dst):
            dst = ""
    if not dst:
        print("Cancelled.")
        return
    decode_file(src, dst)
    print(f"Done: {dst}  ({os.path.getsize(dst):,} bytes)")


def main():
    args = sys.argv[1:]
    if args:
        cmd = args[0].lower()
        if cmd in ("encode", "e") and len(args) >= 2:
            do_encode(args[1], args[2] if len(args) > 2 else None)
        elif cmd in ("decode", "d") and len(args) >= 2:
            do_decode(args[1], args[2] if len(args) > 2 else None)
        else:
            print(__doc__)
        return

    print("Base64 file tool")
    print("  1) Any file  ->  base64 .txt")
    print("  2) base64 .txt  ->  original/any binary file")
    choice = input("Choose 1 or 2: ").strip()
    if choice == "1":
        do_encode()
    elif choice == "2":
        do_decode()
    else:
        print("Nothing chosen.")


if __name__ == "__main__":
    main()