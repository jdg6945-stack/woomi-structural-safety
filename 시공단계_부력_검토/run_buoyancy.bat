@echo off
cd /d "%~dp0"
title 공사중 부력검토 실행기
echo 시스템을 시작합니다...
streamlit run buoyancy_app.py
pause