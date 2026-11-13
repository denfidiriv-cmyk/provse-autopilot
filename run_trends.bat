@echo off
rem Агент трендів PROВсе: запускається планувальником Windows, працює без LLM.
cd /d "%~dp0"
python run_trends.py >> out\trends_log.txt 2>&1
