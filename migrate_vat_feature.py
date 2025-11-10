#!/usr/bin/env python3
"""
Migration Script - Add vatApplied column for optional VAT feature
Safe to run multiple times - checks if column already exists
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def migrate_invoices():
    """Add vatApplied column to invoices table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("The app will create it automatically on first run.")
        return False
    
    print("=" * 70)
    print("  INVOICES TABLE - ADD VAT OPTIONAL FEATURE")
    print("=" * 70)
    print()
    print(f"📁 Database: {DB_PATH}")
    print()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(invoices)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'vatApplied' in columns:
            print("✅ vatApplied column already exists")
            print("   (Database is already up to date)")
            conn.close()
            return True
        
        print("➕ Adding 'vatApplied' column to invoices table...")
        print("   This allows marking whether VAT was applied to each invoice")
        print()
        
        # Add column with default value of TRUE (maintains backward compatibility)
        cursor.execute("ALTER TABLE invoices ADD COLUMN vatApplied BOOLEAN DEFAULT 1")
        
        conn.commit()
        
        print("=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("✨ New Feature Now Available:")
        print("   • Create invoices with optional VAT")
        print("   • Choose whether to apply 20% VAT")
        print("   • Existing invoices treated as having VAT applied")
        print()
        
        # Count invoices
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        
        if invoice_count > 0:
            print(f"📊 Updated {invoice_count} existing invoices")
            print("   All existing invoices: VAT applied = TRUE (backward compatible)")
        
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        print()
        print(f"❌ MIGRATION FAILED: {e}")
        print()
        conn.close()
        return False
    finally:
        conn.close()

def create_backup():
    """Create a backup of the database before migration"""
    if os.path.exists(DB_PATH):
        backup_path = DB_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        try:
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            print(f"💾 Backup created: {backup_path}")
            print()
            return True
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
            print()
            return False
    return True

def main():
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  KHALSA SCAFFOLDING - DATABASE MIGRATION  ".center(68) + "║")
    print("║" + "  Optional VAT Feature for Invoices  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    # Create backup
    if create_backup():
        # Run migration
        if migrate_invoices():
            print()
            print("✅ Your application is ready to use!")
            print()
            print("Next Steps:")
            print("  1. Run START_MANAGER.bat (or python scaffolding_manager.py)")
            print("  2. Go to Invoices tab")
            print("  3. Create or edit an invoice")
            print("  4. You'll see the new 'Apply VAT (20%)' checkbox")
            print()
        else:
            print()
            print("⚠️  Migration encountered an issue")
            print("    The application may still work, but the new feature is unavailable")
            print()
    else:
        print()
        print("⚠️  Could not create backup")
        print("    Run the migration anyway? (yes/no): ", end="")
        response = input().lower().strip()
        if response == 'yes':
            migrate_invoices()
    
    print()
    print("=" * 70)
    input("Press Enter to exit...")

if __name__ == '__main__':
    main()
