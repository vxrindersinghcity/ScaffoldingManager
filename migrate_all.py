#!/usr/bin/env python3
"""
Khalsa Scaffolding Manager - Complete Database Migration Script
Combines all migrations into one comprehensive script:
- Creates all tables if they don't exist
- Adds missing columns to existing tables
- Safe to run multiple times
- Creates automatic backups before making changes
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def print_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_step(message, status="INFO"):
    """Print a formatted step message"""
    symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "ADD": "➕",
        "CHECK": "🔍"
    }
    symbol = symbols.get(status, "•")
    print(f"{symbol} {message}")

def create_backup():
    """Create a backup of the database before migration"""
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        try:
            shutil.copy2(DB_PATH, backup_path)
            print_step(f"Backup created: {backup_path}", "SUCCESS")
            return True
        except Exception as e:
            print_step(f"Could not create backup: {e}", "WARNING")
            return False
    else:
        print_step("No existing database found - will create new one", "INFO")
        return True

def init_database(cursor):
    """Initialize all tables with complete structure"""
    print_header("DATABASE INITIALIZATION")
    
    tables_created = []
    
    # Invoices table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
    if not cursor.fetchone():
        print_step("Creating 'invoices' table...", "ADD")
        cursor.execute('''
            CREATE TABLE invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoiceNumber TEXT UNIQUE NOT NULL,
                clientName TEXT NOT NULL,
                clientAddress TEXT,
                clientPhone TEXT,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                items TEXT NOT NULL,
                subtotal REAL,
                vat REAL,
                vatApplied BOOLEAN DEFAULT 1,
                total REAL,
                notes TEXT,
                linkedJobId INTEGER,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        tables_created.append('invoices')
    else:
        print_step("Table 'invoices' already exists", "CHECK")
    
    # Inquiries table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inquiries'")
    if not cursor.fetchone():
        print_step("Creating 'inquiries' table...", "ADD")
        cursor.execute('''
            CREATE TABLE inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                location TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                date TEXT NOT NULL,
                quoteAmount REAL,
                notes TEXT,
                linkedJobId INTEGER,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        tables_created.append('inquiries')
    else:
        print_step("Table 'inquiries' already exists", "CHECK")
    
    # Jobs table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    if not cursor.fetchone():
        print_step("Creating 'jobs' table...", "ADD")
        cursor.execute('''
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jobNumber TEXT UNIQUE NOT NULL,
                clientName TEXT NOT NULL,
                location TEXT NOT NULL,
                area TEXT,
                jobType TEXT,
                truck TEXT,
                driver TEXT,
                startDate TEXT,
                endDate TEXT,
                status TEXT DEFAULT 'pending',
                value REAL,
                linkedInvoiceId INTEGER,
                linkedInquiryId INTEGER,
                notes TEXT,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_dates ON jobs(startDate, endDate)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_area ON jobs(area)')
        
        tables_created.append('jobs')
    else:
        print_step("Table 'jobs' already exists", "CHECK")
    
    # Vehicles table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicles'")
    if not cursor.fetchone():
        print_step("Creating 'vehicles' table...", "ADD")
        cursor.execute('''
            CREATE TABLE vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration TEXT UNIQUE NOT NULL,
                vehicleType TEXT DEFAULT 'car',
                ownerName TEXT NOT NULL,
                insuranceName TEXT NOT NULL,
                motDue TEXT,
                taxDue TEXT NOT NULL,
                tachoDue TEXT,
                insuranceDue TEXT NOT NULL,
                maintenanceDue TEXT,
                motActioned BOOLEAN DEFAULT 0,
                taxActioned BOOLEAN DEFAULT 0,
                tachoActioned BOOLEAN DEFAULT 0,
                insuranceActioned BOOLEAN DEFAULT 0,
                maintenanceActioned BOOLEAN DEFAULT 0,
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        tables_created.append('vehicles')
    else:
        print_step("Table 'vehicles' already exists", "CHECK")
    
    if tables_created:
        print_step(f"Created {len(tables_created)} new tables: {', '.join(tables_created)}", "SUCCESS")
    else:
        print_step("All required tables already exist", "SUCCESS")
    
    return len(tables_created) > 0

def add_missing_columns(cursor):
    """Add any missing columns to existing tables"""
    print_header("CHECKING FOR MISSING COLUMNS")
    
    changes_made = False
    
    # Define expected columns for each table
    expected_columns = {
        'invoices': [
            ('vatApplied', 'BOOLEAN DEFAULT 1'),
            ('linkedJobId', 'INTEGER')
        ],
        'inquiries': [
            ('linkedJobId', 'INTEGER')
        ],
        'jobs': [
            ('area', 'TEXT'),
            ('truck', 'TEXT'),
            ('driver', 'TEXT'),
            ('linkedInvoiceId', 'INTEGER'),
            ('linkedInquiryId', 'INTEGER'),
            ('updatedAt', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ],
        'vehicles': [
            ('motActioned', 'BOOLEAN DEFAULT 0'),
            ('taxActioned', 'BOOLEAN DEFAULT 0'),
            ('tachoActioned', 'BOOLEAN DEFAULT 0'),
            ('insuranceActioned', 'BOOLEAN DEFAULT 0'),
            ('maintenanceActioned', 'BOOLEAN DEFAULT 0')
        ]
    }
    
    for table_name, columns in expected_columns.items():
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print_step(f"Skipping '{table_name}' - table doesn't exist yet", "WARNING")
            continue
        
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add missing columns
        for col_name, col_type in columns:
            if col_name not in existing_columns:
                print_step(f"Adding '{col_name}' to '{table_name}' table...", "ADD")
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
                changes_made = True
            else:
                print_step(f"Column '{table_name}.{col_name}' already exists", "CHECK")
    
    if changes_made:
        print_step("Successfully added missing columns", "SUCCESS")
    else:
        print_step("All columns are up to date", "SUCCESS")
    
    return changes_made

def verify_database(cursor):
    """Verify database structure and show statistics"""
    print_header("DATABASE VERIFICATION")
    
    # Check all tables
    required_tables = ['invoices', 'inquiries', 'jobs', 'vehicles']
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    all_present = all(table in existing_tables for table in required_tables)
    
    if all_present:
        print_step("All required tables present", "SUCCESS")
    else:
        missing = [t for t in required_tables if t not in existing_tables]
        print_step(f"Missing tables: {', '.join(missing)}", "ERROR")
        return False
    
    # Show record counts
    print("\n📊 Record Counts:")
    for table in required_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   • {table.capitalize()}: {count}")
    
    # Check critical columns
    print("\n🔍 Column Verification:")
    
    critical_checks = [
        ('invoices', 'vatApplied'),
        ('invoices', 'linkedJobId'),
        ('inquiries', 'linkedJobId'),
        ('jobs', 'truck'),
        ('jobs', 'driver'),
        ('jobs', 'area'),
        ('jobs', 'linkedInvoiceId'),
        ('jobs', 'linkedInquiryId'),
        ('vehicles', 'motActioned')
    ]
    
    all_columns_ok = True
    for table, column in critical_checks:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if column in columns:
            print(f"   ✓ {table}.{column}")
        else:
            print(f"   ✗ {table}.{column} - MISSING")
            all_columns_ok = False
    
    return all_present and all_columns_ok

def migrate_database():
    """Main migration function"""
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  KHALSA SCAFFOLDING - DATABASE MIGRATION".center(68) + "║")
    print("║" + "  All-in-One Migration Script".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"\n📂 Database Location: {DB_PATH}")
    
    # Create backup
    if not create_backup():
        response = input("\n⚠️  Continue without backup? (yes/no): ").lower().strip()
        if response != 'yes':
            print("\n❌ Migration cancelled by user")
            return False
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        changes_made = False
        
        # Initialize tables
        if init_database(cursor):
            changes_made = True
        
        # Add missing columns
        if add_missing_columns(cursor):
            changes_made = True
        
        # Commit changes
        if changes_made:
            conn.commit()
            print_header("CHANGES COMMITTED")
            print_step("All changes saved to database", "SUCCESS")
        else:
            print_header("NO CHANGES NEEDED")
            print_step("Database is already up to date", "SUCCESS")
        
        # Verify database
        if verify_database(cursor):
            print_header("✅ MIGRATION COMPLETED SUCCESSFULLY")
            print("\n🎉 Your database is fully configured with all features:")
            print("   • Invoices with optional VAT")
            print("   • Inquiries management")
            print("   • Jobs tracking with truck/driver assignment")
            print("   • Vehicle management with reminders")
            print("   • Cross-linking between invoices, jobs, and inquiries")
            print("   • Area-based job organization")
            print("\n📝 Next Steps:")
            print("   1. Run START_MANAGER.bat (or 'python scaffolding_manager.py')")
            print("   2. Access the dashboard at http://127.0.0.1:5000")
            print("   3. Start managing your scaffolding business!")
            return True
        else:
            print_header("⚠️ VERIFICATION FAILED")
            print("\n❌ Database structure is incomplete")
            print("   Please check the error messages above")
            print("   You may need to delete the database and run this script again")
            return False
        
    except sqlite3.Error as e:
        print_header("❌ DATABASE ERROR")
        print_step(f"SQLite error: {e}", "ERROR")
        conn.rollback()
        return False
    
    except Exception as e:
        print_header("❌ UNEXPECTED ERROR")
        print_step(f"Error: {e}", "ERROR")
        if 'conn' in locals():
            conn.rollback()
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Entry point"""
    try:
        success = migrate_database()
        
        print("\n" + "=" * 70)
        
        if success:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration encountered issues")
            print("   Check the messages above for details")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        print("=" * 70)
    
    finally:
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
