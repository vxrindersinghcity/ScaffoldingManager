@echo off
title Scaffolding Manager - Database Setup
color 0B

echo ============================================================
echo       SCAFFOLDING BUSINESS MANAGER - SETUP WIZARD
echo ============================================================
echo.
echo This wizard will set up your database with all features.
echo.
pause

echo.
echo ============================================================
echo STEP 1: Creating/Updating Jobs Table
echo ============================================================
echo.
python migrate_jobs.py

echo.
echo ============================================================
echo STEP 2: Adding Linking Capability
echo ============================================================
echo.
python migrate_database.py

echo.
echo ============================================================
echo STEP 3: Adding Truck and Driver Fields
echo ============================================================
echo.
python migrate_truck_driver.py

echo.
echo ============================================================
echo.
echo                    SETUP COMPLETE!
echo ============================================================
echo.
echo Your database is now ready with all features:
echo   - Jobs tracking
echo   - Truck and Driver assignment
echo   - Invoice linking
echo   - Inquiry linking
echo.
echo Next steps:
echo   1. Run START_MANAGER.bat to start the application
echo   2. (Optional) Run import_jobs.py to add sample data
echo.
echo ============================================================
echo.
pause
