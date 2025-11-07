#!/usr/bin/env python3
"""
Database Migration Script for Scaffolding Business Manager
Adds jobs table to existing database
"""

import sqlite3
import os
from datetime import datetime

# Database path (same as in main application)
DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def migrate_database():
    """Add jobs table to the database"""
    
    if not os.path.exists(DB_PATH):
        print(f"⚠️  Database not found at: {DB_PATH}")
        print("📝 The new structure will be created automatically when you run the app.")
        return
    
    print("🔄 Migrating database...")
    print(f"📂 Database location: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if jobs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
        jobs_table_exists = cursor.fetchone() is not None
        
        if not jobs_table_exists:
            print("➕ Creating 'jobs' table...")
            cursor.execute('''
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jobNumber TEXT UNIQUE NOT NULL,
                    clientName TEXT NOT NULL,
                    location TEXT NOT NULL,
                    jobType TEXT,
                    startDate TEXT,
                    endDate TEXT,
                    status TEXT DEFAULT 'pending',
                    value REAL,
                    invoiced BOOLEAN DEFAULT 0,
                    invoiceNumber TEXT,
                    workers TEXT,
                    scaffoldType TEXT,
                    height TEXT,
                    area TEXT,
                    notes TEXT,
                    paymentStatus TEXT DEFAULT 'pending',
                    paymentDate TEXT,
                    contactPerson TEXT,
                    contactPhone TEXT,
                    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster queries
            cursor.execute('CREATE INDEX idx_jobs_status ON jobs(status)')
            cursor.execute('CREATE INDEX idx_jobs_dates ON jobs(startDate, endDate)')
            
            print("✅ Jobs table created successfully!")
        else:
            print("✅ Jobs table already exists")
            
            # Check for missing columns and add them if needed
            cursor.execute("PRAGMA table_info(jobs)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            
            new_columns = [
                ('jobType', 'TEXT'),
                ('scaffoldType', 'TEXT'),
                ('height', 'TEXT'),
                ('area', 'TEXT'),
                ('contactPerson', 'TEXT'),
                ('contactPhone', 'TEXT'),
                ('paymentStatus', "TEXT DEFAULT 'pending'"),
                ('paymentDate', 'TEXT'),
                ('updatedAt', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    print(f"➕ Adding '{col_name}' column...")
                    cursor.execute(f"ALTER TABLE jobs ADD COLUMN {col_name} {col_type}")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("🔧 New features:")
        print("   • Jobs tracking with comprehensive details")
        print("   • Job status management (pending/active/completed/cancelled)")
        print("   • Payment tracking")
        print("   • Job filtering and search")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        print("Please contact support or manually update the database.")
    finally:
        conn.close()

def backup_database():
    """Create a backup of the database before migration"""
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        try:
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            print(f"📦 Backup created: {backup_path}")
            return True
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
            return False
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("  SCAFFOLDING BUSINESS MANAGER - JOBS TABLE MIGRATION")
    print("=" * 60)
    print()
    
    # Create backup first
    if backup_database():
        migrate_database()
    else:
        response = input("Continue without backup? (yes/no): ")
        if response.lower() == 'yes':
            migrate_database()
    
    print()
    print("=" * 60)
    input("Press Enter to exit...")
