"""
Servidor HTTP local para servir los PDFs generados por TransControl.
Permite escanear el QR y abrir el PDF directamente desde el móvil
(siempre que esté en la misma red WiFi).
"""

import threading
import http.server
import socket
import os
import logging

_server_instance = None
_server_port = 8765
_docs_dir = "assets/docs"


def get_local_ip() -> str:
    """Obtiene la IP local de la máquina en la red."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def start_doc_server(docs_dir: str = "assets/docs", port: int = 8765) -> int:
    """
    Arranca el servidor HTTP en un hilo daemon.
    Devuelve el puerto en el que está escuchando.
    """
    global _server_instance, _server_port, _docs_dir
    _server_port = port
    _docs_dir = os.path.abspath(docs_dir)

    if _server_instance is not None:
        return _server_port  # ya corriendo

    abs_docs_dir = _docs_dir

    class SilentDocsHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=abs_docs_dir, **kwargs)

        def log_message(self, format, *args):
            pass  # suprimir logs en consola

    try:
        _server_instance = http.server.HTTPServer(("0.0.0.0", port), SilentDocsHandler)
        thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
        thread.start()
        print(f"📡 Servidor de documentos activo en http://{get_local_ip()}:{port}/")
    except OSError as e:
        print(f"⚠️ No se pudo iniciar el servidor de documentos: {e}")

    return _server_port


def get_doc_url(filename: str) -> str:
    """Devuelve la URL completa para acceder al PDF desde la red local."""
    ip = get_local_ip()
    return f"http://{ip}:{_server_port}/{filename}"


def stop_doc_server():
    """Detiene el servidor si está corriendo."""
    global _server_instance
    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None
