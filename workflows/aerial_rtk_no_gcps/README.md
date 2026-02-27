# Aerial RTK (no GCPs)

Use when you have good RTK/PPK camera positions and want DEM + orthomosaic quickly.

## Run
- GUI: Tools → Run Script… → `workflows/aerial_rtk_no_gcps/run.py`
- Headless: `metashape.exe -r workflows/aerial_rtk_no_gcps/run.py` :contentReference[oaicite:13]{index=13}

## Edit
Update `config.json` → `input.photo_dirs` and CRS (`crs_epsg`).