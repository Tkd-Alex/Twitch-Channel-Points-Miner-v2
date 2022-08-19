@echo off

SET arg1=%1
ECHO Your name is: %arg1%

START firefox.exe "https://www.twitch.tv/%arg1%"
ECHO firefox lancé

TIMEOUT /T 4

@REM TASKKILL /f /t /im firefox.exe