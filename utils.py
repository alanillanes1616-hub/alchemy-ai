"""
utils.py — Utilidades transversales: logging, helpers y sanitización.
"""

import logging
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from config import LOG_FILE, LOG_LEVEL


# ── Logger central ────────────────────────────────────────────────────────────

def get_logger(name: str = "alchemy") -> logging.Logger:
    """Devuelve un logger configurado con handler de archivo y consola."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Archivo
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Consola
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


logger = get_logger()


# ── Hashing ───────────────────────────────────────────────────────────────────

def file_hash(content: bytes) -> str:
    """SHA-256 de un archivo para detectar duplicados."""
    return hashlib.sha256(content).hexdigest()[:16]


# ── Texto ─────────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Elimina caracteres de control y normaliza espacios."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate(text: str, max_chars: int = 300) -> str:
    """Recorta texto para previsualizaciones."""
    return text[:max_chars] + "..." if len(text) > max_chars else text


# ── Fechas ────────────────────────────────────────────────────────────────────

def now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Timestamp actual como string."""
    return datetime.now().strftime(fmt)


def timestamp_filename(prefix: str = "export", ext: str = "txt") -> str:
    """Nombre de archivo con timestamp, ej: export_20240615_143022.txt"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{ext}"


# ── Validación ────────────────────────────────────────────────────────────────

def safe_filename(name: str) -> str:
    """Sanitiza un nombre de archivo eliminando caracteres no seguros."""
    return re.sub(r"[^\w\-_\. ]", "_", name).strip()


def extension(filename: str) -> str:
    """Extensión en minúsculas sin punto."""
    return Path(filename).suffix.lstrip(".").lower()


# ── Métricas rápidas ──────────────────────────────────────────────────────────

def count_tokens_approx(text: str) -> int:
    """
    Estimación rápida de tokens (≈ palabras × 1.3).
    Para uso informativo, no para billing.
    """
    return int(len(text.split()) * 1.3)


def format_size(n_bytes: int) -> str:
    """Formatea bytes en unidad legible."""
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes //= 1024
    return f"{n_bytes:.1f} TB"
