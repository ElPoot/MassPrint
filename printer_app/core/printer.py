#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Imprime PDFs subcarpeta por subcarpeta, con:
1.  Control de cola (Win32)   → espera a que termine cada trabajo.
2.  Marcador .imprimido       → evita reimpresiones de carpetas completas.
3.  Motor de impresión SumatraPDF CLI (más fiable que ShellExecute).

Requiere:
    • pywin32  (pip install pywin32)
    • SumatraPDF.exe (portable) accesible en SUMATRA_PATH
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
import win32api
import win32print

# ⇩⇩⇩  Ruta a SumatraPDF  ⇩⇩⇩  (ajusta si lo instalaste en otro sitio)
# SUMATRA_PATH = Path(r"C:\Tools\SumatraPDF\SumatraPDF.exe")
SUMATRA_PATH = Path(__file__).parent.parent / "resources" / "SumatraPDF.exe"


# ────────── utilidades cola de impresión ──────────────────────────────────────
def _queue_job_ids(printer: str) -> set[int]:
    try:
        h = win32print.OpenPrinter(printer)
        jobs = win32print.EnumJobs(h, 0, -1, 1)
        win32print.ClosePrinter(h)
        return {j["JobId"] for j in jobs}
    except Exception:
        return set()


def _wait_for_job_to_appear(
    printer: str, before: set[int], timeout: int = 30, poll: float = 0.5
) -> int:
    t0 = time.time()
    while time.time() - t0 < timeout:
        diff = _queue_job_ids(printer) - before
        if diff:
            return diff.pop()
        time.sleep(poll)
    raise TimeoutError("El trabajo nunca llegó al spooler")


def _wait_until_job_finishes(
    printer: str, job_id: int, timeout: int = 1800, poll: float = 2
) -> None:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if job_id not in _queue_job_ids(printer):
            return
        time.sleep(poll)
    raise TimeoutError("La impresora no terminó dentro del tiempo límite")


# ────────── impresión segura ─────────────────────────────────────────────────
def _print_with_sumatra(pdf: Path, printer: str) -> None:
    """Usa SumatraPDF en modo silencioso."""
    cmd = [
        str(SUMATRA_PATH),
        "-print-to",
        printer,
        "-silent",
        "-exit-when-done",
        str(pdf),
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(
            f"SumatraPDF retornó {result.returncode}: {result.stderr.decode(errors='ignore')}"
        )


def _print_with_shell_execute(pdf: Path, printer: str) -> None:
    """Plan B: ShellExecute (depende del visor PDF predeterminado)."""
    before = _queue_job_ids(printer)
    win32api.ShellExecute(0, "print", str(pdf), None, ".", 0)
    job_id = _wait_for_job_to_appear(printer, before)
    _wait_until_job_finishes(printer, job_id)


def _print_single_pdf(pdf: Path, printer: str) -> None:
    if not pdf.exists() or pdf.suffix.lower() != ".pdf":
        raise FileNotFoundError(pdf)

    if SUMATRA_PATH.is_file():
        _print_with_sumatra(pdf, printer)
    else:
        _print_with_shell_execute(pdf, printer)


# ────────── función pública ──────────────────────────────────────────────────
def print_pdfs_in_folder(root_folder: str) -> None:
    printer = win32print.GetDefaultPrinter()
    if not printer:
        raise EnvironmentError("No hay impresora predeterminada configurada")

    root = Path(root_folder)
    if not root.is_dir():
        raise NotADirectoryError(root_folder)

    total_ok = total_err = 0
    t0_global = time.time()

    for sub in sorted(d for d in root.iterdir() if d.is_dir()):
        done_flag = sub / ".imprimido"
        if done_flag.exists():
            print(f"🟡 Saltando carpeta ya impresa: {sub.name}")
            continue

        pdfs = sorted(sub.glob("*.pdf"))
        if not pdfs:
            continue

        print(f"\n📂 Carpeta: {sub.name}  ({len(pdfs)} PDF)")
        carpeta_ok = True

        for pdf in pdfs:
            try:
                _print_single_pdf(pdf, printer)
                print(f"   ✔  {pdf.name}")
                total_ok += 1
            except Exception as exc:
                print(f"   ✖  {pdf.name}  →  {exc}")
                total_err += 1
                carpeta_ok = False

        if carpeta_ok:
            try:
                done_flag.write_text("impreso")
            except Exception as e:
                print(f"⚠️  No se pudo crear {done_flag}: {e}")

    dt = time.time() - t0_global
    print("\n════ Resumen ═══════════════════")
    print(f"PDF impresos correctamente : {total_ok}")
    print(f"Errores de impresión       : {total_err}")
    print(f"Duración total             : {dt:0.1f} s")


# ────────── ejecutable directo ───────────────────────────────────────────────
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog, messagebox

    tk.Tk().withdraw()
    carpeta = filedialog.askdirectory(title="Carpeta raíz con PDFs por subcarpetas")
    if carpeta:
        try:
            print_pdfs_in_folder(carpeta)
            messagebox.showinfo(
                "Fin", "Proceso de impresión completado.\nRevisa la consola."
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
