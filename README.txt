============================================================
   SCAFFOLDING BUSINESS MANAGER - ULTIMATE EDITION
============================================================

📋 WHAT'S INCLUDED
------------------
✅ Complete business management system
✅ Invoice creation and PDF generation
✅ Customer inquiry tracking
✅ Vehicle fleet management with reminders
✅ Excel export functionality
✅ Beautiful modern interface
✅ SQLite database (no external database needed)


🚀 QUICK START - OPTION 1: Easy Launch (Windows)
------------------------------------------------
1. Make sure Python 3.8+ is installed
   Download from: https://www.python.org/downloads/
   ⚠️ CHECK "Add Python to PATH" during installation!

2. Double-click: START_MANAGER.bat

3. The app will open in your browser automatically

4. Keep the black window (terminal) open while using the app

5. Press Ctrl+C in the terminal to stop the server


🔧 QUICK START - OPTION 2: Manual Launch
-----------------------------------------
1. Open Command Prompt or PowerShell

2. Navigate to this folder:
   cd path\to\this\folder

3. Install dependencies (first time only):
   pip install Flask Flask-CORS

4. Run the application:
   python scaffolding_manager.py

5. Open your browser to:
   http://127.0.0.1:5000


💾 DATABASE LOCATION
--------------------
Your business data is stored in:
📁 C:\Users\YourUsername\scaffolding_business.db

This file contains all your:
- Invoices
- Customer inquiries
- Vehicle information

⚠️ BACKUP THIS FILE REGULARLY!


📊 FEATURES
-----------
📄 INVOICE MANAGEMENT
  • Create and edit professional invoices
  • Automatic VAT calculation (20%)
  • Generate PDF invoices
  • Track payment status (Pending/Paid/Overdue)
  • Export to Excel

👥 INQUIRY TRACKING
  • Manage customer inquiries
  • Track quote amounts
  • Status workflow (New → Contacted → Quoted → Completed)
  • Full contact details
  • Export to Excel

🚗 VEHICLE FLEET
  • Track MOT, Tax, and Insurance dates
  • Automatic reminders (30/14/60 days)
  • Color-coded urgency levels
  • Mark reminders as complete
  • Export to Excel


🔍 SEARCH & FILTER
------------------
• Advanced search functionality
• Filter by status
• Real-time results
• Export filtered data


⚙️ SYSTEM REQUIREMENTS
----------------------
• Windows 7 or higher
• Python 3.8 or higher
• 100MB free disk space
• Modern web browser (Chrome, Firefox, Edge)
• Internet connection (for first-time setup only)


🆘 TROUBLESHOOTING
------------------
❌ "Python is not recognized"
   → Install Python and check "Add to PATH"
   → Restart your computer after installation

❌ Port 5000 already in use
   → Close other applications using port 5000
   → Or edit scaffolding_manager.py and change port number

❌ Browser doesn't open automatically
   → Manually open: http://127.0.0.1:5000

❌ Can't create invoices/inquiries
   → Check that the database file isn't read-only
   → Make sure you have write permissions in your home folder

❌ Excel export not working
   → This is a browser feature - allow downloads
   → Check your Downloads folder


📞 TIPS & BEST PRACTICES
-------------------------
✅ Always backup your database file regularly
✅ Keep the terminal window open while using the app
✅ Use Chrome or Firefox for best experience
✅ Export data to Excel monthly for records
✅ Update vehicle dates promptly
✅ Review reminders at the start of each week


🔒 DATA SECURITY
----------------
• All data is stored locally on your computer
• No internet connection required after setup
• No data is sent to external servers
• Backup your database file to USB/cloud storage


📝 KEYBOARD SHORTCUTS
---------------------
• Ctrl+F: Focus search box
• Esc: Close modal windows
• Tab: Navigate between fields
• Enter: Submit forms


🌟 ADVANCED FEATURES
--------------------
PDF Generation:
  • Professional invoice layout
  • Company branding space
  • Automatic calculations
  • Print-ready format

Excel Exports:
  • Formatted spreadsheets
  • Timestamped filenames
  • All data types supported
  • Opens directly in Excel

Smart Reminders:
  • 🚨 OVERDUE: Past due date
  • ⏰ URGENT: 7 days or less
  • 📅 UPCOMING: Within threshold


📁 FILE STRUCTURE
-----------------
ScaffoldingManager/
├── START_MANAGER.bat           ← Double-click to start
├── scaffolding_manager.py      ← Main application
├── complete_scaffolding_manager.html  ← Web interface
├── README.txt                  ← This file
└── requirements.txt            ← Python packages


🔄 UPDATING THE APPLICATION
---------------------------
1. Backup your database file
2. Replace the application files
3. Run START_MANAGER.bat
4. Your data will be preserved


💡 CREATING DESKTOP SHORTCUT
----------------------------
1. Right-click START_MANAGER.bat
2. Select "Create shortcut"
3. Drag shortcut to Desktop
4. (Optional) Right-click shortcut → Properties → Change Icon


🎓 USING THE APPLICATION
------------------------
INVOICES:
1. Click "Create Invoice" button
2. Fill in client details
3. Add line items (description, quantity, rate)
4. Review totals (VAT calculated automatically)
5. Click "Save Invoice"
6. Generate PDF or change status as needed

INQUIRIES:
1. Click "New Inquiry" button
2. Enter customer contact details
3. Add location and notes
4. Set initial status
5. Update status as you progress
6. Add quote amount when ready

VEHICLES:
1. Click "Add Vehicle" button
2. Enter registration and vehicle details
3. Set MOT, Tax, and Insurance dates
4. View reminders on dashboard
5. Mark items as complete when actioned


⚠️ IMPORTANT NOTES
------------------
• Keep the terminal window OPEN while using the app
• Close browser tab when finished
• Press Ctrl+C in terminal to stop server
• Database auto-saves all changes
• No "Save" button needed for the application itself


📧 SUPPORT
----------
For issues or questions:
1. Check TROUBLESHOOTING section above
2. Verify Python is installed correctly
3. Check database file permissions
4. Try restarting the application


🎉 ENJOY YOUR BUSINESS MANAGER!
--------------------------------
This application was designed to make managing your
scaffolding business easier and more efficient.

Good luck with your business! 🏗️


============================================================
                  Version 1.0 - Ultimate Edition
                     © 2024 - All Rights Reserved
============================================================
