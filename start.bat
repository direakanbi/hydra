@echo off
set /p target="Enter the target URL to scan (e.g., http://example.com): "
.\venv\Scripts\python.exe hydra.py %target%
pause
