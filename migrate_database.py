#!/usr/bin/env python3
"""
Database Migration Script
Adds linkedInvoiceId and linkedInquiryId columns to jobs table
Adds linkedJobId columns to invoices and inquiries tables
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def migrate_database():
    """Add linking columns to all tables"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("Please run the main application first to create the database.")
        return
    
    print("=" * 60)
    print("  DATABASE MIGRATION - ADD LINKING COLUMNS")
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
        
        if 'linkedInvoiceId' not in job_columns:
            print("➕ Adding 'linkedInvoiceId' column to jobs table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN linkedInvoiceId INTEGER")
            changes_made = True
        else:
            print("✅ jobs.linkedInvoiceId already exists")
        
        if 'linkedInquiryId' not in job_columns:
            print("➕ Adding 'linkedInquiryId' column to jobs table...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN linkedInquiryId INTEGER")
            changes_made = True
        else:
            print("✅ jobs.linkedInquiryId already exists")
        
        # Check invoices table
        cursor.execute("PRAGMA table_info(invoices)")
        invoice_columns = [col[1] for col in cursor.fetchall()]
        
        if 'linkedJobId' not in invoice_columns:
            print("➕ Adding 'linkedJobId' column to invoices table...")
            cursor.execute("ALTER TABLE invoices ADD COLUMN linkedJobId INTEGER")
            changes_made = True
        else:
            print("✅ invoices.linkedJobId already exists")
        
        # Check inquiries table
        cursor.execute("PRAGMA table_info(inquiries)")
        inquiry_columns = [col[1] for col in cursor.fetchall()]
        
        if 'linkedJobId' not in inquiry_columns:
            print("➕ Adding 'linkedJobId' column to inquiries table...")
            cursor.execute("ALTER TABLE inquiries ADD COLUMN linkedJobId INTEGER")
            changes_made = True
        else:
            print("✅ inquiries.linkedJobId already exists")
        
        if changes_made:
            conn.commit()
            print()
            print("=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print()
            print("You can now link:")
            print("  • Jobs ↔ Invoices")
            print("  • Jobs ↔ Inquiries")
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