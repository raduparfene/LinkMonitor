@echo off
setlocal enabledelayedexpansion

:loop
py link_monitor.py

rem Check if the script exited due to an exception (non-zero exit code)
if %ERRORLEVEL% neq 0 (
    echo Python script exited with an error. Stopping batch execution.
    exit /b %ERRORLEVEL%
)

rem Generate a random number between 0 and 32767
set /a randnum=%RANDOM%

rem Scale the random number to the desired range (1800-5400 seconds, i.e., 30-90 minutes)
set /a delay=randnum %% 3601 + 1800

rem Display the delay
echo Waiting for !delay! seconds...

rem Wait for the calculated delay
timeout /t !delay!

goto loop