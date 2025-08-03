 @echo off
rmdir /s /q update
md update
rmdir /s /q "%1"
rar.exe x download\launcher.rar update\
rmdir download /s /q
set /p dir=jakej OS (Win/Linux/LinuxARM?
set /p dir2=Jaká architektura? (pro Win 64/32/ARM pro Linux 64/ARM32/ARM64
xcopy "update/%dir%%dir2%" "%1" /E /H /K /Y /I
echo start MimrpimEngine.exe>"%1/run.bat"