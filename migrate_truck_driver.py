#!/usr/bin/env python3
"""
Database Migration Script
Adds truck and driver columns to jobs table
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def migrate_database():
    """Add truck and driver columns to jobs table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("Please run the main application first to create the database.")
        return
    
    print("=" * 60)
    print("  DATABASE MIGRATION - ADD TRUCK & DRIVER FIELDS")
    print("=" * 60)
    print()
    print(f"📂 Database: {DB_PATH}")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    changes_made = False
    
    try:
        # Check jobs table
        cursor.execute("PRAGMA table_info(jobs)")
        job_columns = [col[1] for col in cursor.fetchall()]
        
        if 'truck' not in job_columns:
            print("➕ Adding 'truck' column to jobs table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN truck TEXT")
            changes_made = True
        else:
            print("✅ jobs.truck already exists")
        
        if 'driver' not in job_columns:
            print("➕ Adding 'driver' column to jobs table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN driver TEXT")
            changes_made = True
        else:
            print("✅ jobs.driver already exists")
        
        if changes_made:
            conn.commit()
            print()
            print("=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print()
            print("New fields added:")
            print("  • truck - Store truck/vehicle information")
            print("  • driver - Store driver name")
            print()
        else:
            print()
            print("=" * 60)
            print("✅ Database is already up to date!")
            print("=" * 60)
            print()
        
    except Exception as e:
        conn.rollback()
        print()
        print(f"❌ Migration failed: {e}")
        print()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
    input("Press Enter to exit...")
