@echo off
title Mazani obsahu slozky

echo Toto smaze VSECHNY SOUBORY a SLOZKY v aktualnim adresari.
echo UJISTETE SE, ZE JSTE VE SPRAVNE SLOZCE!

REM Smazat vsechny soubory KROMĚ samotného uninstall.bat
REM Vytvorime si docasny soubor se seznamem vsech souboru
dir /b /a-d *.* > %TEMP%\filelist.txt

REM Smazeme soubory ze seznamu, ale vynechame tento skript
for /F "delims=" %%A in (%TEMP%\filelist.txt) do (
    if /I not "%%A"=="%~nx0" ( 
        echo Mazani souboru: "%%A"
        del /q /f "%%A"
    )
)
del /q /f %TEMP%\filelist.txt 


REM Projde vsechny podslozky a smaze je i s jejich obsahem
for /D %%i in (*) do (
    echo Mazani slozky: "%%i"
    rmdir /s /q "%%i"
)
del /f /q "C:/Users/%username%/Train game Launcher.ink"
rmdir /q /s "C:\Users\mimrp\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Train-Game"
echo Hotovo.
del /q /f *.*