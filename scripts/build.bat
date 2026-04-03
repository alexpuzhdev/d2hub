@echo off
echo Building D2Hub...
pip install pyinstaller
pyinstaller d2hub.spec --clean
echo Done! Executable at dist\D2Hub.exe
pause
