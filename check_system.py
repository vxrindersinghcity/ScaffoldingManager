#!/usr/bin/env python3
"""
Scaffolding Business Manager - System Status Checker
Checks if everything is set up correctly
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"✅ Python {version.major}.{version.minor}.{version.micro}"
    else:
        return False, f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)"

def check_packages():
    """Check required packages"""
    results = []
    try:
        import flask
        results.append(f"✅ Flask {flask.__version__}")
    except ImportError:
        results.append("❌ Flask not installed")
    
    try:
        import flask_cors
        results.append(f"✅ Flask-CORS installed")
    except ImportError:
        results.append("❌ Flask-CORS not installed")
    
    return results

def check_database():
    """Check database status"""
    if not os.path.exists(DB_PATH):
        return False, "❌ Database not found"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['jobs', 'invoices', 'inquiries', 'vehicles']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            conn.close()
            return False, f"❌ Missing tables: {', '.join(missing_tables)}"
        
        # Check jobs table columns
        cursor.execute("PRAGMA table_info(jobs)")
        job_columns = [col[1] for col in cursor.fetchall()]
        
        required_cols = ['truck', 'driver', 'linkedInvoiceId', 'linkedInquiryId', 'area']
        missing_cols = [c for c in required_cols if c not in job_columns]
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM jobs")
        job_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inquiries")
        inquiry_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vehicles")
        vehicle_count = cursor.fetchone()[0]
        
        conn.close()
        
        if missing_cols:
            return False, f"⚠️ Missing columns: {', '.join(missing_cols)}"
        
        return True, {
            'jobs': job_count,
            'invoices': invoice_count,
            'inquiries': inquiry_count,
            'vehicles': vehicle_count
        }
    except Exception as e:
        return False, f"❌ Database error: {e}"

def main():
    print("=" * 70)
    print("  SCAFFOLDING BUSINESS MANAGER - SYSTEM STATUS CHECK")
    print("=" * 70)
    print()
    
    # Check Python
    print("🐍 PYTHON VERSION")
    python_ok, python_msg = check_python()
    print(f"   {python_msg}")
    print()
    
    # Check Packages
    print("📦 REQUIRED PACKAGES")
    package_results = check_packages()
    for result in package_results:
        print(f"   {result}")
    print()
    
    # Check Database
    print("🗄️  DATABASE STATUS")
    print(f"   Location: {DB_PATH}")
    db_ok, db_info = check_database()
    
    if db_ok:
        print("   ✅ Database structure: Complete")
        print()
        print("   📊 Record Counts:")
        print(f"      • Jobs: {db_info['jobs']}")
        print(f"      • Invoices: {db_info['invoices']}")
        print(f"      • Inquiries: {db_info['inquiries']}")
        print(f"      • Vehicles: {db_info['vehicles']}")
    else:
        print(f"   {db_info}")
    
    print()
    print("=" * 70)
    
    # Summary
    all_ok = python_ok and all("✅" in r for r in package_results) and db_ok
    
    if all_ok:
        print("✅ SYSTEM STATUS: READY")
        print()
        print("Your system is fully set up and ready to use!")
        print("Run START_MANAGER.bat or 'python scaffolding_manager.py' to start.")
    else:
        print("⚠️ SYSTEM STATUS: SETUP REQUIRED")
        print()
        if not python_ok:
            print("❗ Install Python 3.8+ from https://www.python.org/")
        if not all("✅" in r for r in package_results):
            print("❗ Run: pip install Flask Flask-CORS")
        if not db_ok:
            print("❗ Run: SETUP_DATABASE.bat or python migrate_*.py scripts")
    
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
    input("Press Enter to exit...")
