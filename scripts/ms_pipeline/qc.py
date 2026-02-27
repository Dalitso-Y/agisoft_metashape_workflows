from __future__ import annotations
from typing import Any, Dict

def qc_snapshot(chunk: Any) -> Dict[str, Any]:
    cams = getattr(chunk, "cameras", []) or []
    aligned = 0
    for c in cams:
        try:
            if c.transform:
                aligned += 1
        except Exception:
            pass

    # Tie points (API names changed across versions; keep defensive)
    tie_pts = None
    try:
        tie_pts = chunk.tie_points
    except Exception:
        pass

    tie_count = None
    if tie_pts is not None:
        try:
            tie_count = len(tie_pts.points)
        except Exception:
            tie_count = None

    # Point cloud
    pc = None
    try:
        pc = chunk.point_cloud
    except Exception:
        pass

    pc_count = None
    if pc is not None:
        try:
            pc_count = len(pc.points)
        except Exception:
            pc_count = None

    markers = getattr(chunk, "markers", []) or []
    return {
        "cameras_total": len(cams),
        "cameras_aligned": aligned,
        "tie_points_count": tie_count,
        "point_cloud_points_count": pc_count,
        "markers_total": len(markers),
    }