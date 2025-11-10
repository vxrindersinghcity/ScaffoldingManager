#!/usr/bin/env python3
"""
Scaffolding Business Manager v2 - With HTML Invoice Preview
Complete business management system with print-to-PDF invoice generation
"""

import sys
import os
import json
import sqlite3
import webbrowser
import threading
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database setup
DB_PATH = os.path.join(os.path.expanduser('~'), 'scaffolding_business.db')

def init_database():
    """Initialize SQLite database with all required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
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
    
    # Inquiries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquiries (
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
    
    # Vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
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
    
    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
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
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")

# API Routes - Invoices
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM invoices ORDER BY date DESC')
    invoices = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(invoices)

@app.route('/api/invoices', methods=['POST'])
def create_invoice():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Handle VAT application
        vat_applied = data.get('vatApplied', True)
        vat = data.get('vat', 0)
        if not vat_applied:
            vat = 0
        
        cursor.execute('''
            INSERT INTO invoices (invoiceNumber, clientName, clientAddress, clientPhone, 
                                date, status, items, subtotal, vat, vatApplied, total, notes, linkedJobId)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['invoiceNumber'], data['clientName'], data.get('clientAddress'),
            data.get('clientPhone'), data['date'], data['status'], data['items'],
            data['subtotal'], vat, vat_applied, data['total'], data.get('notes'),
            data.get('linkedJobId')
        ))
        conn.commit()
        invoice_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': invoice_id, 'message': 'Invoice created successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Invoice number already exists'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Error creating invoice: {str(e)}'}), 400

@app.route('/api/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Handle VAT application
    vat_applied = data.get('vatApplied', True)
    vat = data.get('vat', 0)
    if not vat_applied:
        vat = 0
    
    cursor.execute('''
        UPDATE invoices 
        SET invoiceNumber=?, clientName=?, clientAddress=?, clientPhone=?,
            date=?, status=?, items=?, subtotal=?, vat=?, vatApplied=?, total=?, notes=?, linkedJobId=?
        WHERE id=?
    ''', (
        data['invoiceNumber'], data['clientName'], data.get('clientAddress'),
        data.get('clientPhone'), data['date'], data['status'], data['items'],
        data['subtotal'], vat, vat_applied, data['total'], data.get('notes'), 
        data.get('linkedJobId'), invoice_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Invoice updated successfully'})

@app.route('/api/invoices/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM invoices WHERE id=?', (invoice_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Invoice deleted successfully'})

@app.route('/api/invoices/<int:invoice_id>/preview', methods=['GET'])
def preview_invoice(invoice_id):
    """Generate HTML invoice preview matching the Excel template design"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM invoices WHERE id=?', (invoice_id,))
        invoice_row = cursor.fetchone()
        conn.close()
        
        if not invoice_row:
            return jsonify({'error': 'Invoice not found'}), 404
        
        invoice = dict(invoice_row)
        items = json.loads(invoice['items'])
        
        # Format date as DD/MM/YYYY
        invoice_date = datetime.strptime(invoice['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        
        # Generate HTML invoice matching the template
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice {invoice['invoiceNumber']}</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Calibri', Arial, sans-serif;
            line-height: 1.3;
            color: #000;
            background: white;
            padding: 20px;
        }}
        
        .invoice-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
        }}
        
        .header {{
            margin-bottom: 20px;
        }}
        
        .company-name {{
            font-size: 28px;
            font-weight: bold;
            color: #2E5C8A;
            margin-bottom: 8px;
        }}
        
        .company-details {{
            font-size: 13px;
            line-height: 1.6;
            color: #000;
        }}
        
        .invoice-title {{
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 48px;
            font-weight: bold;
            color: #2E5C8A;
            letter-spacing: 2px;
        }}
        
        .invoice-info-grid {{
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 20px;
            margin: 30px 0;
        }}
        
        .info-box {{
            border: 2px solid #2E5C8A;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .info-header {{
            background: #2E5C8A;
            color: white;
            padding: 8px 12px;
            font-weight: bold;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
        }}
        
        .info-content {{
            padding: 12px;
            font-size: 13px;
            line-height: 1.8;
        }}
        
        .bill-to-content {{
            min-height: 120px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border: 2px solid #000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #2E5C8A;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: bold;
            font-size: 13px;
            border: 1px solid #000;
        }}
        
        td {{
            padding: 10px;
            border: 1px solid #000;
            font-size: 13px;
        }}
        
        .text-right {{
            text-align: right;
        }}
        
        .text-center {{
            text-align: center;
        }}
        
        .item-row td {{
            background: white;
        }}
        
        .empty-row td {{
            height: 30px;
        }}
        
        .footer-section {{
            margin-top: 30px;
        }}
        
        .thank-you {{
            font-size: 16px;
            font-style: italic;
            color: #2E5C8A;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .totals-table {{
            float: right;
            width: 320px;
            border: 2px solid #000;
            margin-top: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .totals-table td {{
            padding: 8px 12px;
            font-size: 14px;
        }}
        
        .total-label {{
            background: #D6E4F0;
            font-weight: bold;
        }}
        
        .total-amount {{
            text-align: right;
            font-weight: bold;
        }}
        
        .grand-total-label {{
            background: #2E5C8A;
            color: white;
            font-weight: bold;
            font-size: 15px;
        }}
        
        .grand-total-amount {{
            background: #D6E4F0;
            text-align: right;
            font-weight: bold;
            font-size: 15px;
        }}
        
        .bank-details {{
            clear: both;
            margin-top: 30px;
            font-size: 13px;
            line-height: 1.8;
        }}
        
        .bank-details div {{
            margin-bottom: 3px;
        }}
        
        .company-footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            line-height: 1.6;
        }}
        
        .contact-name {{
            font-weight: bold;
        }}
        
        @media print {{
            body {{
                padding: 0;
            }}
            
            .no-print {{
                display: none;
            }}
            
            .invoice-container {{
                max-width: 100%;
            }}
        }}
        
        .print-button {{
            position: fixed;
            top: 20px;
            left: 20px;
            padding: 12px 24px;
            background: #2E5C8A;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 1000;
        }}
        
        .print-button:hover {{
            background: #1e4d7a;
        }}
    </style>
</head>
<body>
    <button class="print-button no-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
    
    <div class="invoice-container">
        <div class="invoice-title">INVOICE</div>
        
        <div class="header">
            <div class="company-name">Khalsa Scaffolding LTD</div>
            <div class="company-details">
                <strong>66 Raynton Drive</strong><br>
                <strong>Hayes UB4 8BE</strong><br>
                <strong>Phone: 07741252013</strong>
            </div>
        </div>
        
        <div class="invoice-info-grid">
            <div class="info-box">
                <div class="info-header">BILL TO</div>
                <div class="info-content bill-to-content">
                    <strong>{invoice['clientName']}</strong><br>
'''
        
        if invoice.get('clientAddress'):
            html += f"                    {invoice['clientAddress']}<br>\n"
        
        html += '''
                </div>
            </div>
            
            <div class="info-box">
                <div class="info-header">
                    <span>INVOICE #</span>
                    <span>DATE</span>
                </div>
                <div class="info-content" style="display: flex; justify-content: space-between; align-items: center;">
'''
        
        html += f'''
                    <strong>{invoice['invoiceNumber']}</strong>
                    <strong>{invoice_date}</strong>
'''
        
        html += '''
                </div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th style="width: 8%; text-align: center;"></th>
                    <th style="width: 42%;">DESCRIPTION</th>
                    <th style="width: 10%; text-align: center;">QTY</th>
                    <th style="width: 20%; text-align: right;">UNIT PRICE</th>
                    <th style="width: 20%; text-align: right;">AMOUNT</th>
                </tr>
            </thead>
            <tbody>
'''
        
        # Add items
        for idx, item in enumerate(items, 1):
            quantity = float(item['quantity'])
            rate = float(item['rate'])
            amount = quantity * rate
            
            html += f'''
                <tr class="item-row">
                    <td class="text-center">{idx}</td>
                    <td>{item['description']}</td>
                    <td class="text-center">{quantity:g}</td>
                    <td class="text-right">{rate:,.2f}</td>
                    <td class="text-right">{amount:,.2f}</td>
                </tr>
'''
        
        # Add empty rows to match template (minimum 6 rows total)
        for _ in range(max(0, 6 - len(items))):
            html += '''
                <tr class="empty-row">
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
'''
        
        html += '''
            </tbody>
        </table>
        
        <div class="footer-section">
            <div class="thank-you">Thank you for your business!</div>
            
            <table class="totals-table">
'''
        
        subtotal = float(invoice['subtotal'])
        html += f'''
                <tr>
                    <td class="total-label">SUBTOTAL</td>
                    <td class="total-amount">{subtotal:,.2f}</td>
                </tr>
'''
        
        # Only show VAT if it's applied (vatApplied is True or 1)
        vat_applied = invoice.get('vatApplied')
        if vat_applied is True or vat_applied == 1:
            vat = float(invoice['vat'])
            html += f'''
                <tr>
                    <td class="total-label">TAX RATE</td>
                    <td class="total-amount">20%</td>
                </tr>
                <tr>
                    <td class="total-label">VAT</td>
                    <td class="total-amount">{vat:,.0f}</td>
                </tr>
'''
        else:
            html += '''
                <tr>
                    <td class="total-label" colspan="2" style="text-align: center; font-style: italic; color: #666;">VAT Exempt</td>
                </tr>
'''
        
        total = float(invoice['total'])
        html += f'''
                <tr>
                    <td class="grand-total-label">TOTAL</td>
                    <td class="grand-total-amount">{total:,.0f}</td>
                </tr>
            </table>
            
            <div class="bank-details">
                <div><strong>Bank name: Khalsa Scaffolding LTD</strong></div>
                <div><strong>Account number: 33189759</strong></div>
                <div><strong>Sort code: 20-42-76</strong></div>
            </div>
            
            <div class="company-footer">
                <strong>company number: 13490441 VAT:43747190</strong><br>
                If you have any questions about this invoice, please contact<br>
                <span class="contact-name">Jagtar Singh Brar, 07741252013</span>
            </div>
        </div>
    </div>
    
    <script>
        // Optionally auto-print on load
        // window.onload = function() {{ window.print(); }};
    </script>
</body>
</html>
'''
        
        return html
        
    except Exception as e:
        return jsonify({'error': f'Error generating invoice: {str(e)}'}), 500

# API Routes - Inquiries
@app.route('/api/inquiries', methods=['GET'])
def get_inquiries():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inquiries ORDER BY date DESC')
    inquiries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(inquiries)

@app.route('/api/inquiries', methods=['POST'])
def create_inquiry():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inquiries (name, phone, email, location, status, date, quoteAmount, notes, linkedJobId)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['phone'], data.get('email'), data['location'],
        data['status'], data['date'], data.get('quoteAmount'), data.get('notes'),
        data.get('linkedJobId')
    ))
    conn.commit()
    inquiry_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': inquiry_id, 'message': 'Inquiry created successfully'}), 201

@app.route('/api/inquiries/<int:inquiry_id>', methods=['PUT'])
def update_inquiry(inquiry_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE inquiries 
        SET name=?, phone=?, email=?, location=?, status=?, date=?, quoteAmount=?, notes=?, linkedJobId=?
        WHERE id=?
    ''', (
        data['name'], data['phone'], data.get('email'), data['location'],
        data['status'], data['date'], data.get('quoteAmount'), data.get('notes'),
        data.get('linkedJobId'), inquiry_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Inquiry updated successfully'})

@app.route('/api/inquiries/<int:inquiry_id>', methods=['DELETE'])
def delete_inquiry(inquiry_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inquiries WHERE id=?', (inquiry_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Inquiry deleted successfully'})

# API Routes - Jobs
@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY createdAt DESC')
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(jobs)

@app.route('/api/jobs', methods=['POST'])
def create_job():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO jobs (jobNumber, clientName, location, area, jobType, truck, driver, startDate, 
                            endDate, status, value, linkedInvoiceId, linkedInquiryId, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['jobNumber'], data['clientName'], data['location'], data.get('area'),
            data.get('jobType'), data.get('truck'), data.get('driver'), data.get('startDate'), data.get('endDate'),
            data.get('status', 'pending'), data.get('value'), data.get('linkedInvoiceId'),
            data.get('linkedInquiryId'), data.get('notes')
        ))
        conn.commit()
        job_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': job_id, 'message': 'Job created successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Job number already exists'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Error creating job: {str(e)}'}), 400

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE jobs 
            SET jobNumber=?, clientName=?, location=?, area=?, jobType=?, truck=?, driver=?, startDate=?,
                endDate=?, status=?, value=?, linkedInvoiceId=?, linkedInquiryId=?, notes=?,
                updatedAt=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (
            data['jobNumber'], data['clientName'], data['location'], data.get('area'),
            data.get('jobType'), data.get('truck'), data.get('driver'), data.get('startDate'), data.get('endDate'),
            data.get('status'), data.get('value'), data.get('linkedInvoiceId'),
            data.get('linkedInquiryId'), data.get('notes'), job_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Job updated successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Error updating job: {str(e)}'}), 400

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM jobs WHERE id=?', (job_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Job deleted successfully'})

@app.route('/api/jobs/bulk-delete', methods=['POST'])
def bulk_delete_jobs():
    data = request.json
    ids = data.get('ids', [])
    if not ids:
        return jsonify({'error': 'No IDs provided'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    placeholders = ','.join('?' * len(ids))
    cursor.execute(f'DELETE FROM jobs WHERE id IN ({placeholders})', ids)
    conn.commit()
    conn.close()
    return jsonify({'message': f'{len(ids)} jobs deleted successfully'})

@app.route('/api/jobs/export', methods=['GET'])
def export_jobs():
    import csv
    from io import StringIO
    
    area = request.args.get('area', 'all')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if area == 'all':
        cursor.execute('SELECT * FROM jobs ORDER BY createdAt DESC')
    else:
        cursor.execute('SELECT * FROM jobs WHERE area = ? ORDER BY createdAt DESC', (area,))
    
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if not jobs:
        return jsonify({'error': 'No jobs to export'}), 404
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=jobs[0].keys())
    writer.writeheader()
    writer.writerows(jobs)
    
    from flask import make_response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=jobs_export_{area}_{datetime.now().strftime("%Y%m%d")}.csv'
    return response

# API Routes - Vehicles
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicles ORDER BY registration')
    vehicles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(vehicles)

@app.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO vehicles (registration, vehicleType, ownerName, insuranceName,
                                motDue, taxDue, tachoDue, insuranceDue, maintenanceDue, 
                                motActioned, taxActioned, tachoActioned, insuranceActioned, maintenanceActioned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['registration'].upper(), data.get('vehicleType', 'car'), data['ownerName'], data['insuranceName'],
            data.get('motDue'), data['taxDue'], data.get('tachoDue'), data['insuranceDue'], data.get('maintenanceDue'),
            data.get('motActioned', False), data.get('taxActioned', False), 
            data.get('tachoActioned', False), data.get('insuranceActioned', False), data.get('maintenanceActioned', False)
        ))
        conn.commit()
        vehicle_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': vehicle_id, 'message': 'Vehicle created successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Registration number already exists'}), 400

@app.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vehicles 
        SET registration=?, vehicleType=?, ownerName=?, insuranceName=?,
            motDue=?, taxDue=?, tachoDue=?, insuranceDue=?, maintenanceDue=?, 
            motActioned=?, taxActioned=?, tachoActioned=?, insuranceActioned=?, maintenanceActioned=?
        WHERE id=?
    ''', (
        data['registration'].upper(), data.get('vehicleType', 'car'), data['ownerName'], data['insuranceName'],
        data.get('motDue'), data['taxDue'], data.get('tachoDue'), data['insuranceDue'], data.get('maintenanceDue'),
        data.get('motActioned', False), data.get('taxActioned', False),
        data.get('tachoActioned', False), data.get('insuranceActioned', False), 
        data.get('maintenanceActioned', False), vehicle_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Vehicle updated successfully'})

@app.route('/api/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vehicles WHERE id=?', (vehicle_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Vehicle deleted successfully'})

# Serve the HTML interface
@app.route('/')
def index():
    return send_from_directory('.', 'complete_scaffolding_dashboard.html')

def open_browser():
    """Open the default browser after a short delay"""
    import time
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """Main application entry point"""
    print("=" * 60)
    print("�️ KHALSA SCAFFOLDING - BUSINESS MANAGER V2")
    print("=" * 60)
    print()
    
    # Initialize database
    init_database()
    
    print()
    print("🚀 Starting server...")
    print("📍 Server will run at: http://127.0.0.1:5000")
    print("🗄️ Database location:", DB_PATH)
    print("✨ NEW: Invoice preview matches your Excel template!")
    print()
    print("💡 TIP: Keep this window open while using the application")
    print("⚠️ Press Ctrl+C to stop the server")
    print()
    
    # Open browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Flask server
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)

if __name__ == '__main__':
    main()