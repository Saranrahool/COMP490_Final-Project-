import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from datetime import datetime

# Try to import drag-and-drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

from hashing import generate_hash


# ── Theme ─────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT     = "#4A9EFF"
SUCCESS    = "#3DD68C"
DANGER     = "#FF5C5C"
SURFACE    = "#1E1E2E"
SURFACE2   = "#2A2A3E"
TEXT_DIM   = "#888899"
FONT_HEAD  = ("Courier New", 22, "bold")
FONT_LABEL = ("Courier New", 11)
FONT_MONO  = ("Courier New", 10)


# ── Drop Zone Widget ───────────────────────────────────────────────────────────
class DropZone(ctk.CTkFrame):
    """A labelled frame that accepts drag-and-drop or browse-to-select a file."""

    def __init__(self, master, label: str, on_file_selected, **kwargs):
        super().__init__(master, fg_color=SURFACE2, corner_radius=12, **kwargs)
        self.on_file_selected = on_file_selected
        self.file_path = ""

        self.columnconfigure(0, weight=1)

        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text=label, font=("Courier New", 12, "bold"),
                     text_color=ACCENT).grid(row=0, column=0, sticky="w")

        self.browse_btn = ctk.CTkButton(
            header, text="Browse", width=80, height=26,
            font=FONT_LABEL, fg_color=SURFACE, hover_color=ACCENT,
            border_color=ACCENT, border_width=1,
            command=self._browse
        )
        self.browse_btn.grid(row=0, column=1)

        # Drop / status area
        self.drop_label = ctk.CTkLabel(
            self,
            text="⬇  Drop file here  or  Browse",
            font=FONT_LABEL,
            text_color=TEXT_DIM,
            height=60,
            anchor="center",
        )
        self.drop_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 12))

        # Register drag-and-drop if available
        if DND_AVAILABLE:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self._on_drop)

    def _browse(self):
        path = filedialog.askopenfilename()
        if path:
            self._set_file(path)

    def _on_drop(self, event):
        # tkinterdnd2 wraps paths in {} when they contain spaces
        path = event.data.strip().strip("{}")
        if os.path.isfile(path):
            self._set_file(path)

    def _set_file(self, path: str):
        self.file_path = path
        name = os.path.basename(path)
        size = os.path.getsize(path)
        size_str = f"{size / 1024:.1f} KB" if size < 1_048_576 else f"{size / 1_048_576:.2f} MB"
        self.drop_label.configure(
            text=f"📄  {name}   ({size_str})",
            text_color="white"
        )
        self.on_file_selected(path)

    def reset(self):
        self.file_path = ""
        self.drop_label.configure(text="⬇  Drop file here  or  Browse", text_color=TEXT_DIM)


# ── Single Hash Tab ────────────────────────────────────────────────────────────
class SingleHashTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.file_path = ""
        self.algorithm = ctk.StringVar(value="sha256")
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # Drop zone
        self.zone = DropZone(self, "Select File", self._on_file_selected)
        self.zone.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 10))

        # Algorithm row
        algo_row = ctk.CTkFrame(self, fg_color="transparent")
        algo_row.grid(row=1, column=0, sticky="ew", padx=24, pady=6)
        ctk.CTkLabel(algo_row, text="Algorithm:", font=FONT_LABEL).pack(side="left")
        ctk.CTkSegmentedButton(
            algo_row, values=["md5", "sha256"],
            variable=self.algorithm, font=FONT_LABEL, width=180
        ).pack(side="left", padx=12)

        # Hash button
        self.hash_btn = ctk.CTkButton(
            self, text="Generate Hash", font=("Courier New", 12, "bold"),
            height=38, fg_color=ACCENT, hover_color="#2a7de0",
            command=self._run
        )
        self.hash_btn.grid(row=2, column=0, padx=24, pady=10, sticky="ew")

        # Result frame
        result_frame = ctk.CTkFrame(self, fg_color=SURFACE2, corner_radius=12)
        result_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(4, 10))
        result_frame.columnconfigure(0, weight=1)

        self.result_label = ctk.CTkLabel(
            result_frame, text="Hash will appear here",
            font=FONT_MONO, text_color=TEXT_DIM,
            wraplength=600, justify="left", anchor="w"
        )
        self.result_label.grid(row=0, column=0, padx=14, pady=12, sticky="ew")

        self.copy_btn = ctk.CTkButton(
            result_frame, text="Copy", width=70, height=28,
            font=FONT_LABEL, fg_color=SURFACE, hover_color=ACCENT,
            border_color=ACCENT, border_width=1,
            command=self._copy, state="disabled"
        )
        self.copy_btn.grid(row=0, column=1, padx=(0, 12))

        self._hash_value = ""

    def _on_file_selected(self, path):
        self.file_path = path

    def _run(self):
        if not self.file_path:
            messagebox.showwarning("No file", "Please select a file first.")
            return
        try:
            h = generate_hash(self.file_path, self.algorithm.get())
            self._hash_value = h
            self.result_label.configure(
                text=h, text_color=SUCCESS
            )
            self.copy_btn.configure(state="normal")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _copy(self):
        if self._hash_value:
            self.clipboard_clear()
            self.clipboard_append(self._hash_value)
            self.copy_btn.configure(text="Copied ✓")
            self.after(1800, lambda: self.copy_btn.configure(text="Copy"))

    def reset(self):
        self.file_path = ""
        self._hash_value = ""
        self.zone.reset()
        self.result_label.configure(text="Hash will appear here", text_color=TEXT_DIM)
        self.copy_btn.configure(state="disabled", text="Copy")


# ── Compare Tab ────────────────────────────────────────────────────────────────
class CompareTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.file1 = ""
        self.file2 = ""
        self.algorithm = ctk.StringVar(value="sha256")
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        # Two drop zones
        self.zone1 = DropZone(self, "File 1", lambda p: setattr(self, "file1", p))
        self.zone1.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 6))

        self.zone2 = DropZone(self, "File 2", lambda p: setattr(self, "file2", p))
        self.zone2.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))

        # Algorithm row
        algo_row = ctk.CTkFrame(self, fg_color="transparent")
        algo_row.grid(row=2, column=0, sticky="ew", padx=24, pady=4)
        ctk.CTkLabel(algo_row, text="Algorithm:", font=FONT_LABEL).pack(side="left")
        ctk.CTkSegmentedButton(
            algo_row, values=["md5", "sha256"],
            variable=self.algorithm, font=FONT_LABEL, width=180
        ).pack(side="left", padx=12)

        # Buttons row
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, sticky="ew", padx=24, pady=8)
        btn_row.columnconfigure((0, 1), weight=1)

        self.compare_btn = ctk.CTkButton(
            btn_row, text="Compare Files", font=("Courier New", 12, "bold"),
            height=38, fg_color=ACCENT, hover_color="#2a7de0",
            command=self._run
        )
        self.compare_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.save_btn = ctk.CTkButton(
            btn_row, text="Save Report", font=FONT_LABEL,
            height=38, fg_color=SURFACE2, hover_color=SURFACE,
            border_color=TEXT_DIM, border_width=1,
            command=self._save
        )
        self.save_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Verdict banner
        self.verdict = ctk.CTkLabel(
            self, text="", font=("Courier New", 16, "bold"), height=40
        )
        self.verdict.grid(row=4, column=0, pady=(4, 0))

        # Details output
        detail_frame = ctk.CTkFrame(self, fg_color=SURFACE2, corner_radius=12)
        detail_frame.grid(row=5, column=0, sticky="nsew", padx=24, pady=(6, 20))
        detail_frame.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)

        self.output = ctk.CTkTextbox(
            detail_frame, font=FONT_MONO,
            fg_color="transparent", wrap="none", height=160
        )
        self.output.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        detail_frame.rowconfigure(0, weight=1)

        # Copy hashes buttons row
        copy_row = ctk.CTkFrame(detail_frame, fg_color="transparent")
        copy_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))

        self.copy1_btn = ctk.CTkButton(
            copy_row, text="Copy Hash 1", width=120, height=26,
            font=FONT_LABEL, fg_color=SURFACE, hover_color=ACCENT,
            border_color=ACCENT, border_width=1,
            command=lambda: self._copy_hash(1), state="disabled"
        )
        self.copy1_btn.pack(side="left", padx=(0, 8))

        self.copy2_btn = ctk.CTkButton(
            copy_row, text="Copy Hash 2", width=120, height=26,
            font=FONT_LABEL, fg_color=SURFACE, hover_color=ACCENT,
            border_color=ACCENT, border_width=1,
            command=lambda: self._copy_hash(2), state="disabled"
        )
        self.copy2_btn.pack(side="left")

        self._hash1 = ""
        self._hash2 = ""
        self._report_text = ""

    def _run(self):
        if not self.file1 or not self.file2:
            messagebox.showwarning("No files", "Please select both files.")
            return
        try:
            algo = self.algorithm.get()
            self._hash1 = generate_hash(self.file1, algo)
            self._hash2 = generate_hash(self.file2, algo)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            match = self._hash1 == self._hash2

            self.verdict.configure(
                text="✅  Files are identical" if match else "❌  Files differ",
                text_color=SUCCESS if match else DANGER
            )

            lines = [
                f"Time       : {now}",
                f"Algorithm  : {algo.upper()}",
                "",
                f"File 1     : {self.file1}",
                f"Hash 1     : {self._hash1}",
                "",
                f"File 2     : {self.file2}",
                f"Hash 2     : {self._hash2}",
                "",
                f"Result     : {'MATCH' if match else 'DIFFERENT'}",
            ]
            self._report_text = "\n".join(lines)

            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.insert("end", self._report_text)
            self.output.configure(state="disabled")

            self.copy1_btn.configure(state="normal")
            self.copy2_btn.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _copy_hash(self, n):
        val = self._hash1 if n == 1 else self._hash2
        btn = self.copy1_btn if n == 1 else self.copy2_btn
        if val:
            self.clipboard_clear()
            self.clipboard_append(val)
            btn.configure(text="Copied ✓")
            self.after(1800, lambda: btn.configure(text=f"Copy Hash {n}"))

    def _save(self):
        if not self._report_text.strip():
            messagebox.showwarning("Empty", "Run a comparison first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if path:
            with open(path, "w") as f:
                f.write(self._report_text)
            messagebox.showinfo("Saved", "Report saved.")

    def reset(self):
        self.file1 = self.file2 = ""
        self._hash1 = self._hash2 = ""
        self._report_text = ""
        self.zone1.reset()
        self.zone2.reset()
        self.verdict.configure(text="")
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")
        self.copy1_btn.configure(state="disabled", text="Copy Hash 1")
        self.copy2_btn.configure(state="disabled", text="Copy Hash 2")


# ── Main App ───────────────────────────────────────────────────────────────────
class FileIntegrityApp(ctk.CTk if not DND_AVAILABLE else type("_Base", (TkinterDnD.Tk, ctk.CTk), {})):
    pass


class FileIntegrityGUI:
    def __init__(self):
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            self.root.configure(bg=SURFACE)
        else:
            self.root = ctk.CTk()

        self.root.title("File Integrity Checker")
        self.root.geometry("720x600")
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # ── Header ──
        header = ctk.CTkFrame(self.root, fg_color=SURFACE2, corner_radius=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="FILE INTEGRITY CHECKER",
            font=FONT_HEAD, text_color=ACCENT
        ).grid(row=0, column=0, sticky="w", padx=24, pady=14)

        # Clear button
        ctk.CTkButton(
            header, text="Clear All", width=80, height=30,
            font=FONT_LABEL, fg_color=SURFACE, hover_color=DANGER,
            border_color=DANGER, border_width=1,
            command=self._clear
        ).grid(row=0, column=1, padx=(0, 24))

        # ── Tabs ──
        tabs = ctk.CTkTabview(self.root, fg_color=SURFACE, segmented_button_fg_color=SURFACE2,
                              segmented_button_selected_color=ACCENT,
                              segmented_button_unselected_hover_color=SURFACE)
        tabs.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        tabs.columnconfigure(0, weight=1)

        tabs.add("Hash File")
        tabs.add("Compare Files")

        self.single_tab = SingleHashTab(tabs.tab("Hash File"))
        self.single_tab.pack(fill="both", expand=True)

        self.compare_tab = CompareTab(tabs.tab("Compare Files"))
        self.compare_tab.pack(fill="both", expand=True)

        self._tabs = tabs

        # DND hint
        if not DND_AVAILABLE:
            ctk.CTkLabel(
                self.root,
                text="💡 Install tkinterdnd2 for drag-and-drop support",
                font=("Courier New", 9), text_color=TEXT_DIM
            ).grid(row=2, column=0, pady=(0, 4))

    def _clear(self):
        self.single_tab.reset()
        self.compare_tab.reset()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FileIntegrityGUI()
    app.run()