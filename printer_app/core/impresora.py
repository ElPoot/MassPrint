from pathlib import Path
import subprocess, time
import win32print, win32con, pywintypes, tkinter as tk
from tkinter import simpledialog

SUMATRA = Path(__file__).resolve().parent.parent / "resources" / "SumatraPDF.exe"

# --------------------------------------------------
# Fallbacks si la constante no existe en win32print
_PD_RETURNDC = getattr(win32print, "PD_RETURNDC", 0x0100)
_PD_USEDEVMODECOPIESANDCOLLATE = getattr(
    win32print, "PD_USEDEVMODECOPIESANDCOLLATE", 0x40000
)


# ----------------------------------------------------------------------
def seleccionar_impresora() -> tuple[str, bytes | None]:
    """
    Devuelve (nombre_impresora, None).  Muestra un
    cuadro con la lista de impresoras instaladas y
    evita cualquier llamada problemática a PrintDlg.
    """
    impresoras = [p[2] for p in win32print.EnumPrinters(2)]
    if not impresoras:
        raise RuntimeError("No hay impresoras instaladas")

    root = tk.Tk()
    root.withdraw()
    impresora = simpledialog.askstring(
        "Seleccionar impresora",
        "Escribe el nombre exacto de la impresora:\n\n" + "\n".join(impresoras),
    )
    root.destroy()

    if not impresora or impresora not in impresoras:
        raise RuntimeError("Selección cancelada")
    return impresora, None


# ----------------------------------------------------------------------
def _esperar_cola(prn: str):
    while True:
        h = win32print.OpenPrinter(prn)
        jobs = win32print.EnumJobs(h, 0, -1, 1)
        win32print.ClosePrinter(h)
        if not jobs:
            break
        time.sleep(0.3)


def imprimir_pdf(pdf: Path, printer: str):
    """Llama a Sumatra con la impresora elegida; respeta ajustes guardados
    en el driver (color, orientación, etc.)."""
    cmd = [str(SUMATRA), "-silent", "-print-to", printer, "-exit-when-done", str(pdf)]
    subprocess.run(cmd, check=True)
    _esperar_cola(printer)


def imprimir_lote(lista_pdf: list[Path], printer: str):
    for pdf in lista_pdf:
        imprimir_pdf(pdf, printer)
