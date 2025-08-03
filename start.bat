@echo off
choice /c an /m "Force update?"
if %errorlevel% == 1 (
force_update.exe
)
python Launcher.py