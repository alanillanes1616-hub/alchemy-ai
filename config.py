"""
config.py — Configuración central de Alchemy AI.
Todas las constantes, rutas y parámetros por defecto viven aquí.
"""

from pathlib import Path
from typing import Final

# ── Rutas ────────────────────────────────────────────────────────────────────
BASE_DIR: Final[Path] = Path(__file__).parent
DATA_DIR: Final[Path] = BASE_DIR / "data"
UPLOADS_DIR: Final[Path] = DATA_DIR / "uploads"
VECTORSTORE_DIR: Final[Path] = DATA_DIR / "vectorstore"
CACHE_DIR: Final[Path] = DATA_DIR / "cache"
LOGS_DIR: Final[Path] = DATA_DIR / "logs"

for _dir in (UPLOADS_DIR, VECTORSTORE_DIR, CACHE_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ── Modelos disponibles ───────────────────────────────────────────────────────
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
]

DEFAULT_MODEL = "gemini-2.5-flash"
# ── Parámetros LLM por defecto ────────────────────────────────────────────────
DEFAULT_TEMPERATURE: Final[float] = 0.2
DEFAULT_MAX_TOKENS: Final[int] = 8192
DEFAULT_TOP_P: Final[float] = 0.95
DEFAULT_TOP_K: Final[int] = 40

# ── RAG ───────────────────────────────────────────────────────────────────────
CHUNK_SIZE: Final[int] = 1000
CHUNK_OVERLAP: Final[int] = 150
RETRIEVAL_K: Final[int] = 5          # chunks recuperados por consulta
SIMILARITY_THRESHOLD: Final[float] = 0.35

# ── Embeddings ────────────────────────────────────────────────────────────────
EMBEDDING_MODEL: Final[str] = "models/embedding-001"   # Google Generative AI Embeddings

# ── Tipos de archivo aceptados ────────────────────────────────────────────────
ACCEPTED_EXTENSIONS: Final[list[str]] = [
    "pdf", "docx", "txt", "pptx", "xlsx", "csv", "md"
]

# ── Modos de trabajo ──────────────────────────────────────────────────────────
MODES: Final[dict[str, str]] = {
    "Chat":          "Conversación libre con memoria completa.",
    "Investigación": "Análisis profundo de documentos cargados.",
    "Comparación":   "Contrasta múltiples documentos con tablas.",
    "Redacción":     "Genera secciones académicas (intro, metodología, etc.).",
    "Resumen":       "Resume documentos o fragmentos seleccionados.",
    "Traducción":    "Traduce contenido de los documentos.",
    "Extracción":    "Extrae variables, hipótesis, objetivos, referencias.",
    "Libre":         "Sin instrucciones previas; comportamiento base del modelo.",
}

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE: Final[Path] = LOGS_DIR / "alchemy.log"
LOG_LEVEL: Final[str] = "INFO"

# ── Exportación ───────────────────────────────────────────────────────────────
EXPORT_FORMATS: Final[list[str]] = ["TXT", "Markdown", "DOCX", "PDF"]

