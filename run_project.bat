@echo off
title Astronomy Telescope Cataloging - Windows 11 Launcher
color 0B

echo ==============================================================================
echo        ASTRONOMY TELESCOPE CATALOGING - WINDOWS 11 LAUNCHER
echo ==============================================================================
echo.

:: Detect Python command
set PY_CMD=
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PY_CMD=py
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PY_CMD=python
    ) else (
        echo [ERROR] Neither 'py' nor 'python' was found in your PATH.
        echo Please install Python 3.10+ from https://www.python.org/ or the Microsoft Store.
        echo Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )
)

echo Python launcher detected: %PY_CMD%
echo.

:MENU
echo ------------------------------------------------------------------------------
echo Choose an option to run:
echo   [1] Run Full Cataloging Pipeline (Ingestion, QC, Analytics, Charts, HTML)
echo   [2] Launch Desktop GUI Dashboard (Tkinter Native Desktop App)
echo   [3] Open Interactive HTML Dashboard in Web Browser
echo   [4] Run Automated Unit Tests (Verify All Modules)
echo   [5] Install / Verify Dependencies (pip install -r requirements.txt)
echo   [6] Exit
echo ------------------------------------------------------------------------------
set /p choice="Enter choice [1-6]: "

if "%choice%"=="1" goto RUN_PIPELINE
if "%choice%"=="2" goto RUN_GUI
if "%choice%"=="3" goto OPEN_HTML
if "%choice%"=="4" goto RUN_TESTS
if "%choice%"=="5" goto INSTALL_DEPS
if "%choice%"=="6" goto EXIT_PROMPT

echo Invalid choice. Please enter a number between 1 and 6.
echo.
goto MENU

:RUN_PIPELINE
echo.
echo Running full astronomical cataloging pipeline...
%PY_CMD% main.py --open-dashboard
echo.
pause
goto MENU

:RUN_GUI
echo.
echo Launching Tkinter Desktop GUI Dashboard...
%PY_CMD% main.py --gui
echo.
goto MENU

:OPEN_HTML
echo.
if exist "outputs\dashboard.html" (
    echo Opening HTML Dashboard in default browser...
    start outputs\dashboard.html
) else (
    echo [NOTICE] Dashboard not found yet. Running pipeline first...
    %PY_CMD% main.py
    start outputs\dashboard.html
)
echo.
pause
goto MENU

:RUN_TESTS
echo.
echo Running project unit test suite...
%PY_CMD% -m unittest tests/test_pipeline.py
echo.
pause
goto MENU

:INSTALL_DEPS
echo.
echo Installing dependencies from requirements.txt...
%PY_CMD% -m pip install -r requirements.txt
echo.
pause
goto MENU

:EXIT_PROMPT
echo.
echo Thank you for using Astronomy Telescope Cataloging!
exit /b 0
