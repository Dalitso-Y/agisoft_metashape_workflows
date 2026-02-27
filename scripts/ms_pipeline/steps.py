from __future__ import annotations
import os
import glob
from typing import Any, Dict, List, Optional

from .enums import maybe_enum, require_ms_attr

def collect_photos(photo_dirs: List[str], globs_: List[str], recursive: bool) -> List[str]:
    paths: List[str] = []
    for d in photo_dirs:
        if not d:
            continue
        d = os.path.abspath(d)
        if not os.path.isdir(d):
            continue
        for pattern in globs_:
            g = os.path.join(d, pattern)
            paths.extend(glob.glob(g, recursive=recursive))
    # De-dupe while preserving order
    seen = set()
    out = []
    for p in paths:
        ap = os.path.abspath(p)
        if ap not in seen and os.path.isfile(ap):
            seen.add(ap)
            out.append(ap)
    return out

def set_chunk_crs(Metashape: Any, chunk: Any, epsg: Optional[str]) -> None:
    if not epsg:
        return
    # Metashape expects EPSG strings like "EPSG::32641" :contentReference[oaicite:11]{index=11}
    chunk.crs = Metashape.CoordinateSystem(epsg)
    chunk.updateTransform()

def import_reference_if_any(Metashape: Any, chunk: Any, ref_cfg: Dict[str, Any]) -> None:
    """
    Optional: import camera/GCP reference data from CSV/etc via chunk.importReference().
    """
    if not ref_cfg or not ref_cfg.get("enabled", False):
        return

    path = ref_cfg.get("path", "")
    if not path:
        raise ValueError("reference.enabled is true but reference.path is empty")

    fmt = maybe_enum(Metashape, ref_cfg.get("format", "ReferenceFormatCSV"), Metashape.ReferenceFormatCSV)
    columns = ref_cfg.get("columns", "")
    delimiter = ref_cfg.get("delimiter", ",")
    group_delimiters = bool(ref_cfg.get("group_delimiters", False))
    skip_rows = int(ref_cfg.get("skip_rows", 0))
    items = maybe_enum(Metashape, ref_cfg.get("items", "ReferenceItemsAll"), Metashape.ReferenceItemsAll)
    crs = ref_cfg.get("crs_epsg", None)
    crs_obj = Metashape.CoordinateSystem(crs) if crs else None

    chunk.importReference(
        path,
        format=fmt,
        columns=columns,
        delimiter=delimiter,
        group_delimiters=group_delimiters,
        skip_rows=skip_rows,
        items=items,
        crs=crs_obj,
        create_markers=bool(ref_cfg.get("create_markers", False)),
        ignore_labels=bool(ref_cfg.get("ignore_labels", False)),
        threshold=float(ref_cfg.get("threshold", 0.1)),
        load_rotation=bool(ref_cfg.get("load_rotation", True)),
        load_location_accuracy=bool(ref_cfg.get("load_location_accuracy", False)),
        load_rotation_accuracy=bool(ref_cfg.get("load_rotation_accuracy", False)),
        load_enabled=bool(ref_cfg.get("load_enabled", False)),
    )
    chunk.updateTransform()

def run_match_align_optimize(Metashape: Any, chunk: Any, cfg: Dict[str, Any]) -> None:
    mp = cfg.get("match_photos", {})
    chunk.matchPhotos(
        downscale=int(mp.get("downscale", 1)),
        generic_preselection=bool(mp.get("generic_preselection", True)),
        reference_preselection=bool(mp.get("reference_preselection", True)),
        filter_mask=bool(mp.get("filter_mask", False)),
        mask_tiepoints=bool(mp.get("mask_tiepoints", True)),
        filter_stationary_points=bool(mp.get("filter_stationary_points", True)),
        keypoint_limit=int(mp.get("keypoint_limit", 40000)),
        tiepoint_limit=int(mp.get("tiepoint_limit", 4000)),
        guided_matching=bool(mp.get("guided_matching", False)),
        reset_matches=bool(mp.get("reset_matches", False)),
        subdivide_task=bool(mp.get("subdivide_task", True)),
    )

    ac = cfg.get("align_cameras", {})
    chunk.alignCameras(
        min_image=int(ac.get("min_image", 2)),
        adaptive_fitting=bool(ac.get("adaptive_fitting", False)),
        reset_alignment=bool(ac.get("reset_alignment", False)),
        subdivide_task=bool(ac.get("subdivide_task", True)),
        align_laser_scans=bool(ac.get("align_laser_scans", False)),
    )

    oc = cfg.get("optimize_cameras", {})
    if oc.get("enabled", True):
        chunk.optimizeCameras(
            fit_f=bool(oc.get("fit_f", True)),
            fit_cx=bool(oc.get("fit_cx", True)),
            fit_cy=bool(oc.get("fit_cy", True)),
            fit_b1=bool(oc.get("fit_b1", False)),
            fit_b2=bool(oc.get("fit_b2", False)),
            fit_k1=bool(oc.get("fit_k1", True)),
            fit_k2=bool(oc.get("fit_k2", True)),
            fit_k3=bool(oc.get("fit_k3", True)),
            fit_k4=bool(oc.get("fit_k4", False)),
            fit_p1=bool(oc.get("fit_p1", True)),
            fit_p2=bool(oc.get("fit_p2", True)),
            fit_corrections=bool(oc.get("fit_corrections", False)),
            adaptive_fitting=bool(oc.get("adaptive_fitting", False)),
            tiepoint_covariance=bool(oc.get("tiepoint_covariance", False)),
        )

def build_depth_maps_and_point_cloud(Metashape: Any, chunk: Any, cfg: Dict[str, Any]) -> None:
    dm = cfg.get("build_depth_maps", {})
    if dm.get("enabled", True):
        chunk.buildDepthMaps(
            downscale=int(dm.get("downscale", 4)),
            filter_mode=maybe_enum(Metashape, dm.get("filter_mode", "MildFiltering"), Metashape.MildFiltering),
            reuse_depth=bool(dm.get("reuse_depth", False)),
            max_neighbors=int(dm.get("max_neighbors", 16)),
            subdivide_task=bool(dm.get("subdivide_task", True)),
        )

    pc = cfg.get("build_point_cloud", {})
    if pc.get("enabled", True):
        chunk.buildPointCloud(
            source_data=maybe_enum(Metashape, pc.get("source_data", "DepthMapsData"), Metashape.DepthMapsData),
            point_colors=bool(pc.get("point_colors", True)),
            point_confidence=bool(pc.get("point_confidence", False)),
            keep_depth=bool(pc.get("keep_depth", True)),
            max_neighbors=int(pc.get("max_neighbors", 100)),
            uniform_sampling=bool(pc.get("uniform_sampling", True)),
            points_spacing=float(pc.get("points_spacing", 0.1)),
            subdivide_task=bool(pc.get("subdivide_task", True)),
        )

def build_dem_and_ortho(Metashape: Any, chunk: Any, cfg: Dict[str, Any]) -> None:
    dem = cfg.get("build_dem", {})
    if dem.get("enabled", True):
        chunk.buildDem(
            source_data=maybe_enum(Metashape, dem.get("source_data", "PointCloudData"), Metashape.PointCloudData),
            interpolation=maybe_enum(Metashape, dem.get("interpolation", "EnabledInterpolation"), Metashape.EnabledInterpolation),
            resolution=float(dem.get("resolution", 0)),
            subdivide_task=bool(dem.get("subdivide_task", True)),
        )

    ortho = cfg.get("build_orthomosaic", {})
    if ortho.get("enabled", True):
        chunk.buildOrthomosaic(
            surface_data=maybe_enum(Metashape, ortho.get("surface_data", "ElevationData"), Metashape.ElevationData),
            blending_mode=maybe_enum(Metashape, ortho.get("blending_mode", "MosaicBlending"), Metashape.MosaicBlending),
            fill_holes=bool(ortho.get("fill_holes", True)),
            ghosting_filter=bool(ortho.get("ghosting_filter", False)),
            refine_seamlines=bool(ortho.get("refine_seamlines", False)),
            resolution=float(ortho.get("resolution", 0)),
            subdivide_task=bool(ortho.get("subdivide_task", True)),
        )

def build_model_uv_texture(Metashape: Any, chunk: Any, cfg: Dict[str, Any]) -> None:
    model = cfg.get("build_model", {})
    if model.get("enabled", True):
        chunk.buildModel(
            surface_type=maybe_enum(Metashape, model.get("surface_type", "Arbitrary"), Metashape.Arbitrary),
            interpolation=maybe_enum(Metashape, model.get("interpolation", "EnabledInterpolation"), Metashape.EnabledInterpolation),
            face_count=maybe_enum(Metashape, model.get("face_count", "HighFaceCount"), Metashape.HighFaceCount),
            face_count_custom=int(model.get("face_count_custom", 200000)),
            source_data=maybe_enum(Metashape, model.get("source_data", "DepthMapsData"), Metashape.DepthMapsData),
            vertex_colors=bool(model.get("vertex_colors", True)),
            vertex_confidence=bool(model.get("vertex_confidence", True)),
            keep_depth=bool(model.get("keep_depth", True)),
        )

    uv = cfg.get("build_uv", {})
    if uv.get("enabled", True):
        chunk.buildUV(
            mapping_mode=maybe_enum(Metashape, uv.get("mapping_mode", "GenericMapping"), Metashape.GenericMapping),
            page_count=int(uv.get("page_count", 1)),
            texture_size=int(uv.get("texture_size", 8192)),
            pixel_size=float(uv.get("pixel_size", 0)),
        )

    tex = cfg.get("build_texture", {})
    if tex.get("enabled", True):
        chunk.buildTexture(
            blending_mode=maybe_enum(Metashape, tex.get("blending_mode", "NaturalBlending"), Metashape.NaturalBlending),
            texture_size=int(tex.get("texture_size", 8192)),
            downscale=int(tex.get("downscale", 2)),
            sharpening=int(tex.get("sharpening", 1)),
            fill_holes=bool(tex.get("fill_holes", True)),
            ghosting_filter=bool(tex.get("ghosting_filter", True)),
            texture_type=maybe_enum(Metashape, tex.get("texture_type", "DiffuseMap"), Metashape.DiffuseMap),
            source_data=maybe_enum(Metashape, tex.get("source_data", "ImagesData"), Metashape.ImagesData),
            transfer_texture=bool(tex.get("transfer_texture", True)),
            anti_aliasing=int(tex.get("anti_aliasing", 1)),
        )

def export_assets(Metashape: Any, chunk: Any, export_cfg: Dict[str, Any]) -> None:
    if not export_cfg:
        return

    out_dir = export_cfg.get("output_dir", "")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Report
    rep = export_cfg.get("report", {})
    if rep.get("enabled", False):
        chunk.exportReport(
            path=rep.get("path", os.path.join(out_dir, "report.pdf")),
            title=rep.get("title", ""),
            description=rep.get("description", ""),
            font_size=int(rep.get("font_size", 12)),
            page_numbers=bool(rep.get("page_numbers", True)),
            save_system_info=bool(rep.get("save_system_info", True)),
        )

    # Raster exports (DEM + Ortho) using exportRaster() :contentReference[oaicite:12]{index=12}
    for r in export_cfg.get("rasters", []):
        if not r.get("enabled", True):
            continue
        path = r.get("path", "")
        if not path:
            continue

        chunk.exportRaster(
            path=path,
            format=maybe_enum(Metashape, r.get("format", "RasterFormatGeoTIFF"), Metashape.RasterFormatGeoTIFF),
            image_format=maybe_enum(Metashape, r.get("image_format", "ImageFormatNone"), Metashape.ImageFormatNone),
            source_data=maybe_enum(Metashape, r.get("source_data", "OrthomosaicData"), Metashape.OrthomosaicData),
            save_world=bool(r.get("save_world", True)),
            save_alpha=bool(r.get("save_alpha", True)),
            white_background=bool(r.get("white_background", True)),
            clip_to_boundary=bool(r.get("clip_to_boundary", True)),
        )

    # Model export (optional)
    m = export_cfg.get("model", {})
    if m.get("enabled", False):
        chunk.exportModel(
            path=m.get("path", os.path.join(out_dir, "model.obj")),
            format=maybe_enum(Metashape, m.get("format", "ModelFormatOBJ"), Metashape.ModelFormatOBJ),
            texture_format=maybe_enum(Metashape, m.get("texture_format", "ImageFormatJPEG"), Metashape.ImageFormatJPEG),
            save_texture=bool(m.get("save_texture", True)),
            save_uv=bool(m.get("save_uv", True)),
            save_normals=bool(m.get("save_normals", True)),
            save_colors=bool(m.get("save_colors", True)),
            binary=bool(m.get("binary", True)),
        )