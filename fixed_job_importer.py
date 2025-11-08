#!/usr/bin/env python3
"""
COMPLETE: Import ALL Jobs from ALL CSV files
Run this from the folder containing your CSV files
"""

import sqlite3
import os
import csv
from datetime import datetime
from collections import defaultdict

DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def parse_date(date_str):
    """Parse various date formats to YYYY-MM-DD"""
    if not date_str or date_str == '0' or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    # Try various date formats
    formats = [
        '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d',
        '%m/%d/%Y', '%d/%m/%Y'
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%Y-%m-%d')
        except:
            continue
    
    # Handle "26-Nov" format
    try:
        if '-' in date_str and len(date_str.split('-')) == 2:
            parts = date_str.split('-')
            if parts[1].isalpha():
                month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                           'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
                day = int(parts[0])
                month = month_map.get(parts[1].lower()[:3], 11)
                return f"2024-{month:02d}-{day:02d}"
    except:
        pass
    
    # Handle "Apr-25" format
    try:
        if '-' in date_str:
            parts = date_str.split('-')
            if parts[0].isalpha() and len(parts[1]) == 2:
                month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                           'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
                month = month_map.get(parts[0].lower()[:3], 4)
                year = 2000 + int(parts[1])
                return f"{year}-{month:02d}-01"
    except:
        pass
    
    return None

def map_status(status_str):
    """Map status from CSV to database status"""
    if not status_str:
        return 'pending'
    status = status_str.lower().strip()
    if status in ['removed', 'completed']:
        return 'completed'
    elif status in ['done', 'active', 'start', 'ok']:
        return 'active'
    else:
        return 'pending'

def generate_job_number(index, area):
    """Generate unique job number"""
    prefix_map = {
        'Peterborough': 'PB', 'Leicester': 'LC', 'London': 'LD',
        'Birmingham': 'BH', 'Luton': 'LT', 'Builders': 'BD'
    }
    prefix = prefix_map.get(area, 'JB')
    return f"{prefix}{str(index + 10000).zfill(6)}"

def find_csv_file(filename_patterns):
    """Find CSV file in current directory"""
    for pattern in filename_patterns:
        if os.path.exists(pattern):
            return pattern
    return None

def parse_peterborough_leicester_csv():
    """Parse Peterborough/Leicester/London CSV"""
    jobs = []
    csv_path = find_csv_file([
        'Khlasa Scaffolding Jobs (Peterbrough__Job_).csv',
        'Khlasa Scaffolding Jobs (Peterbrough Job).csv'
    ])
    
    if not csv_path:
        print(f"   ⚠️ Peterborough CSV not found")
        return jobs
    
    print(f"   ✓ Found: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            current_area = 'Peterborough'
            
            for i, row in enumerate(rows):
                if i < 2 or not row or len(row) < 6:
                    continue
                
                # Check for area markers
                line_text = ' '.join(str(cell).lower() for cell in row)
                if 'leicester' in line_text and len(row) < 6:
                    current_area = 'Leicester'
                    continue
                elif 'peterborough' in line_text and len(row) < 6:
                    current_area = 'Peterborough'
                    continue
                elif 'london' in line_text and len(row) < 6:
                    current_area = 'London'
                    continue
                
                try:
                    date_str = str(row[1]).strip() if len(row) > 1 else ''
                    job_type = str(row[2]).strip() if len(row) > 2 else ''
                    address = str(row[3]).strip() if len(row) > 3 else ''
                    price = str(row[4]).strip() if len(row) > 4 else '0'
                    status = str(row[5]).strip() if len(row) > 5 else ''
                    fitter = str(row[6]).strip() if len(row) > 6 else ''
                    
                    if not date_str or not address:
                        continue
                    
                    start_date = parse_date(date_str)
                    if not start_date:
                        continue
                    
                    try:
                        price_val = float(price.replace(',', '')) if price and price != '0' else 0
                    except:
                        price_val = 0
                    
                    jobs.append({
                        'date': start_date, 'jobType': job_type, 'address': address,
                        'area': current_area, 'price': price_val, 'status': map_status(status),
                        'fitter': fitter, 'truck': '', 'driver': '', 'time': None, 'finishDate': None
                    })
                except:
                    continue
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    return jobs

def parse_luton_csv():
    """Parse Luton CSV"""
    jobs = []
    csv_path = find_csv_file([
        'Khlasa Scaffolding Jobs (Luton_Job__(2)).csv',
        'Khlasa Scaffolding Jobs (Luton Job (2)).csv'
    ])
    
    if not csv_path:
        print(f"   ⚠️ Luton CSV not found")
        return jobs
    
    print(f"   ✓ Found: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            for i, row in enumerate(rows):
                if i < 2 or not row or len(row) < 6:
                    continue
                
                try:
                    date_str = str(row[0]).strip()
                    job_type = str(row[1]).strip() if len(row) > 1 else ''
                    address = str(row[2]).strip() if len(row) > 2 else ''
                    price = str(row[3]).strip() if len(row) > 3 else '0'
                    status = str(row[4]).strip() if len(row) > 4 else ''
                    fitter = str(row[5]).strip() if len(row) > 5 else ''
                    truck = str(row[6]).strip() if len(row) > 6 else ''
                    driver = str(row[7]).strip() if len(row) > 7 else ''
                    
                    if not date_str or not address or date_str.lower() == 'date':
                        continue
                    
                    start_date = parse_date(date_str)
                    if not start_date:
                        continue
                    
                    try:
                        price_val = float(price.replace(',', '')) if price and price != '0' else 0
                    except:
                        price_val = 0
                    
                    jobs.append({
                        'date': start_date, 'jobType': job_type, 'address': address,
                        'area': 'Luton', 'price': price_val, 'status': map_status(status),
                        'fitter': fitter, 'truck': truck, 'driver': driver, 'time': None, 'finishDate': None
                    })
                except:
                    continue
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    return jobs

def parse_birmingham_csv():
    """Parse Birmingham CSV"""
    jobs = []
    csv_path = find_csv_file([
        'Khlasa Scaffolding Jobs (Khalsa_Scaffolding_BHM).csv',
        'Khalsa_Scaffolding_BHM.csv'
    ])
    
    if not csv_path:
        print(f"   ⚠️ Birmingham CSV not found")
        return jobs
    
    print(f"   ✓ Found: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            for i, row in enumerate(rows):
                if i < 2 or not row or len(row) < 6:
                    continue
                
                try:
                    date_str = str(row[0]).strip()
                    job_type = str(row[1]).strip() if len(row) > 1 else ''
                    address = str(row[2]).strip() if len(row) > 2 else ''
                    price = str(row[3]).strip() if len(row) > 3 else '0'
                    status = str(row[6]).strip() if len(row) > 6 else ''
                    fitter = str(row[7]).strip() if len(row) > 7 else ''
                    truck = str(row[8]).strip() if len(row) > 8 else ''
                    driver = str(row[9]).strip() if len(row) > 9 else ''
                    
                    if not date_str or not address or date_str.lower() == 'date':
                        continue
                    
                    start_date = parse_date(date_str)
                    if not start_date:
                        continue
                    
                    try:
                        price_val = float(price.replace(',', '')) if price and price != '0' else 0
                    except:
                        price_val = 0
                    
                    jobs.append({
                        'date': start_date, 'jobType': job_type, 'address': address,
                        'area': 'Birmingham', 'price': price_val, 'status': map_status(status),
                        'fitter': fitter, 'truck': truck, 'driver': driver, 'time': None, 'finishDate': None
                    })
                except:
                    continue
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    return jobs

def parse_builder_jobs_csv():
    """Parse Builder jobs CSV"""
    jobs = []
    csv_path = find_csv_file([
        'Khlasa Scaffolding Jobs (Builders_Job__(3)).csv',
        'Khlasa Scaffolding Jobs (Builders Job (3)).csv'
    ])
    
    if not csv_path:
        print(f"   ⚠️ Builders CSV not found")
        return jobs
    
    print(f"   ✓ Found: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            for i in range(2, len(rows)):
                row = rows[i]
                if len(row) < 6:
                    continue
                
                try:
                    date_str = str(row[0]).strip()
                    job_type = str(row[1]).strip() if len(row) > 1 else ''
                    builder = str(row[2]).strip() if len(row) > 2 else ''
                    phone = str(row[3]).strip() if len(row) > 3 else ''
                    address = str(row[4]).strip() if len(row) > 4 else ''
                    price = str(row[5]).strip() if len(row) > 5 else '0'
                    status = str(row[10]).strip() if len(row) > 10 else 'pending'
                    fitter = str(row[11]).strip() if len(row) > 11 else ''
                    time_weeks = str(row[12]).strip() if len(row) > 12 else ''
                    finish_date = str(row[13]).strip() if len(row) > 13 else ''
                    truck = str(row[14]).strip() if len(row) > 14 else ''
                    driver = str(row[15]).strip() if len(row) > 15 else ''
                    
                    if not date_str or not address:
                        continue
                    
                    start_date = parse_date(date_str)
                    if not start_date:
                        continue
                    
                    end_date = parse_date(finish_date) if finish_date else None
                    
                    try:
                        price_str = price.replace('+vat', '').replace('ok', '1000').strip()
                        price_val = float(price_str) if price_str and price_str.replace('.', '').isdigit() else 0
                    except:
                        price_val = 0
                    
                    jobs.append({
                        'date': start_date, 'jobType': job_type, 'address': address,
                        'area': 'Builders', 'price': price_val, 'status': map_status(status),
                        'fitter': fitter, 'truck': truck, 'driver': driver,
                        'time': time_weeks if time_weeks and time_weeks != '0' else None,
                        'finishDate': end_date, 'builder': builder, 'phone': phone
                    })
                except:
                    continue
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    return jobs

def create_job_key(job):
    """Create unique key for deduplication"""
    address = job['address'].lower().strip().replace('  ', ' ').replace(',', '').strip()
    return f"{job['date']}_{address}"

def merge_jobs(jobs):
    """Merge duplicate jobs intelligently"""
    job_dict = defaultdict(list)
    
    for job in jobs:
        key = create_job_key(job)
        job_dict[key].append(job)
    
    merged_jobs = []
    for key, job_list in job_dict.items():
        if len(job_list) == 1:
            merged_jobs.append(job_list[0])
        else:
            # Merge multiple jobs
            merged = job_list[0].copy()
            for job in job_list[1:]:
                # Keep non-empty values
                for field in ['truck', 'driver', 'fitter', 'time', 'finishDate', 'builder', 'phone']:
                    if field in job and job[field] and not merged.get(field):
                        merged[field] = job[field]
                # Keep higher price
                if job['price'] > merged['price']:
                    merged['price'] = job['price']
                # Keep more complete status
                if job['status'] != 'pending' and merged['status'] == 'pending':
                    merged['status'] = job['status']
            merged_jobs.append(merged)
    
    print(f"   ℹ️ Merged {len(jobs)} jobs into {len(merged_jobs)} unique jobs")
    return merged_jobs

def import_jobs():
    """Main import function"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    print("=" * 70)
    print("  COMPLETE JOB IMPORT FROM ALL CSV FILES")
    print("=" * 70)
    print()
    print(f"📂 Database: {DB_PATH}")
    print(f"📂 Current directory: {os.getcwd()}")
    print()
    
    # List CSV files
    csv_files = [f for f in os.listdir(os.getcwd()) if f.endswith('.csv')]
    print("📋 CSV files found:")
    for f in csv_files:
        print(f"   • {f}")
    print()
    
    # Parse all jobs
    print("📋 Parsing all CSV files...")
    all_jobs = []
    
    all_jobs.extend(parse_peterborough_leicester_csv())
    all_jobs.extend(parse_luton_csv())
    all_jobs.extend(parse_birmingham_csv())
    all_jobs.extend(parse_builder_jobs_csv())
    
    print()
    print(f"📊 Total jobs found: {len(all_jobs)}")
    print()
    
    # Merge duplicates
    print("🔄 Merging duplicates...")
    all_jobs = merge_jobs(all_jobs)
    print()
    
    # Show breakdown
    area_counts = defaultdict(int)
    for job in all_jobs:
        area_counts[job['area']] += 1
    
    print("📊 Jobs by area (after deduplication):")
    for area, count in sorted(area_counts.items()):
        print(f"   • {area}: {count} jobs")
    print()
    
    # Confirm
    response = input("Import these jobs? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Import cancelled")
        return
    
    # Import
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT jobNumber, location, startDate FROM jobs")
    existing = cursor.fetchall()
    existing_keys = {f"{row[2]}_{row[1].lower().strip()}": row[0] for row in existing}
    
    imported, updated, skipped = 0, 0, 0
    
    print("\n📥 Importing jobs...")
    
    for i, job in enumerate(all_jobs):
        job_key = create_job_key(job)
        client_name = f"Client at {job['address'][:40]}..."
        
        # Create notes
        notes_parts = []
        if job.get('fitter'):
            notes_parts.append(f"Fitter: {job['fitter']}")
        if job.get('driver'):
            notes_parts.append(f"Driver: {job['driver']}")
        if job.get('time'):
            notes_parts.append(f"Duration: {job['time']} weeks")
        if job.get('builder'):
            notes_parts.append(f"Builder: {job['builder']}")
        if job.get('phone'):
            notes_parts.append(f"Phone: {job['phone']}")
        notes = ' | '.join(notes_parts) if notes_parts else None
        
        try:
            if job_key in existing_keys:
                job_number = existing_keys[job_key]
                cursor.execute('''
                    UPDATE jobs 
                    SET truck = COALESCE(NULLIF(?, ''), truck),
                        driver = COALESCE(NULLIF(?, ''), driver),
                        endDate = COALESCE(?, endDate),
                        value = CASE WHEN ? > COALESCE(value, 0) THEN ? ELSE value END,
                        notes = COALESCE(?, notes),
                        status = CASE WHEN ? != 'pending' THEN ? ELSE status END,
                        updatedAt = CURRENT_TIMESTAMP
                    WHERE jobNumber = ?
                ''', (job.get('truck', ''), job.get('driver', ''), job.get('finishDate'),
                      job['price'], job['price'], notes, job['status'], job['status'], job_number))
                updated += 1
            else:
                job_number = generate_job_number(i, job['area'])
                cursor.execute('''
                    INSERT INTO jobs (
                        jobNumber, clientName, location, area, jobType,
                        truck, driver, startDate, endDate, status, value, notes,
                        createdAt, updatedAt
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', (job_number, client_name, job['address'], job['area'], job['jobType'],
                      job.get('truck', ''), job.get('driver', ''), job['date'],
                      job.get('finishDate'), job['status'], job['price'], notes))
                imported += 1
            
            if (imported + updated) % 100 == 0:
                conn.commit()
                print(f"   ✓ Processed {imported + updated} jobs...")
        except Exception as e:
            skipped += 1
            continue
    
    conn.commit()
    conn.close()
    
    print()
    print("=" * 70)
    print(f"✅ Import complete!")
    print(f"   • New jobs: {imported}")
    print(f"   • Updated: {updated}")
    if skipped > 0:
        print(f"   • Skipped: {skipped}")
    print()
    for area, count in sorted(area_counts.items()):
        print(f"   • {area}: {count} jobs")
    print("=" * 70)
    print()

if __name__ == '__main__':
    import_jobs()
    input("Press Enter to exit...")