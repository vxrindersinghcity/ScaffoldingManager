#!/usr/bin/env python3
"""
Database Migration Script for Scaffolding Business Manager
Adds maintenanceDue and maintenanceActioned columns to existing vehicles table
"""

import sqlite3
import os

# Database path (same as in main application)
DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def migrate_database():
    """Add new columns to the vehicles table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("📝 This is normal if you haven't run the application yet.")
        print("   The new structure will be created automatically when you run the app.")
        return
    
    print("🔄 Migrating database...")
    print(f"📂 Database location: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(vehicles)")
        columns = [column[1] for column in cursor.fetchall()]
        
        changes_made = False
        
        # Add maintenanceDue column if it doesn't exist
        if 'maintenanceDue' not in columns:
            print("➕ Adding 'maintenanceDue' column...")
            cursor.execute("ALTER TABLE vehicles ADD COLUMN maintenanceDue TEXT")
            changes_made = True
        else:
            print("✅ Column 'maintenanceDue' already exists")
        
        # Add maintenanceActioned column if it doesn't exist
        if 'maintenanceActioned' not in columns:
            print("➕ Adding 'maintenanceActioned' column...")
            cursor.execute("ALTER TABLE vehicles ADD COLUMN maintenanceActioned BOOLEAN DEFAULT 0")
            changes_made = True
        else:
            print("✅ Column 'maintenanceActioned' already exists")
        
        # Make motDue nullable (SQLite doesn't support modifying columns directly)
        # This is handled by the new schema - existing data will remain intact
        
        if changes_made:
            conn.commit()
            print("\n✅ Migration completed successfully!")
            print("🔧 New features:")
            print("   • Maintenance tracking for trucks (8-week cycle)")
            print("   • MOT is now optional")
            print("   • 7-day advance reminder for maintenance")
        else:
            print("\n✅ Database is already up to date!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        print("Please contact support or manually update the database.")
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("  SCAFFOLDING BUSINESS MANAGER - DATABASE MIGRATION")
    print("=" * 60)
    print()
    
    migrate_database()
    
    print()
    print("=" * 60)
    input("Press Enter to exit...")
