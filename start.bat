@echo off
setlocal
python "%~dp0manage.py" start dev %*
