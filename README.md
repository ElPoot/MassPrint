# MassPrint

> Imprime en lote tus archivos PDF de múltiples subcarpetas con un solo clic.

MassPrint es una utilidad ligera para **Windows** escrita en **Python** y **Tkinter**. Recorre la carpeta que elijas, envía a impresión cada PDF encontrado de forma recursiva usando la CLI de **SumatraPDF**, y espera a que cada trabajo termine mediante la cola de impresión de Windows (`pywin32`). Para evitar reimpresiones, deja un archivo marcador `.imprimido` dentro de cada subcarpeta ya procesada.

---

## ✨ Características

* **Impresión masiva** con un solo clic.
* Uso de **SumatraPDF** en modo silencioso (`-silent -print-to -exit-when-done`) para un envío fiable.
* **Control de la cola**: el siguiente trabajo solo se envía cuando el anterior desaparece del spooler.
* **Protección contra dobles impresiones** mediante `.imprimido`.
* **Interfaz mínima** que permanece fluida gracias a un hilo en segundo plano.
* Se empaqueta como un único **.exe** portable con PyInstaller.

---

## 🖥️ Requisitos

| Software            | Versión                             |
| ------------------- | ----------------------------------- |
| Windows             | 10 u 11                             |
| Python              | 3.11 o superior                     |
| SumatraPDF portable | Incluido en `printer_app/resources` |
| Bibliotecas Python  | ver `requirements.txt`              |

---

## 🚀 Instalación rápida (modo desarrollo)

```powershell
# Clonar el repositorio
git clone https://github.com/ElPoot/MassPrint.git
cd MassPrint

# Crear entorno virtual (opcional)
python -m venv .venv
.\.venv\Scripts\activate  # En PowerShell

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación\python printer_app\main.py
```

---

## 📦 Construir el ejecutable standalone

```powershell
py -m PyInstaller ^
  --onefile --windowed ^
  --icon printer_app/app_icon.ico ^
  --add-data "printer_app/resources;printer_app/resources" ^
  printer_app/main.py
```

El ejecutable aparecerá en `dist\main.exe`.

---

## 🗂️ Estructura del proyecto

```text
printer_app/
├─ core/
│  └─ printer.py        # motor de impresión
├─ resources/
│  ├─ SumatraPDF.exe    # lector PDF portable usado en CLI
│  ├─ SumatraPDF-settings.txt
│  └─ app_icon.ico
├─ main.py              # GUI Tkinter
└─ ...
```

---

## 🔄 Versionado

Este proyecto sigue **Semantic Versioning** (MAJOR.MINOR.PATCH).

* **v1.0.0** – Primera versión estable.

---

## 🛣️ Hoja de ruta

* Barra de progreso y botón *Cancelar*.
* Selector de impresora.
* Persistencia de configuración (última carpeta, impresora, etc.).
* Comprobación automática de actualizaciones vía GitHub Releases.

---

## 🤝 Contribuir

¡Los *Pull Requests* son bienvenidos! Para cambios grandes, abre primero un *issue* y comentamos la propuesta.

---

## 📜 Licencia

Distribuido bajo la licencia MIT. Consulta el archivo **LICENSE** para más detalles.

---

## 🙏 Agradecimientos

* [SumatraPDF](https://www.sumatrapdfreader.org)
* [PyInstaller](https://www.pyinstaller.org)
