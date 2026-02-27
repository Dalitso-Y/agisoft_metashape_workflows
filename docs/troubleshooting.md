# Troubleshooting

## Script won’t run headless
Use `-r` and (on non-GUI systems) add `-platform offscreen` if required. :contentReference[oaicite:8]{index=8}

## Missing Python module inside Metashape
Install into Metashape’s bundled Python (not your system Python). :contentReference[oaicite:9]{index=9}

## CRS looks wrong
Use `EPSG::####` strings and ensure your reference/GCP coordinates match that CRS. :contentReference[oaicite:10]{index=10}