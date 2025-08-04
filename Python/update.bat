 @echo off
rmdir /s /q update
md update
rmdir /s /q "%1"
rar.exe x download\launcher.rar update\
rmdir download /s /q
xcopy "update/%2" "%1" /E /H /K /Y /I
echo start MimrpimEngine.exe>"%1/run.bat"
rmdir update /s /q