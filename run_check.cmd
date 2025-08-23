@echo off
cd /d C:\Users\ygenk\Desktop\TMCloud
python run_diagnosis.py
if exist diagnosis_output.txt (
    echo === Result ===
    type diagnosis_output.txt
)