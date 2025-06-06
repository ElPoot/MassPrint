# ui/main.py
import threading, queue, time, subprocess, os, tkinter as tk
from tkinter import ttk, filedialog, messagebox as mb
from pathlib import Path
import logging

from printer_app.core.manager import EstadoImpresion
from printer_app.core.impresora import (
    seleccionar_impresora,
    imprimir_lote,
)


# ----- logging -----
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/MassPrint.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def seleccionar_carpeta():
    carpeta = filedialog.askdirectory()
    if not carpeta:
        return
    ruta = Path(carpeta)

    # eventos de control
    pause_evt = threading.Event()  # clear = continuar
    cancel_evt = threading.Event()

    def toogle_pause():
        if pause_evt.is_set():
            pause_evt.clear()
            btn_pause.config(text="Pausar")
        else:
            pause_evt.set()
            btn_pause.config(text="Reanudar")

    btn_pause.config(text="Pausar", command=toogle_pause, state="normal")
    btn_cancel.config(command=lambda: cancel_evt.set(), state="normal")

    btn["state"] = "disabled"
    status.set("Procesando…")
    q = queue.Queue()

    th = threading.Thread(
        target=run_impresion,
        args=(ruta, q, pause_evt, cancel_evt, mostrar_dialogo.get()),
        daemon=True,
    )
    th.start()

    poll_queue(q, pause_evt)


def run_impresion(carpeta, cola, pause_evt, cancel_evt, pedir_dialogo):
    em = EstadoImpresion()
    if pedir_dialogo:
        printer = seleccionar_impresora()
        em.guardar_config(printer)
    else:
        printer = em.cargar_config()
        if not printer:
            printer = seleccionar_impresora()
            em.guardar_config(printer)
    pendientes = None
    pendientes = em.pendientes_en(carpeta)
    cola.put(("total", len(pendientes)))
    errores = []

    for i, pdf in enumerate(pendientes, 1):
        if cancel_evt.is_set():
            cola.put(("cancel", errores))
            return
        while pause_evt.is_set():
            time.sleep(0.25)

        try:
            imprimir_lote([pdf], printer)
            em.marcar_impreso(pdf)
            logging.info(f"OK {pdf}")
        except Exception as exc:
            errores.append(pdf)
            logging.error(f"ERR {pdf} -> {exc}")
        cola.put(("progress", i))

    cola.put(("done", errores))


def mostrar_errores(lista):
    win = tk.Toplevel(root)
    win.title("Errores de impresión")
    ttk.Label(win, text=f"Archivos con error: {len(lista)}").pack(pady=5)
    lb = tk.Listbox(win, width=60)
    lb.pack(padx=10, pady=5, fill="both", expand=True)
    for p in lista:
        lb.insert("end", p.name)

    def abrir_sel():
        sel = lb.curselection()
        if sel:
            subprocess.Popen(["explorer", "/select,", str(lista[sel[0]])])

    lb.bind("<Double-Button-1>", lambda e: abrir_sel())

    def reintentar():
        win.destroy()
        # nueva impresión solo de fallos
        q2 = queue.Queue()
        threading.Thread(
            target=run_impresion,
            args=(None, q2, threading.Event(), threading.Event(), False),
            daemon=True,
        ).start()

    ttk.Button(win, text="Re-imprimir fallos", command=reintentar).pack(pady=(0, 8))


def poll_queue(cola, pause_evt):
    try:
        while True:
            msg = cola.get_nowait()
            if msg[0] == "total":
                barra["maximum"] = msg[1]
            elif msg[0] == "progress":
                progreso.set(msg[1])
            elif msg[0] == "cancel":
                mostrar_errores(msg[1]) if msg[1] else None
                finalizar()
                mb.showwarning("Cancelado", "La impresión fue cancelada.")
                return
            elif msg[0] == "done":
                (
                    mostrar_errores(msg[1])
                    if msg[1]
                    else mb.showinfo("Fin", "Todo impreso sin errores.")
                )
                finalizar()
                return
    except queue.Empty:
        root.after(150, lambda: poll_queue(cola, pause_evt))


def finalizar():
    status.set("Listo")
    btn["state"] = "normal"
    btn_pause.config(state="disabled")
    btn_cancel.config(state="disabled")
    progreso.set(0)
    barra["maximum"] = 1


# ----- TK -----
root = tk.Tk()
root.title("MassPrint 2.0")
root.resizable(False, False)

mostrar_dialogo = tk.BooleanVar(value=False)
ttk.Checkbutton(
    root, text="Mostrar diálogo solo en el primer PDF", variable=mostrar_dialogo
).pack(pady=(10, 0))

btn = ttk.Button(root, text="Seleccionar carpeta", command=seleccionar_carpeta)
btn.pack(padx=20, pady=(20, 10))
frame_ctl = ttk.Frame(root)
frame_ctl.pack(pady=(5, 10))
btn_pause = ttk.Button(frame_ctl, text="Pausar", state="disabled")
btn_cancel = ttk.Button(frame_ctl, text="Cancelar", state="disabled")
btn_pause.grid(row=0, column=0, padx=5)
btn_cancel.grid(row=0, column=1, padx=5)

progreso = tk.IntVar(value=0)
barra = ttk.Progressbar(
    root,
    orient="horizontal",
    length=300,
    mode="determinate",
    variable=progreso,
    maximum=1,
)
barra.pack(pady=(0, 10))

status = tk.StringVar(value="Listo")
ttk.Label(root, textvariable=status).pack(pady=(0, 20))

root.mainloop()
