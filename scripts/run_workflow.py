from __future__ import annotations
import os
import sys
import time

try:
    import Metashape
except Exception as e:
    raise RuntimeError("This script must be run inside Agisoft Metashape Professional.") from e

from ms_pipeline.config import load_json
from ms_pipeline.log import Logger
from ms_pipeline.steps import (
    collect_photos,
    set_chunk_crs,
    import_reference_if_any,
    run_match_align_optimize,
    build_depth_maps_and_point_cloud,
    build_dem_and_ortho,
    build_model_uv_texture,
    export_assets,
)
from ms_pipeline.qc import qc_snapshot

def _now_stamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")

def run(config_path: str, workflow_name: str = "workflow") -> None:
    cfg = load_json(config_path)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logs_dir = os.path.join(repo_root, "logs", workflow_name)
    log_path = os.path.join(logs_dir, f"{_now_stamp()}.log")
    log = Logger(log_path)

    log.info(f"Config: {os.path.abspath(config_path)}")
    log.info(f"Metashape version: {getattr(Metashape, 'version', 'unknown')}")
    log.info(f"Workflow: {workflow_name}")

    # Document / chunk
    doc = Metashape.app.document
    try:
        doc.clear()
    except Exception:
        pass

    chunk = doc.addChunk()
    chunk.label = cfg.get("project", {}).get("chunk_label", workflow_name)

    # Inputs
    inp = cfg.get("input", {})
    photo_dirs = inp.get("photo_dirs", [])
    photo_globs = inp.get("photo_globs", ["*.jpg", "*.jpeg", "*.tif", "*.tiff", "*.png"])
    recursive = bool(inp.get("recursive", True))

    photos = collect_photos(photo_dirs, photo_globs, recursive)
    if not photos:
        raise RuntimeError("No photos found. Check input.photo_dirs and input.photo_globs.")

    log.info(f"Photos found: {len(photos)}")
    chunk.addPhotos(photos)

    # CRS (optional)
    epsg = inp.get("crs_epsg", "")
    if epsg:
        log.info(f"Setting CRS: {epsg}")
        set_chunk_crs(Metashape, chunk, epsg)

    # Optional reference import (camera/GCP CSV etc)
    reference_cfg = cfg.get("reference", {})
    if reference_cfg.get("enabled", False):
        log.info("Importing reference data...")
        import_reference_if_any(Metashape, chunk, reference_cfg)

    # Processing
    proc = cfg.get("processing", {})
    stage = proc.get("stage", "aerial_products")

    log.info(f"Processing stage: {stage}")
    run_match_align_optimize(Metashape, chunk, proc)

    if stage in ("aerial_products", "aerial_dem_ortho"):
        build_depth_maps_and_point_cloud(Metashape, chunk, proc)
        build_dem_and_ortho(Metashape, chunk, proc)
    elif stage in ("object_model_texture",):
        build_depth_maps_and_point_cloud(Metashape, chunk, proc)
        build_model_uv_texture(Metashape, chunk, proc)
    else:
        raise ValueError(f"Unknown processing.stage: {stage}")

    # QC snapshot
    qc = qc_snapshot(chunk)
    log.info(f"QC: {qc}")

    # Exports
    export_cfg = cfg.get("export", {})
    if export_cfg:
        # Allow relative output paths to be relative to repo root
        out_dir = export_cfg.get("output_dir", "")
        if out_dir and not os.path.isabs(out_dir):
            export_cfg["output_dir"] = os.path.abspath(os.path.join(repo_root, out_dir))
        export_assets(Metashape, chunk, export_cfg)

    # Save project (optional)
    proj_path = cfg.get("project", {}).get("project_path", "")
    if proj_path:
        if not os.path.isabs(proj_path):
            proj_path = os.path.abspath(os.path.join(repo_root, proj_path))
        os.makedirs(os.path.dirname(proj_path), exist_ok=True)
        log.info(f"Saving project: {proj_path}")
        doc.save(proj_path)

    log.info("DONE")

def main(argv: list[str]) -> None:
    if len(argv) >= 2:
        config_path = argv[1]
        workflow_name = os.path.splitext(os.path.basename(config_path))[0]
        run(config_path=config_path, workflow_name=workflow_name)
        return

    # GUI-friendly fallback: run a default selector via workflow wrappers instead
    raise RuntimeError("No config path provided. Use a workflow wrapper in workflows/<name>/run.py.")

if __name__ == "__main__":
    main(sys.argv)