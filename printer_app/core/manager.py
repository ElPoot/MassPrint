# core/manager.py
from pathlib import Path
import sqlite3, time, os


class EstadoImpresion:
    def __init__(self, db_path: str = "estado_impresion.db"):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS impresos(
                ruta TEXT PRIMARY KEY,
                tam  INTEGER,
                mtime REAL,
                ok   INTEGER DEFAULT 0,
                fecha REAL
            )
        """
        )
        self.con.commit()

    # ---------- alta / chequeo ----------
    def pendientes_en(self, carpeta: Path) -> list[Path]:
        """Devuelve lista de PDF que aún no se han impreso
        o han cambiado tam/mtime."""
        pendientes: list[Path] = []
        for pdf in carpeta.rglob("*.pdf"):
            ruta = str(pdf.resolve())
            stat = pdf.stat()
            tam, mtime = stat.st_size, stat.st_mtime

            self.cur.execute(
                "SELECT tam, mtime, ok FROM impresos WHERE ruta = ?", (ruta,)
            )
            fila = self.cur.fetchone()

            if fila and fila[2] == 1 and fila[0] == tam and fila[1] == mtime:
                # Ya impreso y no cambió
                continue

            if fila:
                # Existe pero cambió: reset ok=0
                self.cur.execute(
                    "UPDATE impresos SET tam=?, mtime=?, ok=0 WHERE ruta=?",
                    (tam, mtime, ruta),
                )
            else:
                self.cur.execute(
                    "INSERT INTO impresos(ruta, tam, mtime) VALUES (?,?,?)",
                    (ruta, tam, mtime),
                )
            pendientes.append(pdf)

        self.con.commit()
        return pendientes

    # ---------- marcar ----------
    def marcar_impreso(self, pdf: Path):
        ruta = str(pdf.resolve())
        self.cur.execute(
            "UPDATE impresos SET ok=1, fecha=? WHERE ruta=?", (time.time(), ruta)
        )
        self.con.commit()

    # ---------- config impresora ----------


def guardar_config(self, printer: str):
    self.cur.execute("CREATE TABLE IF NOT EXISTS config (k TEXT PRIMARY KEY, v TEXT)")
    self.cur.execute("REPLACE INTO config(k,v) VALUES ('printer',?)", (printer,))
    self.con.commit()


def cargar_config(self) -> str | None:
    self.cur.execute("CREATE TABLE IF NOT EXISTS config (k TEXT PRIMARY KEY, v TEXT)")
    self.cur.execute("SELECT v FROM config WHERE k='printer'")
    row = self.cur.fetchone()
    return row[0] if row else None
