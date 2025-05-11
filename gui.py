import os
import zipfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
from core import process_file, gather_files

class CSVCleanerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Cleaner")
        self.geometry("600x400")

        # Input selector
        tk.Label(self, text="Input:").grid(row=0, column=0, sticky="e")
        self.inp_var = tk.StringVar()
        tk.Entry(self, textvariable=self.inp_var, width=50).grid(row=0, column=1)
        tk.Button(self, text="Browse", command=lambda: self._browse(self.inp_var)).grid(row=0, column=2)

        # Output selector
        tk.Label(self, text="Output:").grid(row=1, column=0, sticky="e")
        self.out_var = tk.StringVar()
        tk.Entry(self, textvariable=self.out_var, width=50).grid(row=1, column=1)
        tk.Button(self, text="Browse", command=lambda: self._browse(self.out_var, select_dir=True)).grid(row=1, column=2)

        # Options
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_var = tk.StringVar(value="")  # optional
        self.backup_var = tk.StringVar()
        self.pattern_var = tk.StringVar(value="*.csv")
        self.zip_var = tk.StringVar()
        self.verbose = tk.BooleanVar()

        opts = [
            ("Log file (optional)", self.log_var),
            ("Backup dir (optional)", self.backup_var),
            ("Pattern", self.pattern_var),
            ("Zip name", self.zip_var)
        ]
        for i, (label, var) in enumerate(opts, start=2):
            tk.Label(self, text=f"{label}:").grid(row=i, column=0, sticky="e")
            tk.Entry(self, textvariable=var, width=40).grid(row=i, column=1, columnspan=2, sticky="w")

        tk.Checkbutton(self, text="Verbose Mode", variable=self.verbose).grid(row=6, column=1, sticky="w")

        # Console
        self.console = scrolledtext.ScrolledText(self, state="disabled", height=10)
        self.console.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Run button
        tk.Button(self, text="Run Cleanup", command=self._run).grid(row=8, column=1)

        self.grid_rowconfigure(7, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _browse(self, var, select_dir=False):
        path = filedialog.askdirectory() if select_dir else filedialog.askopenfilename()
        if path:
            var.set(path)

    def _log(self, msg: str):
        self.console.configure(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def _run(self):
        args = {
            "input": Path(self.inp_var.get()),
            "output": Path(self.out_var.get()),
            "log": self.log_var.get() or None,
            "backup": Path(self.backup_var.get()) if self.backup_var.get() else None,
            "pattern": self.pattern_var.get(),
            "zip_out": self.zip_var.get() or None,
            "verbose": self.verbose.get()
        }
        threading.Thread(target=self._worker, args=(args,), daemon=True).start()

    def _worker(self, args):
        try:
            # Logging
            if args["log"]:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_name = args["log"] if Path(args["log"]).suffix else f"{args['log']}_{timestamp}.log"
                log_fp = open(log_name, 'w', encoding='utf-8')
            else:
                log_fp = None

            # Process files
            for f in gather_files(args["input"], args["pattern"]):
                rel = f.relative_to(args["input"]) if args["input"].is_dir() else Path(f.name)
                out_fp = args["output"] / rel if args["input"].is_dir() else args["output"]
                out_fp.parent.mkdir(parents=True, exist_ok=True)
                changed = process_file(
                    f, out_fp,
                    log_fp=log_fp,
                    backup_dir=args["backup"],
                    verbose=args["verbose"],
                    input_root=args["input"] if args["backup"] else None
                )
                self._log(f"{'✔' if changed else '–'} {f}")

            # Finalize log
            if log_fp:
                log_fp.close()
                log_zip = Path(log_name).with_suffix('.zip')
                with zipfile.ZipFile(log_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                    z.write(log_name, Path(log_name).name)
                os.remove(log_name)
                self._log(f"📄 Log compressed → {log_zip}")

            # Zip output
            if args["zip_out"]:
                zipf = args["zip_out"]
                with zipfile.ZipFile(zipf, 'w', zipfile.ZIP_DEFLATED) as z:
                    for item in args["output"].rglob('*'):
                        z.write(item, item.relative_to(args["output"]))
                self._log(f"📦 Compressed to {zipf}")

            self._log("✅ Done.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    CSVCleanerGUI().mainloop()