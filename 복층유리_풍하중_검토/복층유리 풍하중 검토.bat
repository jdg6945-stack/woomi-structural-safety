@echo off
cd /d "%~dp0"
echo 복층유리 풍하중 검토 프로그램을 실행합니다...
echo.
python -m streamlit run wind_app.py
