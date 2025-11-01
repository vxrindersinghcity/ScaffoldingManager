import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, AlertCircle, Users, FileText, Car, Download, Search, Loader, History, Filter, X } from 'lucide-react';

const API_URL = 'http://localhost:5000/api';

const BusinessDashboard = () => {
  const [activeTab, setActiveTab] = useState('invoices');
  const [invoices, setInvoices] = useState([]);
  const [inquiries, setInquiries] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [editingItem, setEditingItem] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // Search states
  const [invoiceSearch, setInvoiceSearch] = useState('');
  const [invoiceStatusFilter, setInvoiceStatusFilter] = useState('');
  const [invoiceYearFilter, setInvoiceYearFilter] = useState('');
  const [inquirySearch, setInquirySearch] = useState('');
  const [inquiryStatusFilter, setInquiryStatusFilter] = useState('');
  
  // Change history states
  const [showHistory, setShowHistory] = useState(false);
  const [changeHistory, setChangeHistory] = useState([]);
  const [historyItemId, setHistoryItemId] = useState(null);
  const [historyType, setHistoryType] = useState('');

  // Invoice editor state
  const [invoiceData, setInvoiceData] = useState({
    invoiceNumber: '',
    date: new Date().toISOString().split('T')[0],
    clientName: '',
    clientAddress: '',
    clientPhone: '',
    items: [{ description: '', quantity: 1, rate: 0 }],
    notes: ''
  });

  // Load data on component mount and when filters change
  useEffect(() => {
    loadInvoices();
  }, [invoiceSearch, invoiceStatusFilter, invoiceYearFilter]);

  useEffect(() => {
    loadInquiries();
  }, [inquirySearch, inquiryStatusFilter]);

  useEffect(() => {
    loadVehicles();
  }, []);

  const loadInvoices = async () => {
    try {
      const params = new URLSearchParams();
      if (invoiceSearch) params.append('search', invoiceSearch);
      if (invoiceStatusFilter) params.append('status', invoiceStatusFilter);
      if (invoiceYearFilter) params.append('year', invoiceYearFilter);
      
      const response = await fetch(`${API_URL}/invoices?${params}`);
      const data = await response.json();
      setInvoices(data);
    } catch (error) {
      console.error('Error loading invoices:', error);
      // Use mock data if API not available
      setInvoices([
        { id: 1, invoiceNumber: 'INV-001', clientName: 'ABC Construction', status: 'paid', date: '2025-10-15' },
        { id: 2, invoiceNumber: 'INV-002', clientName: 'Smith Builders', status: 'pending', date: '2025-10-28' }
      ]);
    }
  };

  const loadInquiries = async () => {
    try {
      const params = new URLSearchParams();
      if (inquirySearch) params.append('search', inquirySearch);
      if (inquiryStatusFilter) params.append('status', inquiryStatusFilter);
      
      const response = await fetch(`${API_URL}/inquiries?${params}`);
      const data = await response.json();
      setInquiries(data);
    } catch (error) {
      console.error('Error loading inquiries:', error);
      setInquiries([
        { id: 1, name: 'John Davis', phone: '07700 900123', location: 'Leicester', status: 'new', date: '2025-10-30', notes: 'Needs scaffolding for 2-story house renovation' }
      ]);
    }
  };

  const loadVehicles = async () => {
    try {
      const response = await fetch(`${API_URL}/vehicles`);
      const data = await response.json();
      setVehicles(data);
    } catch (error) {
      console.error('Error loading vehicles:', error);
      setVehicles([
        { id: 1, registration: 'AB12CDE', make: 'Ford', model: 'Transit', colour: 'White', fuelType: 'Diesel', motDue: '2025-11-15', taxDue: '2025-12-01', insuranceDue: '2025-11-20', motActioned: false, taxActioned: false, insuranceActioned: false }
      ]);
    }
  };

  const viewHistory = async (itemId, type) => {
    setHistoryItemId(itemId);
    setHistoryType(type);
    setShowHistory(true);
    
    try {
      const endpoint = type === 'invoice' ? `invoices/${itemId}/changes` : 
                       type === 'inquiry' ? `inquiries/${itemId}/changes` : 
                       `vehicles/${itemId}/changes`;
      const response = await fetch(`${API_URL}/${endpoint}`);
      const data = await response.json();
      setChangeHistory(data);
    } catch (error) {
      console.error('Error loading history:', error);
      setChangeHistory([]);
    }
  };

  const getUpcomingReminders = () => {
    const today = new Date();
    const reminders = [];

    vehicles.forEach(vehicle => {
      const checkDate = (dateStr, type, reminderDays, actioned) => {
        if (actioned) return;
        
        const date = new Date(dateStr);
        const daysUntil = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
        
        if (daysUntil <= reminderDays) {
          let urgencyLevel = 'warning';
          if (daysUntil <= 0) {
            urgencyLevel = 'overdue';
          } else if (daysUntil <= 7) {
            urgencyLevel = 'critical';
          }
          
          reminders.push({
            vehicleId: vehicle.id,
            vehicle: `${vehicle.registration} (${vehicle.make} ${vehicle.model})`,
            type,
            date: dateStr,
            daysUntil,
            urgencyLevel,
            actionField: type === 'MOT' ? 'motActioned' : type === 'Tax' ? 'taxActioned' : 'insuranceActioned'
          });
        }
      };

      checkDate(vehicle.motDue, 'MOT', 30, vehicle.motActioned);
      checkDate(vehicle.taxDue, 'Tax', 7, vehicle.taxActioned);
      checkDate(vehicle.insuranceDue, 'Insurance', 60, vehicle.insuranceActioned);
    });

    return reminders.sort((a, b) => {
      if (a.daysUntil < 0 && b.daysUntil >= 0) return -1;
      if (b.daysUntil < 0 && a.daysUntil >= 0) return 1;
      return a.daysUntil - b.daysUntil;
    });
  };

  const markAsActioned = async (vehicleId, actionField) => {
    try {
      const vehicle = vehicles.find(v => v.id === vehicleId);
      const updateData = { ...vehicle, [actionField]: true };
      
      await fetch(`${API_URL}/vehicles/${vehicleId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      
      loadVehicles();
    } catch (error) {
      console.error('Error updating vehicle:', error);
    }
  };

  const openModal = (type, item = null) => {
    setModalType(type);
    setEditingItem(item);
    
    if (type === 'invoice' && item) {
      const items = typeof item.items === 'string' ? JSON.parse(item.items) : item.items || [];
      setInvoiceData({
        invoiceNumber: item.invoiceNumber,
        date: item.date,
        clientName: item.clientName,
        clientAddress: item.clientAddress || '',
        clientPhone: item.clientPhone || '',
        items: items.length > 0 ? items : [{ description: '', quantity: 1, rate: 0 }],
        notes: item.notes || ''
      });
    } else if (type === 'invoice') {
      const nextInvoiceNum = `INV-${String(invoices.length + 1).padStart(3, '0')}`;
      setInvoiceData({
        invoiceNumber: nextInvoiceNum,
        date: new Date().toISOString().split('T')[0],
        clientName: '',
        clientAddress: '',
        clientPhone: '',
        items: [{ description: '', quantity: 1, rate: 0 }],
        notes: ''
      });
    }
    
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingItem(null);
  };

  const handleInvoiceChange = (field, value) => {
    setInvoiceData({ ...invoiceData, [field]: value });
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...invoiceData.items];
    newItems[index][field] = field === 'quantity' || field === 'rate' ? parseFloat(value) || 0 : value;
    setInvoiceData({ ...invoiceData, items: newItems });
  };

  const addInvoiceItem = () => {
    setInvoiceData({
      ...invoiceData,
      items: [...invoiceData.items, { description: '', quantity: 1, rate: 0 }]
    });
  };

  const removeInvoiceItem = (index) => {
    if (invoiceData.items.length > 1) {
      const newItems = invoiceData.items.filter((_, i) => i !== index);
      setInvoiceData({ ...invoiceData, items: newItems });
    }
  };

  const calculateTotal = () => {
    const subtotal = invoiceData.items.reduce((sum, item) => sum + (item.quantity * item.rate), 0);
    const vat = subtotal * 0.20;
    const total = subtotal + vat;
    return { subtotal, vat, total };
  };

  const saveInvoice = async () => {
    setIsGenerating(true);
    try {
      const totals = calculateTotal();
      const payload = {
        invoiceNumber: invoiceData.invoiceNumber,
        clientName: invoiceData.clientName,
        clientAddress: invoiceData.clientAddress,
        clientPhone: invoiceData.clientPhone,
        date: invoiceData.date,
        status: editingItem ? editingItem.status : 'pending',
        items: JSON.stringify(invoiceData.items),
        subtotal: totals.subtotal,
        vat: totals.vat,
        total: totals.total,
        notes: invoiceData.notes
      };
      
      if (editingItem) {
        await fetch(`${API_URL}/invoices/${editingItem.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        await fetch(`${API_URL}/invoices`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }
      
      loadInvoices();
      closeModal();
      alert('Invoice saved successfully!');
    } catch (error) {
      console.error('Error saving invoice:', error);
      alert('Error saving invoice. Check console for details.');
    } finally {
      setIsGenerating(false);
    }
  };

  const generateInvoiceExcel = async () => {
    try {
      const totals = calculateTotal();
      const payload = {
        invoiceNumber: invoiceData.invoiceNumber,
        clientName: invoiceData.clientName,
        clientAddress: invoiceData.clientAddress,
        clientPhone: invoiceData.clientPhone,
        date: invoiceData.date,
        items: JSON.stringify(invoiceData.items)
      };
      
      const response = await fetch(`${API_URL}/invoice/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice_${invoiceData.invoiceNumber}.xlsx`;
      a.click();
      
      alert('Invoice Excel file downloaded!');
    } catch (error) {
      console.error('Error generating Excel:', error);
      alert('Excel generation not available. Invoice saved to database.');
    }
  };

  const lookupVehicle = async (registration) => {
    if (!registration || registration.length < 5) {
      alert('Please enter a valid registration number');
      return;
    }
    
    setLookupLoading(true);
    try {
      const response = await fetch(`${API_URL}/vehicle/lookup/${registration}`);
      const data = await response.json();
      
      document.getElementById('make').value = data.make;
      document.getElementById('model').value = data.model;
      document.getElementById('colour').value = data.colour;
      document.getElementById('fuelType').value = data.fuelType;
      document.getElementById('motDue').value = data.motExpiryDate;
      
      alert('Vehicle data retrieved!');
    } catch (error) {
      console.error('Error looking up vehicle:', error);
      alert('Vehicle lookup failed. Please enter details manually.');
    } finally {
      setLookupLoading(false);
    }
  };

  const handleSubmitInquiry = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const payload = {
      name: formData.get('name'),
      phone: formData.get('phone'),
      email: formData.get('email'),
      location: formData.get('location'),
      status: formData.get('status'),
      date: formData.get('date'),
      notes: formData.get('notes'),
      quoteAmount: parseFloat(formData.get('quoteAmount')) || null
    };

    try {
      if (editingItem) {
        await fetch(`${API_URL}/inquiries/${editingItem.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        await fetch(`${API_URL}/inquiries`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }
      
      loadInquiries();
      closeModal();
    } catch (error) {
      console.error('Error saving inquiry:', error);
    }
  };

  const handleSubmitVehicle = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const payload = {
      registration: formData.get('registration'),
      make: formData.get('make'),
      model: formData.get('model'),
      colour: formData.get('colour'),
      fuelType: formData.get('fuelType'),
      motDue: formData.get('motDue'),
      taxDue: formData.get('taxDue'),
      insuranceDue: formData.get('insuranceDue'),
      motActioned: editingItem ? editingItem.motActioned : false,
      taxActioned: editingItem ? editingItem.taxActioned : false,
      insuranceActioned: editingItem ? editingItem.insuranceActioned : false
    };

    try {
      if (editingItem) {
        await fetch(`${API_URL}/vehicles/${editingItem.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } else {
        await fetch(`${API_URL}/vehicles`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      }
      
      loadVehicles();
      closeModal();
    } catch (error) {
      console.error('Error saving vehicle:', error);
    }
  };

  const deleteItem = async (id, type) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      const endpoint = type === 'invoice' ? 'invoices' : type === 'inquiry' ? 'inquiries' : 'vehicles';
      await fetch(`${API_URL}/${endpoint}/${id}`, { method: 'DELETE' });
      
      if (type === 'invoice') loadInvoices();
      else if (type === 'inquiry') loadInquiries();
      else loadVehicles();
    } catch (error) {
      console.error('Error deleting item:', error);
    }
  };

  const updateInvoiceStatus = async (invoiceId, newStatus) => {
    try {
      const invoice = invoices.find(inv => inv.id === invoiceId);
      await fetch(`${API_URL}/invoices/${invoiceId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...invoice, status: newStatus })
      });
      loadInvoices();
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const upcomingReminders = getUpcomingReminders();
  
  // Generate year options for filter
  const currentYear = new Date().getFullYear();
  const yearOptions = Array.from({ length: 11 }, (_, i) => currentYear - i);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-800 mb-2">Scaffolding Business Manager</h1>
          <p className="text-slate-600">Complete business management with permanent data storage</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-600 text-sm">Total Invoices</p>
                <p className="text-2xl font-bold text-slate-800">{invoices.length}</p>
              </div>
              <FileText className="text-blue-500" size={32} />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-600 text-sm">New Inquiries</p>
                <p className="text-2xl font-bold text-slate-800">{inquiries.filter(i => i.status === 'new').length}</p>
              </div>
              <Users className="text-green-500" size={32} />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-600 text-sm">Active Reminders</p>
                <p className="text-2xl font-bold text-slate-800">{upcomingReminders.length}</p>
              </div>
              <AlertCircle className="text-red-500" size={32} />
            </div>
          </div>
        </div>

        {upcomingReminders.length > 0 && (
          <div className="bg-orange-50 border-l-4 border-orange-500 p-4 mb-8 rounded-lg shadow">
            <div className="flex items-start">
              <AlertCircle className="text-orange-500 mr-3 mt-1 flex-shrink-0" size={24} />
              <div className="flex-1">
                <h3 className="font-bold text-orange-800 mb-3">⚠️ Vehicle Reminders - Action Required</h3>
                <div className="space-y-3">
                  {upcomingReminders.map((reminder, idx) => (
                    <div 
                      key={idx} 
                      className={`p-3 rounded-lg border ${
                        reminder.urgencyLevel === 'overdue' 
                          ? 'bg-red-100 border-red-300' 
                          : reminder.urgencyLevel === 'critical'
                          ? 'bg-orange-100 border-orange-300'
                          : 'bg-yellow-50 border-yellow-300'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-semibold text-slate-800">
                            {reminder.vehicle} - {reminder.type}
                          </p>
                          <p className={`text-sm font-semibold ${
                            reminder.urgencyLevel === 'overdue' 
                              ? 'text-red-700' 
                              : reminder.urgencyLevel === 'critical'
                              ? 'text-orange-700'
                              : 'text-yellow-700'
                          }`}>
                            {reminder.daysUntil < 0 
                              ? `⚠️ OVERDUE by ${Math.abs(reminder.daysUntil)} days!` 
                              : `Due in ${reminder.daysUntil} days (${reminder.date})`}
                          </p>
                          <p className="text-xs text-slate-600 mt-1">
                            {reminder.type === 'MOT' && '🔧 Book MOT test'}
                            {reminder.type === 'Tax' && '💰 Renew road tax'}
                            {reminder.type === 'Insurance' && '🛡️ Renew insurance policy'}
                          </p>
                        </div>
                        <button
                          onClick={() => markAsActioned(reminder.vehicleId, reminder.actionField)}
                          className="ml-3 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition font-semibold whitespace-nowrap"
                        >
                          ✓ Done
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-orange-600 mt-3 italic">
                  💡 Reminders: MOT (1 month before) • Insurance (2 months before) • Tax (7 days before)
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('invoices')}
              className={`flex-1 py-4 px-6 font-semibold transition ${
                activeTab === 'invoices'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <FileText className="inline mr-2" size={20} />
              Invoices
            </button>
            <button
              onClick={() => setActiveTab('inquiries')}
              className={`flex-1 py-4 px-6 font-semibold transition ${
                activeTab === 'inquiries'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <Users className="inline mr-2" size={20} />
              Inquiries
            </button>
            <button
              onClick={() => setActiveTab('vehicles')}
              className={`flex-1 py-4 px-6 font-semibold transition ${
                activeTab === 'vehicles'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <Car className="inline mr-2" size={20} />
              Vehicles
            </button>
          </div>

          {activeTab === 'invoices' && (
            <div className="p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <h2 className="text-2xl font-bold text-slate-800">Invoices</h2>
                <button
                  onClick={() => openModal('invoice')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center hover:bg-blue-700 transition"
                >
                  <Plus size={20} className="mr-2" />
                  Create Invoice
                </button>
              </div>

              {/* Search and Filter Bar */}
              <div className="bg-slate-50 p-4 rounded-lg mb-4 border border-slate-200">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                  <div className="md:col-span-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-3 text-slate-400" size={18} />
                      <input
                        type="text"
                        placeholder="Search by invoice # or client name..."
                        value={invoiceSearch}
                        onChange={(e) => setInvoiceSearch(e.target.value)}
                        className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div>
                    <select
                      value={invoiceStatusFilter}
                      onChange={(e) => setInvoiceStatusFilter(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Statuses</option>
                      <option value="pending">Pending</option>
                      <option value="paid">Paid</option>
                      <option value="overdue">Overdue</option>
                    </select>
                  </div>
                  <div>
                    <select
                      value={invoiceYearFilter}
                      onChange={(e) => setInvoiceYearFilter(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Years</option>
                      {yearOptions.map(year => (
                        <option key={year} value={year}>{year}</option>
                      ))}
                    </select>
                  </div>
                </div>
                {(invoiceSearch || invoiceStatusFilter || invoiceYearFilter) && (
                  <div className="mt-3 flex items-center text-sm text-slate-600">
                    <Filter size={16} className="mr-2" />
                    <span>Showing {invoices.length} results</span>
                    <button
                      onClick={() => {
                        setInvoiceSearch('');
                        setInvoiceStatusFilter('');
                        setInvoiceYearFilter('');
                      }}
                      className="ml-4 text-blue-600 hover:text-blue-800"
                    >
                      Clear filters
                    </button>
                  </div>
                )}
              </div>

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-slate-200">
                      <th className="text-left py-3 px-4 text-slate-700 font-semibold">Invoice #</th>
                      <th className="text-left py-3 px-4 text-slate-700 font-semibold">Client</th>
                      <th className="text-left py-3 px-4 text-slate-700 font-semibold">Date</th>
                      <th className="text-left py-3 px-4 text-slate-700 font-semibold">Total</th>
                      <th className="text-left py-3 px-4 text-slate-700 font-semibold">Status</th>
                      <th className="text-left py-3 px-4 text-slate-700 font-semibold">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoices.map(invoice => (
                      <tr key={invoice.id} className="border-b border-slate-100 hover:bg-slate-50">
                        <td className="py-3 px-4 font-mono text-sm">{invoice.invoiceNumber}</td>
                        <td className="py-3 px-4">{invoice.clientName}</td>
                        <td className="py-3 px-4">{invoice.date}</td>
                        <td className="py-3 px-4 font-semibold">
                          {invoice.total ? `£${invoice.total.toFixed(2)}` : '-'}
                        </td>
                        <td className="py-3 px-4">
                          <select
                            value={invoice.status}
                            onChange={(e) => updateInvoiceStatus(invoice.id, e.target.value)}
                            className={`px-3 py-1 rounded-full text-xs font-semibold border-0 cursor-pointer ${
                              invoice.status === 'paid' ? 'bg-green-100 text-green-800' :
                              invoice.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}
                          >
                            <option value="pending">Pending</option>
                            <option value="paid">Paid</option>
                            <option value="overdue">Overdue</option>
                          </select>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => viewHistory(invoice.id, 'invoice')}
                              className="text-purple-600 hover:text-purple-800"
                              title="View History"
                            >
                              <History size={18} />
                            </button>
                            <button
                              onClick={() => openModal('invoice', invoice)}
                              className="text-blue-600 hover:text-blue-800"
                              title="Edit"
                            >
                              <Edit2 size={18} />
                            </button>
                            <button
                              onClick={() => deleteItem(invoice.id, 'invoice')}
                              className="text-red-600 hover:text-red-800"
                              title="Delete"
                            >
                              <Trash2 size={18} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {invoices.length === 0 && (
                  <div className="text-center py-8 text-slate-500">
                    No invoices found. Create your first invoice!
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'inquiries' && (
            <div className="p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <h2 className="text-2xl font-bold text-slate-800">Scaffolding Inquiries</h2>
                <button
                  onClick={() => openModal('inquiry')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center hover:bg-blue-700 transition"
                >
                  <Plus size={20} className="mr-2" />
                  New Inquiry
                </button>
              </div>

              {/* Search and Filter Bar */}
              <div className="bg-slate-50 p-4 rounded-lg mb-4 border border-slate-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <div className="relative">
                      <Search className="absolute left-3 top-3 text-slate-400" size={18} />
                      <input
                        type="text"
                        placeholder="Search by name, phone, or location..."
                        value={inquirySearch}
                        onChange={(e) => setInquirySearch(e.target.value)}
                        className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div>
                    <select
                      value={inquiryStatusFilter}
                      onChange={(e) => setInquiryStatusFilter(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Statuses</option>
                      <option value="new">New</option>
                      <option value="contacted">Contacted</option>
                      <option value="quoted">Quoted</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                {inquiries.map(inquiry => (
                  <div key={inquiry.id} className="bg-slate-50 rounded-lg p-4 border border-slate-200 hover:border-blue-300 transition">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-slate-800">{inquiry.name}</h3>
                        <p className="text-sm text-slate-600">{inquiry.phone} • {inquiry.location}</p>
                        {inquiry.email && <p className="text-sm text-slate-600">{inquiry.email}</p>}
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          inquiry.status === 'new' ? 'bg-blue-100 text-blue-800' :
                          inquiry.status === 'contacted' ? 'bg-yellow-100 text-yellow-800' :
                          inquiry.status === 'quoted' ? 'bg-purple-100 text-purple-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {inquiry.status}
                        </span>
                        <button
                          onClick={() => viewHistory(inquiry.id, 'inquiry')}
                          className="text-purple-600 hover:text-purple-800"
                          title="View History"
                        >
                          <History size={18} />
                        </button>
                        <button
                          onClick={() => openModal('inquiry', inquiry)}
                          className="text-blue-600 hover:text-blue-800"
                          title="Edit"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => deleteItem(inquiry.id, 'inquiry')}
                          className="text-red-600 hover:text-red-800"
                          title="Delete"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>
                    <p className="text-sm text-slate-700 mb-2">{inquiry.notes}</p>
                    <div className="flex justify-between items-center text-xs text-slate-500">
                      <span>Date: {inquiry.date}</span>
                      {inquiry.quoteAmount && <span className="font-semibold">Quote: £{inquiry.quoteAmount}</span>}
                    </div>
                  </div>
                ))}
                {inquiries.length === 0 && (
                  <div className="text-center py-8 text-slate-500">
                    No inquiries found. Add a new inquiry!
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'vehicles' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-slate-800">Vehicle Reminders</h2>
                <button
                  onClick={() => openModal('vehicle')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center hover:bg-blue-700 transition"
                >
                  <Plus size={20} className="mr-2" />
                  Add Vehicle
                </button>
              </div>
              <div className="space-y-4">
                {vehicles.map(vehicle => {
                  const today = new Date();
                  const checkDue = (dateStr) => {
                    const date = new Date(dateStr);
                    const daysUntil = Math.ceil((date - today) / (1000 * 60 * 60 * 24));
                    return { daysUntil, isUrgent: daysUntil <= 14 && daysUntil >= 0 };
                  };

                  const motStatus = checkDue(vehicle.motDue);
                  const taxStatus = checkDue(vehicle.taxDue);
                  const insuranceStatus = checkDue(vehicle.insuranceDue);

                  return (
                    <div key={vehicle.id} className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h3 className="text-lg font-bold text-slate-800">{vehicle.registration}</h3>
                          <p className="text-sm text-slate-600">{vehicle.make} {vehicle.model} • {vehicle.colour} • {vehicle.fuelType}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => viewHistory(vehicle.id, 'vehicle')}
                            className="text-purple-600 hover:text-purple-800"
                            title="View History"
                          >
                            <History size={18} />
                          </button>
                          <button
                            onClick={() => openModal('vehicle', vehicle)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Edit"
                          >
                            <Edit2 size={18} />
                          </button>
                          <button
                            onClick={() => deleteItem(vehicle.id, 'vehicle')}
                            className="text-red-600 hover:text-red-800"
                            title="Delete"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className={`p-3 rounded ${motStatus.isUrgent ? 'bg-red-50 border border-red-200' : 'bg-white border border-slate-200'}`}>
                          <div className="flex justify-between items-start mb-1">
                            <p className="text-xs font-semibold text-slate-600">MOT Due</p>
                            {vehicle.motActioned && (
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">
                                ✓ Done
                              </span>
                            )}
                          </div>
                          <p className="font-bold text-slate-800">{vehicle.motDue}</p>
                          {motStatus.isUrgent && !vehicle.motActioned && (
                            <p className="text-xs text-red-600 font-semibold mt-1">
                              {motStatus.daysUntil < 0 ? `OVERDUE by ${Math.abs(motStatus.daysUntil)} days!` : `Due in ${motStatus.daysUntil} days!`}
                            </p>
                          )}
                        </div>
                        <div className={`p-3 rounded ${taxStatus.isUrgent ? 'bg-red-50 border border-red-200' : 'bg-white border border-slate-200'}`}>
                          <div className="flex justify-between items-start mb-1">
                            <p className="text-xs font-semibold text-slate-600">Tax Due</p>
                            {vehicle.taxActioned && (
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">
                                ✓ Done
                              </span>
                            )}
                          </div>
                          <p className="font-bold text-slate-800">{vehicle.taxDue}</p>
                          {taxStatus.isUrgent && !vehicle.taxActioned && (
                            <p className="text-xs text-red-600 font-semibold mt-1">
                              {taxStatus.daysUntil < 0 ? `OVERDUE by ${Math.abs(taxStatus.daysUntil)} days!` : `Due in ${taxStatus.daysUntil} days!`}
                            </p>
                          )}
                        </div>
                        <div className={`p-3 rounded ${insuranceStatus.isUrgent ? 'bg-red-50 border border-red-200' : 'bg-white border border-slate-200'}`}>
                          <div className="flex justify-between items-start mb-1">
                            <p className="text-xs font-semibold text-slate-600">Insurance Due</p>
                            {vehicle.insuranceActioned && (
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-semibold">
                                ✓ Done
                              </span>
                            )}
                          </div>
                          <p className="font-bold text-slate-800">{vehicle.insuranceDue}</p>
                          {insuranceStatus.isUrgent && !vehicle.insuranceActioned && (
                            <p className="text-xs text-red-600 font-semibold mt-1">
                              {insuranceStatus.daysUntil < 0 ? `OVERDUE by ${Math.abs(insuranceStatus.daysUntil)} days!` : `Due in ${insuranceStatus.daysUntil} days!`}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Invoice Modal */}
      {showModal && modalType === 'invoice' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-slate-800 mb-4">
                {editingItem ? 'Edit Invoice' : 'Create New Invoice'}
              </h2>

              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Invoice Number</label>
                    <input
                      type="text"
                      value={invoiceData.invoiceNumber}
                      onChange={(e) => handleInvoiceChange('invoiceNumber', e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Date</label>
                    <input
                      type="date"
                      value={invoiceData.date}
                      onChange={(e) => handleInvoiceChange('date', e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h3 className="font-bold text-slate-800 mb-3">Client Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Client Name</label>
                      <input
                        type="text"
                        value={invoiceData.clientName}
                        onChange={(e) => handleInvoiceChange('clientName', e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Address</label>
                      <input
                        type="text"
                        value={invoiceData.clientAddress}
                        onChange={(e) => handleInvoiceChange('clientAddress', e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-slate-700 mb-1">Phone</label>
                      <input
                        type="tel"
                        value={invoiceData.clientPhone}
                        onChange={(e) => handleInvoiceChange('clientPhone', e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      />
                    </div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="font-bold text-slate-800">Line Items</h3>
                    <button
                      onClick={addInvoiceItem}
                      className="text-blue-600 hover:text-blue-800 flex items-center text-sm"
                    >
                      <Plus size={16} className="mr-1" /> Add Item
                    </button>
                  </div>
                  
                  {invoiceData.items.map((item, index) => (
                    <div key={index} className="grid grid-cols-12 gap-2 mb-2">
                      <div className="col-span-5">
                        <input
                          type="text"
                          placeholder="Description"
                          value={item.description}
                          onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                        />
                      </div>
                      <div className="col-span-2">
                        <input
                          type="number"
                          placeholder="Qty"
                          value={item.quantity}
                          onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                          min="0"
                        />
                      </div>
                      <div className="col-span-2">
                        <input
                          type="number"
                          placeholder="Rate £"
                          value={item.rate}
                          onChange={(e) => handleItemChange(index, 'rate', e.target.value)}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                          min="0"
                          step="0.01"
                        />
                      </div>
                      <div className="col-span-2 flex items-center">
                        <span className="text-sm font-semibold text-slate-700">
                          £{(item.quantity * item.rate).toFixed(2)}
                        </span>
                      </div>
                      <div className="col-span-1 flex items-center justify-center">
                        {invoiceData.items.length > 1 && (
                          <button
                            onClick={() => removeInvoiceItem(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="border-t pt-4">
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Notes</label>
                  <textarea
                    value={invoiceData.notes}
                    onChange={(e) => handleInvoiceChange('notes', e.target.value)}
                    rows="2"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    placeholder="Additional notes..."
                  ></textarea>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-end">
                    <div className="w-64">
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-slate-600">Subtotal:</span>
                        <span className="text-sm font-semibold">£{calculateTotal().subtotal.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-slate-600">VAT (20%):</span>
                        <span className="text-sm font-semibold">£{calculateTotal().vat.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2">
                        <span className="font-bold text-slate-800">Total:</span>
                        <span className="font-bold text-slate-800 text-lg">£{calculateTotal().total.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={saveInvoice}
                    disabled={isGenerating}
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition font-semibold"
                  >
                    {isGenerating ? 'Saving...' : 'Save Invoice'}
                  </button>
                  <button
                    onClick={generateInvoiceExcel}
                    className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition font-semibold flex items-center justify-center"
                  >
                    <Download className="mr-2" size={20} />
                    Download Excel
                  </button>
                  <button
                    onClick={closeModal}
                    className="flex-1 bg-slate-200 text-slate-700 py-2 rounded-lg hover:bg-slate-300 transition font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Inquiry Modal */}
      {showModal && modalType === 'inquiry' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-slate-800 mb-4">
                {editingItem ? 'Edit Inquiry' : 'New Inquiry'}
              </h2>

              <form onSubmit={handleSubmitInquiry} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Name *</label>
                    <input
                      type="text"
                      name="name"
                      defaultValue={editingItem?.name}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Phone *</label>
                    <input
                      type="tel"
                      name="phone"
                      defaultValue={editingItem?.phone}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Email</label>
                    <input
                      type="email"
                      name="email"
                      defaultValue={editingItem?.email}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Location *</label>
                    <input
                      type="text"
                      name="location"
                      defaultValue={editingItem?.location}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Date *</label>
                    <input
                      type="date"
                      name="date"
                      defaultValue={editingItem?.date || new Date().toISOString().split('T')[0]}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Status</label>
                    <select
                      name="status"
                      defaultValue={editingItem?.status || 'new'}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    >
                      <option value="new">New</option>
                      <option value="contacted">Contacted</option>
                      <option value="quoted">Quoted</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Quote Amount (£)</label>
                    <input
                      type="number"
                      name="quoteAmount"
                      step="0.01"
                      defaultValue={editingItem?.quoteAmount}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Notes</label>
                  <textarea
                    name="notes"
                    defaultValue={editingItem?.notes}
                    rows="3"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                  ></textarea>
                </div>
                <div className="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition font-semibold"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={closeModal}
                    className="flex-1 bg-slate-200 text-slate-700 py-2 rounded-lg hover:bg-slate-300 transition font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Vehicle Modal */}
      {showModal && modalType === 'vehicle' && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-slate-800 mb-4">
                {editingItem ? 'Edit Vehicle' : 'Add Vehicle'}
              </h2>

              <form onSubmit={handleSubmitVehicle} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Registration Number *</label>
                  <input
                    type="text"
                    id="registration"
                    name="registration"
                    defaultValue={editingItem?.registration}
                    placeholder="AB12 CDE"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg uppercase"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Make *</label>
                    <input
                      type="text"
                      id="make"
                      name="make"
                      defaultValue={editingItem?.make}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Model *</label>
                    <input
                      type="text"
                      id="model"
                      name="model"
                      defaultValue={editingItem?.model}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Colour</label>
                    <input
                      type="text"
                      id="colour"
                      name="colour"
                      defaultValue={editingItem?.colour}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Fuel Type</label>
                    <input
                      type="text"
                      id="fuelType"
                      name="fuelType"
                      defaultValue={editingItem?.fuelType}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">MOT Due Date *</label>
                    <input
                      type="date"
                      id="motDue"
                      name="motDue"
                      defaultValue={editingItem?.motDue}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Tax Due Date *</label>
                    <input
                      type="date"
                      name="taxDue"
                      defaultValue={editingItem?.taxDue}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-1">Insurance Due Date *</label>
                    <input
                      type="date"
                      name="insuranceDue"
                      defaultValue={editingItem?.insuranceDue}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg"
                      required
                    />
                  </div>
                </div>
                <div className="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition font-semibold"
                  >
                    Save Vehicle
                  </button>
                  <button
                    type="button"
                    onClick={closeModal}
                    className="flex-1 bg-slate-200 text-slate-700 py-2 rounded-lg hover:bg-slate-300 transition font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Change History Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold text-slate-800">Change History</h2>
                <button
                  onClick={() => setShowHistory(false)}
                  className="text-slate-600 hover:text-slate-800"
                >
                  <X size={24} />
                </button>
              </div>
              
              <div className="space-y-3">
                {changeHistory.length > 0 ? (
                  changeHistory.map((change, idx) => (
                    <div key={change.id} className="border-l-4 border-blue-500 bg-slate-50 p-4 rounded">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <span className={`inline-block px-2 py-1 rounded text-xs font-semibold mb-2 ${
                            change.changeType === 'created' ? 'bg-green-100 text-green-800' :
                            change.changeType === 'updated' ? 'bg-blue-100 text-blue-800' :
                            change.changeType === 'status_changed' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-slate-100 text-slate-800'
                          }`}>
                            {change.changeType}
                          </span>
                          <p className="text-sm text-slate-700">{change.description}</p>
                        </div>
                        <span className="text-xs text-slate-500">
                          {new Date(change.changedAt).toLocaleString()}
                        </span>
                      </div>
                      {change.oldValue && change.newValue && (
                        <div className="text-xs text-slate-600 mt-2">
                          <span className="font-semibold">From:</span> {change.oldValue} 
                          <span className="mx-2">→</span>
                          <span className="font-semibold">To:</span> {change.newValue}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-slate-500">
                    No change history available
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BusinessDashboard;