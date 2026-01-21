# ✈️ Odoo Travel Management Module

This project is an **Odoo module** designed to manage **employee travel and mission requests** within an organization.  
It provides a structured workflow to **request, approve, track, and manage business trips** directly inside Odoo.

The module aims to improve transparency, efficiency, and traceability of employee travel management processes.

---

## 🚀 Features

- Employee travel / mission request management
- Request submission with travel details (destination, dates, purpose)
- Approval workflow (draft → submitted → approved / rejected)
- Tracking of mission status
- Automatic reference generation
- Integration with Odoo HR module
- Role-based access control
- User-friendly Odoo views (form, list)
  
### Fleet Integration
- Integration with **Odoo Fleet**
- Vehicle assignment to a mission 
- Track mission transportation details (vehicle, driver, notes)
- Improved visibility of vehicle usage for business trips

---

## 🛠️ Technologies Used

- Odoo
- Python
- XML (Odoo Views & Data)
- PostgreSQL

---

## 📂 Module Structure


travel_management/
│
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── travel_request.py
├── views/
│   └── travel_request_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── sequence.xml
└── static/
