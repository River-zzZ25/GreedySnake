@echo off
rem Launch greedy snake (step 1 UI preview). Keep this file ASCII-only.
setlocal
set "PYTHONPATH=%~dp0..\src"
python -m greedy_snake %*
endlocal
