from __future__ import annotations
from typing import Any, Optional

def ms_attr(Metashape: Any, name: str, default: Optional[Any] = None) -> Any:
    """
    Return Metashape.<name> if it exists, else default.
    We keep config strings aligned with Metashape constant names.
    """
    return getattr(Metashape, name, default)

def require_ms_attr(Metashape: Any, name: str) -> Any:
    v = getattr(Metashape, name, None)
    if v is None:
        raise ValueError(f"Metashape enum/constant not found: {name}")
    return v

def maybe_enum(Metashape: Any, value: Any, default: Any = None) -> Any:
    """
    If value is a string, treat it as Metashape.<value>.
    Otherwise return value as-is.
    """
    if value is None:
        return default
    if isinstance(value, str):
        return ms_attr(Metashape, value, default)
    return value