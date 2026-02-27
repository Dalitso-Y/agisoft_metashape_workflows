# Installation / Setup

## Run scripts
You can run scripts:
- From Metashape GUI: Tools → Run Script…
- From command line using `-r` (headless supported). :contentReference[oaicite:6]{index=6}

## Installing external Python modules (optional)
Metashape ships its own Python. To install modules into that environment: :contentReference[oaicite:7]{index=7}

### Windows (run cmd as Administrator)
"%programfiles%\Agisoft\Metashape Pro\python\python.exe" -m pip install python_module_name

### macOS
/MetashapePro.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9 -m pip install python_module_name

### Linux
./metashape-pro/python/bin/python3.9 -m pip install python_module_name