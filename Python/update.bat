@echo off
set "GAME_PATH=%~1"
set "PLATFORM_VERSION=%~2"
where rar.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo Chyba: rar.exe nebyl nalezen. Ujistěte se, že je v PATH nebo ve stejném adresáři jako tento skript.
    goto :eof
)
rmdir /s /q update
md update
rmdir /s /q "%GAME_PATH%"
rar.exe x download\launcher.rar update\
rmdir download /s /q
xcopy "update\%PLATFORM_VERSION%" "%GAME_PATH%" /E /H /K /Y /I
rmdir update /s /q
cd "%GAME_PATH%"
echo start MimrpimEngine.exe>run.bat
