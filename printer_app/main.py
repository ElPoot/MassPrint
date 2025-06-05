# printer_app/main.py
import threading, tkinter as tk, tkinter.filedialog as fd, tkinter.messagebox as mb
from pathlib import Path
from core.printer import print_pdfs_in_folder

APP_TITLE = "Batch PDF Printer"
ICON_PATH = Path(__file__).with_name("app_icon.ico")


def _run(folder: str, btn, status):
    try:
        btn["state"] = "disabled"
        print_pdfs_in_folder(folder)
        mb.showinfo("Fin", "Todos los PDF fueron enviados a la impresora.")
    except Exception as e:
        mb.showerror("Error", str(e))
    finally:
        status.set("Listo")
        btn["state"] = "normal"


def choose_folder(btn, status):
    folder = fd.askdirectory(title="Carpeta raíz con subcarpetas de PDFs")
    if folder:
        status.set(f"Imprimiendo {folder} …")
        threading.Thread(target=_run, args=(folder, btn, status), daemon=True).start()


root = tk.Tk()
root.title(APP_TITLE)
root.resizable(False, False)
if ICON_PATH.is_file():
    root.iconbitmap(ICON_PATH)

status = tk.StringVar(value="Listo")
btn = tk.Button(
    root,
    text="Seleccionar carpeta y ¡Imprimir!",
    command=lambda: choose_folder(btn, status),
)
btn.pack(padx=40, pady=20)
tk.Label(root, textvariable=status).pack(pady=(0, 15))

root.mainloop()
