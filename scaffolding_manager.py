#!/usr/bin/env python3
"""
Scaffolding Business Manager - Standalone Application
Complete business management system with embedded web interface
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
            total REAL,
            notes TEXT,
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
            motDue TEXT NOT NULL,
            taxDue TEXT NOT NULL,
            tachoDue TEXT,
            insuranceDue TEXT NOT NULL,
            motActioned BOOLEAN DEFAULT 0,
            taxActioned BOOLEAN DEFAULT 0,
            tachoActioned BOOLEAN DEFAULT 0,
            insuranceActioned BOOLEAN DEFAULT 0,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        cursor.execute('''
            INSERT INTO invoices (invoiceNumber, clientName, clientAddress, clientPhone, 
                                date, status, items, subtotal, vat, total, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['invoiceNumber'], data['clientName'], data.get('clientAddress'),
            data.get('clientPhone'), data['date'], data['status'], data['items'],
            data['subtotal'], data['vat'], data['total'], data.get('notes')
        ))
        conn.commit()
        invoice_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': invoice_id, 'message': 'Invoice created successfully'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Invoice number already exists'}), 400

@app.route('/api/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE invoices 
        SET invoiceNumber=?, clientName=?, clientAddress=?, clientPhone=?,
            date=?, status=?, items=?, subtotal=?, vat=?, total=?, notes=?
        WHERE id=?
    ''', (
        data['invoiceNumber'], data['clientName'], data.get('clientAddress'),
        data.get('clientPhone'), data['date'], data['status'], data['items'],
        data['subtotal'], data['vat'], data['total'], data.get('notes'), invoice_id
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
        INSERT INTO inquiries (name, phone, email, location, status, date, quoteAmount, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data['phone'], data.get('email'), data['location'],
        data['status'], data['date'], data.get('quoteAmount'), data.get('notes')
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
        SET name=?, phone=?, email=?, location=?, status=?, date=?, quoteAmount=?, notes=?
        WHERE id=?
    ''', (
        data['name'], data['phone'], data.get('email'), data['location'],
        data['status'], data['date'], data.get('quoteAmount'), data.get('notes'), inquiry_id
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
                                motDue, taxDue, tachoDue, insuranceDue, motActioned, taxActioned, tachoActioned, insuranceActioned)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['registration'].upper(), data.get('vehicleType', 'car'), data['ownerName'], data['insuranceName'],
            data['motDue'], data['taxDue'], data.get('tachoDue'), data['insuranceDue'],
            data.get('motActioned', False), data.get('taxActioned', False), 
            data.get('tachoActioned', False), data.get('insuranceActioned', False)
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
            motDue=?, taxDue=?, tachoDue=?, insuranceDue=?, motActioned=?, taxActioned=?, tachoActioned=?, insuranceActioned=?
        WHERE id=?
    ''', (
        data['registration'].upper(), data.get('vehicleType', 'car'), data['ownerName'], data['insuranceName'],
        data['motDue'], data['taxDue'], data.get('tachoDue'), data['insuranceDue'],
        data.get('motActioned', False), data.get('taxActioned', False),
        data.get('tachoActioned', False), data.get('insuranceActioned', False), vehicle_id
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
    return send_from_directory('.', 'complete_scaffolding_manager.html')

def open_browser():
    """Open the default browser after a short delay"""
    import time
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

def main():
    """Main application entry point"""
    print("=" * 60)
    print("🏗️  SCAFFOLDING BUSINESS MANAGER")
    print("=" * 60)
    print()
    
    # Initialize database
    init_database()
    
    print()
    print("🚀 Starting server...")
    print("📍 Server will run at: http://127.0.0.1:5000")
    print("🗄️  Database location:", DB_PATH)
    print()
    print("💡 TIP: Keep this window open while using the application")
    print("⚠️  Press Ctrl+C to stop the server")
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
