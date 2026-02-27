# Runbook (QC + Reproducibility)

## Always record
- Metashape version
- workflow name + config.json
- CRS (EPSG::#### if used)
- processing settings (match/align/optimize/depth quality/filtering)

## Suggested QC gates (aerial)
- Aligned cameras: > 95% of photos (unless intended exclusions)
- Sparse tie points: sanity check (project-dependent)
- If using GCPs: check point errors and reject outliers before final products

## Suggested QC gates (turntable object scan)
- No obvious “double surfaces” or holes from masking errors
- Texture seams acceptable for your use-case

Outputs:
- `logs/<workflow>/<timestamp>.log`
- `output/<workflow>/...` (exports)