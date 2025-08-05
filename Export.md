# Export

**Potřeba nainstalovat všechny knihovny**

## Command pro export Launcher_gui

je potřeba mít na to python 310 a ve venv
pyinstaller --onedir --hidden-import=numpy.core._multiarray_umath --hidden-import=numpy.core.umath --windowed --icon=icon.ico .\Launcher_gui.py

## Command pro export Launcher

pyinstaller --onedir --icon=icon.ico .\Launcher.py

## Command pro export Updater

pyinstaller --onedir .\updater.py

Nebo použij Export.bat (Pro windows) nebo Export.sh (Pro linux)
**Potřeba nainstalovat PyInstaller (python -m pip install pyinstaller a na linuxu musíš do venv)**
