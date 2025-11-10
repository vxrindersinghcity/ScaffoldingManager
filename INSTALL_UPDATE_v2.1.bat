@echo off
title Khalsa Scaffolding Manager - Version 2.1 Update Installer
color 0B

echo ====================================================================
echo       KHALSA SCAFFOLDING MANAGER - VERSION 2.1 UPDATE
echo ====================================================================
echo.
echo This script will:
echo   1. Install required Python packages (openpyxl)
echo   2. Update your database (add VAT feature)
echo   3. Guide you through file replacement
echo.
pause

echo.
echo ====================================================================
echo STEP 1: Installing Python Packages
echo ====================================================================
echo.
echo Installing openpyxl (required for Excel export)...
pip install openpyxl
if errorlevel 1 (
    echo.
    echo [WARNING] Package installation may have failed
    echo Please run manually: pip install openpyxl
    echo.
    pause
)

echo.
echo ====================================================================
echo STEP 2: Updating Database (Adding VAT Feature)
echo ====================================================================
echo.
if exist migrate_vat_feature.py (
    echo Running VAT migration script...
    python migrate_vat_feature.py
) else (
    echo [WARNING] migrate_vat_feature.py not found in current directory
    echo Please ensure you're running this from the correct folder
    echo.
)

echo.
echo ====================================================================
echo STEP 3: File Replacement Instructions
echo ====================================================================
echo.
echo IMPORTANT: You need to manually replace your HTML file!
echo.
echo 1. Find your current file:
echo    complete_scaffolding_dashboard.html
echo.
echo 2. Rename it to (for backup):
echo    complete_scaffolding_dashboard.html.old
echo.
echo 3. Rename the new file:
echo    complete_scaffolding_dashboard_fixed.html
echo    TO:
echo    complete_scaffolding_dashboard.html
echo.
echo ====================================================================
echo.

pause

echo.
echo ====================================================================
echo                     UPDATE INSTALLATION COMPLETE!
echo ====================================================================
echo.
echo New Features Available:
echo   ✓ Export invoices to Excel (click 📊 button)
echo   ✓ Optional VAT on invoices (checkbox in form)
echo   ✓ Quick job status updates (dropdown in table)
echo.
echo Next Steps:
echo   1. Complete the file replacement (see above)
echo   2. Run START_MANAGER.bat to start the application
echo   3. Test the new features!
echo.
echo For detailed information, read: UPDATE_README_v2.1.txt
echo.
echo ====================================================================
pause
