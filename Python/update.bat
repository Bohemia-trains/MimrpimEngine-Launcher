@echo off
setlocal enableDelayedExpansion

REM Ziskame ASCII znak ESC (27)
for /f "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
  set "ESC=%%b"
)

REM Barevne kody (text) - podle Launcher.py
set "RESET=%ESC%[0m"
set "RED=%ESC%[31m"      REM Pro chyby
set "GREEN=%ESC%[32m"    REM Pro uspesne operace, dokonceni
set "YELLOW=%ESC%[33m"   REM Pro varovani, uzivatelsky vstup, dulezite informace
set "BLUE=%ESC%[34m"     REM Pro obecne informace, uvodni zpravy
set "CYAN=%ESC%[36m"     REM Pro debugovaci zpravy
set "GREY=%ESC%[90m"     REM Pro mene dulezite, "tiche" zpravy

echo %BLUE%--- Spoustim update.bat ---%RESET%
set "GAME_PATH=%~1"
set "PLATFORM_VERSION=%~2"

echo %BLUE%Kontroluji, zda je k dispozici rar.exe...%RESET%
where rar.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%Chyba: rar.exe nebyl nalezen. Ujistete se, ze je v PATH nebo ve stejnem adresari jako tento skript.%RESET%
    goto :eof
)
echo %GREEN%rar.exe nalezeno.%RESET%

echo %BLUE%Pripravuji aktualizacni slozky...%RESET%
rmdir /s /q update >nul 2>&1
md update
echo %BLUE%Odstranuji predchozi instalaci hry z "%GAME_PATH%"...%RESET%
rmdir /s /q "%GAME_PATH%" >nul 2>&1

echo %BLUE%Rozbaluji launcher.rar do docasne slozky...%RESET%
color 01
rar.exe x download\launcher.rar update\
color 07
echo %BLUE%Odstranuji stahovaci slozku "download"...%RESET%
rmdir download /s /q >nul 2>&1

echo %BLUE%Kopiruji soubory verze "%PLATFORM_VERSION%" do "%GAME_PATH%"...%RESET%
xcopy "update\%PLATFORM_VERSION%" "%GAME_PATH%" /E /H /K /Y /I

echo %BLUE%Odstranuji docasnou aktualizacni slozku "update"...%RESET%
rmdir update /s /q >nul 2>&1

echo %BLUE%Měním pracovní adresář na "%GAME_PATH%"...%RESET%
cd "%GAME_PATH%"

echo %BLUE%Vytvarim spousteci soubor run.bat...%RESET%
cd %1
echo start MimrpimEngine.exe>run.bat

echo %GREEN%Aktualizace dokoncena. Program je pripraven ke spusteni.%RESET%
