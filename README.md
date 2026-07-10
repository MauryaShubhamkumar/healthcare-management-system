# 🏥 Healthcare Operation Management System

This is a **web-based Healthcare Operation Management System** built by me using **Streamlit** and **MySQL**, designed to streamline clinic and hospital workflows. It allows patients, doctors, and administrators to manage appointments, medical records, lab tests, billing, and transactions.

---

## 🚀 How to Clone and Run on Any System

Follow these simple steps to download, install, and run this project on your system (Windows, macOS, or Linux).

### 📋 Prerequisites
Ensure you have the following installed on your machine:
* **Python 3.9+** (Check using: `python --version`)
* **MySQL Server** (Check using: `mysql --version` or ensure the service is running)
* **Git** (Check using: `git --version`)

---

### Step 1: Clone the Repository
Open your terminal (macOS/Linux) or Command Prompt/PowerShell (Windows) and run:
```bash
git clone https://github.com/<your-username>/DBMS-Project.git
cd DBMS-Project
```

---

### Step 2: Install Python Libraries
Install the required packages using `pip`:
```bash
pip install streamlit pymysql cryptography
```

---

### Step 3: Setup the Database
1. Open your MySQL client (like MySQL Command Line Client, Workbench, or phpMyAdmin).
2. Create a new database:
   ```sql
   CREATE DATABASE IF NOT EXISTS ehr;
   USE ehr;
   ```
3. Import the database tables by importing the SQL file `ehr.sql` included in the root folder:
   ```sql
   SOURCE ehr.sql;
   ```
4. Open the [database.py](file:///d:/My%20Room/Healthcare%20MS/DBMS-Project/health-record/database.py#L9-L15) file in your text editor and update the database credentials dictionary to match your local MySQL username and password:
   ```python
   # In database.py
   db_config = {
       "host": "localhost",
       "user": "your_mysql_username",  # E.g. 'root'
       "password": "your_mysql_password", 
       "database": "ehr"
   }
   ```

---

### Step 4: Run the Application
Start the Streamlit application server by running the following command from the root folder:
```bash
streamlit run health-record/Electronic_Health_Record.py
```

Streamlit will compile the files and automatically open the application in your default web browser at:
`http://localhost:8501`

---

## 🛠️ Package Architecture

The codebase has been refactored into a clean, structured package under the `health-record/` directory:

```
DBMS-Project/
├── ehr.sql                       # Database Setup SQL Script
├── README.md                     # Central Documentation File
└── health-record/                # Main Application Package
    ├── Electronic_Health_Record.py # Main Entrypoint & Style Manager
    ├── database.py               # DB Connections & Auto-Schema Migrations
    ├── auth.py                   # Session State, Signup Validation & Login Diagnostics
    ├── appointments.py           # Appointment Scheduler, State Keys & Cascading Deletes
    ├── medical_records.py        # Diagnosis Sheets, Prescription History
    ├── lab_tests.py              # Test Allocation & Scoped Lab Result Logs
    └── billing_wallet.py         # Dynamic UPI QR Generation & Doctor Verification Queue
```

---

## ✨ Features by Role

### 👤 Patient Portal
* **Appointment Manager**: Schedule appointments using persistent calendar date & time inputs (selections do not reset on page redraws).
* **Medical Record Sheets**: Access chronological prescriptions, diagnostic results, consultation date/times, and physician notes.
* **Lab Results Hub**: View diagnostic lab test outcomes as soon as they are submitted by doctors.
* **Instant UPI Payments**: Pay invoices directly using dynamic BHIM/UPI QR codes pre-loaded with the bill details, then submit your **12-digit UPI UTR receipt number** and Payer Name for verification.
* **Transaction Ledger**: Access complete, detailed billing history for all paid and cleared invoices.

### 🩺 Doctor Panel
* **Consultation Workspace**: Create patient diagnosis logs and write clinical prescriptions tied directly to scheduled patient visits.
* **Invoice Generator**: Raise bills dynamically. The patient select box is filtered to only show patients with appointments under your schedule, and the medical records list shows only unbilled consultation records.
* **Verification Portal**: A dedicated **Verify Payments** tab listing patient payment submissions, showing UTR numbers, Payer Names, and diagnosis details with a one-click **Verify & Clear Bill** action.
* **Lab Test Coordinator**: Assign test panels (X-ray, blood panel, etc.) and submit diagnostic outcomes directly to the patient's records.

### 🛠️ Administrator Panel
* **Global Overviews**: Read-only oversight of all system appointments, diagnostics, and patient accounts.
* **Lab Packages**: Configure test packages, fees, and diagnostic parameters globally.
* **Financial Oversight**: Monitor clinic revenue ledgers.
