@echo off
cd Python
rmdir /s /q dist
rmdir /s /q build
choice /c AN /m "Je toto pc mimrpima? A/N: "
if %errorlevel%==1 (
"C:/users/mimrp/.venv/venv_launcher\Scripts\activate"
pyinstaller --onedir --hidden-import=numpy.core._multiarray_umath --hidden-import=numpy.core.umath --windowed --icon=icon.ico .\Launcher_gui.py
pyinstaller --onedir --icon=icon.ico .\Launcher.py
pyinstaller --onedir .\updater.py
)

pause
exit /b 0
