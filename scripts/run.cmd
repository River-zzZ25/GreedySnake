@echo off
rem Launch greedy snake (graphical window). Keep this file ASCII-only.
setlocal
set "PYTHONPATH=%~dp0..\src"
python -m greedy_snake %*
endlocal
