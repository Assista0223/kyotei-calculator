@echo off
echo Installing packages...
pip install -r requirements.txt
echo.
echo Starting application...
python main.py
pause