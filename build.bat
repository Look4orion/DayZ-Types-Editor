@echo off
echo ========================================
echo DayZ Types Editor - Build Script
echo ========================================
echo.

REM Check if pyinstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Building executable...
echo This may take several minutes...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build with spec file
pyinstaller DayZTypesEditor.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo Executable location: dist\DayZTypesEditor.exe
echo.
echo You can distribute the entire "dist" folder
echo or just DayZTypesEditor.exe if using --onefile
echo.
pause
