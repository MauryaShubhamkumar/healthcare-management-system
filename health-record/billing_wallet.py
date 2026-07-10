import streamlit as st
import pymysql
import urllib.parse
from datetime import datetime
from database import connect_to_db

# Configuration: Update this with your actual receiver UPI ID
RECEIVER_UPI_ID = "shubhamkumarmaurya155@okaxis"


# Check if wallet exists for a patient
def check_wallet_exists(patient_id):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = "SELECT WalletID FROM Wallets WHERE PatientID = %s"
    try:
        cursor.execute(query, (patient_id,))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        print(f"Error checking wallet: {e}")
        return False
    finally:
        conn.close()

# Create wallet for the patient
def create_wallet(patient_id, initial_balance=0.0):
    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()

    query = "INSERT INTO Wallets (PatientID, Balance) VALUES (%s, %s)"
    try:
        cursor.execute(query, (patient_id, initial_balance))
        conn.commit()
    except Exception as e:
        print(f"Error creating wallet: {e}")
    finally:
        conn.close()

# Fetch wallet balance
def fetch_wallet_balance(patient_id):
    conn = connect_to_db()
    if conn is None:
        return None
    cursor = conn.cursor()

    query = "SELECT Balance FROM Wallets WHERE PatientID = %s"
    try:
        cursor.execute(query, (patient_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error fetching wallet balance: {e}")
        return None
    finally:
        conn.close()

# Add money to wallet
def add_money_to_wallet(patient_id, amount):
    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()

    query = "UPDATE Wallets SET Balance = Balance + %s WHERE PatientID = %s"
    try:
        cursor.execute(query, (amount, patient_id))
        conn.commit()
    except Exception as e:
        print(f"Error adding money to wallet: {e}")
    finally:
        conn.close()

# Fetch unpaid/pending bills
def fetch_unpaid_bills(patient_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT BillingID, TotalAmount, PaymentStatus, TransactionID, PayerName 
        FROM Billing 
        WHERE PatientID = %s AND PaymentStatus != 'Completed'
    """
    try:
        cursor.execute(query, (patient_id,))
        bills = cursor.fetchall()
        return bills
    except Exception as e:
        print(f"Error fetching unpaid bills: {e}")
        return []
    finally:
        conn.close()

def pay_bill_with_wallet(patient_id, billing_id, amount):
    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        conn.begin()

        # Deduct from wallet balance
        deduct_query = "UPDATE Wallets SET Balance = Balance - %s WHERE PatientID = %s"
        cursor.execute(deduct_query, (amount, patient_id))

        # Generate a unique transaction ID
        transaction_id = int(datetime.now().timestamp())

        # Update billing status
        update_query = "UPDATE Billing SET PaymentStatus = 'Completed', TransactionID = %s WHERE BillingID = %s"
        cursor.execute(update_query, (transaction_id, billing_id))

        # Update admin wallet balance
        update_admin_query = "UPDATE AdminWallets SET Balance = Balance + %s WHERE WalletID = 1"
        cursor.execute(update_admin_query, (amount,))

        conn.commit()

    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Submit UPI QR Code Payment & Reference UTR for Verification
def pay_bill_with_upi(billing_id, utr_code, payer_name):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    try:
        conn.begin()

        # Update billing status with UPI UTR as the TransactionID and PayerName
        update_query = """
            UPDATE Billing 
            SET PaymentStatus = 'Pending Verification', TransactionID = %s, PayerName = %s 
            WHERE BillingID = %s
        """
        cursor.execute(update_query, (utr_code, payer_name, billing_id))
        conn.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Error during UPI Payment submission: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Fetch bills pending verification for Doctor panel
def fetch_pending_verification_bills():
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            b.BillingID,
            b.TotalAmount,
            b.TransactionID,
            b.PayerName,
            CONCAT(p.FirstName, ' ', p.LastName) AS PatientName,
            m.Diagnosis
        FROM 
            Billing b
        JOIN 
            Patient p ON b.PatientID = p.PatientID
        JOIN 
            MedicalRecord m ON b.RecordID = m.RecordID
        WHERE 
            b.PaymentStatus = 'Pending Verification'
        ORDER BY 
            b.BillingID ASC
    """
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching verification bills: {e}")
        return []
    finally:
        conn.close()

# Doctor verifies the UPI payment and completes the bill
def verify_and_clear_bill(billing_id, amount):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    try:
        conn.begin()

        # Mark bill as Completed
        cursor.execute("UPDATE Billing SET PaymentStatus = 'Completed' WHERE BillingID = %s", (billing_id,))

        # Add amount to admin wallet balance
        cursor.execute("UPDATE AdminWallets SET Balance = Balance + %s WHERE WalletID = 1", (amount,))

        conn.commit()
        return True
    except pymysql.MySQLError as err:
        print(f"Error verifying payment: {err}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Fetch unbilled medical records for a specific patient and doctor
def fetch_billable_records(patient_id, doctor_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT mr.RecordID, mr.Diagnosis, a.AppointmentDate
        FROM MedicalRecord mr
        JOIN Appointment a ON mr.AppointmentID = a.AppointmentID
        WHERE a.PatientID = %s 
          AND a.DoctorID = %s
          AND mr.RecordID NOT IN (SELECT RecordID FROM Billing)
    """
    try:
        cursor.execute(query, (patient_id, doctor_id))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching billable records: {e}")
        return []
    finally:
        conn.close()

# Wallet UI
def wallet_ui():
    st.title("Manage Your Wallet")

    patient_id = st.session_state.get("user_id", 1)
    
    wallet_exists = check_wallet_exists(patient_id)
    if not wallet_exists:
        st.warning("No wallet found for your account.")
        if st.button("Create Wallet"):
            create_wallet(patient_id)
            st.success("Wallet created successfully!")
        return

    balance = fetch_wallet_balance(patient_id)
    if balance is not None:
        st.write(f"### Current Wallet Balance: ₹{balance:.2f}")
    else:
        st.error("Failed to fetch wallet balance. Please try again later.")
        return

    st.subheader("Add Money to Wallet")
    add_amount = st.number_input("Enter amount to add:", min_value=0.0, step=100.0)
    if st.button("Add Money"):
        if add_amount > 0:
            add_money_to_wallet(patient_id, add_amount)
            st.success(f"₹{add_amount:.2f} added to your wallet.")
        else:
            st.warning("Please enter a valid amount.")

# Fetch billing history for a patient
def fetch_patient_billing_history(patient_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            b.BillingID, 
            b.TotalAmount, 
            b.PaymentStatus, 
            b.TransactionID, 
            b.PayerName, 
            m.Diagnosis,
            CONCAT(d.FirstName, ' ', d.LastName) AS DoctorName
        FROM 
            Billing b
        JOIN 
            MedicalRecord m ON b.RecordId = m.RecordID
        JOIN 
            Appointment a ON m.AppointmentID = a.AppointmentID
        JOIN 
            Doctor d ON a.DoctorID = d.DoctorID
        WHERE 
            b.PatientID = %s AND b.PaymentStatus = 'Completed'
        ORDER BY 
            b.BillingID DESC
    """
    try:
        cursor.execute(query, (patient_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching billing history: {e}")
        return []
    finally:
        conn.close()

# Pay Bill UI for Patients
def pay_bill_ui():
    st.title("Patient Billing Portal")

    tab1, tab2 = st.tabs(["💳 Outstanding Bills", "📜 Billing History"])

    patient_id = st.session_state.get("user_id", 1)

    with tab1:
        st.subheader("Pending Invoices")
        unpaid_bills = fetch_unpaid_bills(patient_id)

        if unpaid_bills:
            for bill in unpaid_bills:
                billing_id, total_amount, payment_status, transaction_id, payer_name = bill
                
                with st.container():
                    if payment_status == 'Pending':
                        st.markdown(f"""
                        <div style="background-color: #ffffff; color: #0f172a; padding: 1.2rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.8rem; border-left: 5px solid #ef4444;">
                            <span style="font-weight: 700; color: #0f172a; font-size: 1.05rem;">Billing ID: {billing_id}</span><br>
                            <span style="color: #475569; font-size: 0.85rem;">Status: <b style="color: #ef4444;">Unpaid / Pending</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write(f"**Total Amount Due:** ₹{total_amount:.2f}")
                        
                        # Generate dynamic UPI link and QR code URL
                        upi_link = f"upi://pay?pa={RECEIVER_UPI_ID}&pn=HealthCareMS&am={total_amount}&cu=INR&tr={billing_id}"
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(upi_link)}"
                        
                        col_qr, col_form = st.columns([1, 2])
                        with col_qr:
                            st.image(qr_url, width=170, caption="Scan with GPay/Paytm/PhonePe")
                          
                        with col_form:
                            st.markdown("##### Submit Payment Proof")
                            payer = st.text_input("Name of the Payer", key=f"payer_input_{billing_id}", placeholder="e.g. John Doe")
                            utr = st.text_input("UPI Reference / UTR Number (12 digits)", key=f"utr_input_{billing_id}", max_chars=12, placeholder="e.g. 403212345678")
                            
                            if st.button("Submit UPI Payment for Verification", key=f"upi_pay_{billing_id}"):
                                if not payer.strip():
                                    st.error("Please enter the name of the payer.")
                                elif len(utr) == 12 and utr.isdigit():
                                    success = pay_bill_with_upi(billing_id, utr, payer.strip())
                                    if success:
                                        st.success("Payment submitted successfully! Doctor will verify and clear it shortly.")
                                        st.rerun()
                                    else:
                                        st.error("Failed to process payment details. Please check the inputs and try again.")
                                else:
                                    st.error("Please enter a valid 12-digit numeric UPI Reference / UTR number.")
                    
                    elif payment_status == 'Pending Verification':
                        st.markdown(f"""
                        <div style="background-color: #f8fafc; color: #0f172a; padding: 1.2rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.8rem; border-left: 5px solid #eab308;">
                            <span style="font-weight: 700; color: #0f172a; font-size: 1.05rem;">Billing ID: {billing_id}</span><br>
                            <span style="color: #475569; font-size: 0.85rem;">Status: <b style="color: #eab308;">Pending Doctor Verification</b></span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write(f"**Total Amount:** ₹{total_amount:.2f}")
                        st.info(f"⏳ Verification in progress.\n\n* **Payer:** {payer_name}\n* **Transaction UTR:** `{transaction_id}`\n\nYour doctor will confirm receipt and clear the bill soon.")
                        
                st.markdown("---")
        else:
            st.success("🎉 You have no outstanding bills!")

    with tab2:
        st.subheader("Completed Payments")
        history = fetch_patient_billing_history(patient_id)
        if history:
            for bill in history:
                billing_id, total_amount, payment_status, transaction_id, payer_name, diagnosis, doctor_name = bill
                st.markdown(f"""
                <div style="background-color: #ffffff; color: #0f172a; padding: 1.2rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.8rem; border-left: 5px solid #22c55e;">
                    <span style="font-weight: 700; color: #0f172a; font-size: 1.05rem;">Bill ID: {billing_id} | Consultant: {doctor_name}</span><br>
                    <span style="color: #475569; font-size: 0.9rem;"><b>Diagnosis:</b> {diagnosis}</span><br>
                    <span style="color: #16a34a; font-weight: 700; font-size: 1.1rem;">Amount Paid: ₹{total_amount:.2f}</span><br>
                    <hr style="margin: 0.5rem 0; border: 0; border-top: 1px solid #f1f5f9;">
                    <span style="font-size: 0.9rem; color: #1e293b;">👤 <b>Payer Name:</b> {payer_name}</span><br>
                    <span style="font-size: 0.9rem; color: #1e293b;">💳 <b>UPI UTR / Reference ID:</b> <code style="background-color: #f1f5f9; padding: 0.15rem 0.45rem; border-radius: 4px; color: #0f172a; font-weight: bold;">{transaction_id}</code></span>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
        else:
            st.info("No billing history found.")

# Function to add billing
def add_billing(patient_id, record_id, total_amount, payment_status, transaction_id):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = """
        INSERT INTO Billing (PatientID, RecordID, TotalAmount, PaymentStatus, TransactionID)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (patient_id, record_id, total_amount, payment_status, transaction_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error creating billing record: {e}")
        return False
    finally:
        conn.close()

# UI for Doctor Billing Actions (Invoice creation & UPI verification)
def doctor_add_billing_ui():
    tab1, tab2 = st.tabs(["📝 Create Invoice", "✅ Verify Payments"])
    
    with tab1:
        st.subheader("Create Billing Record")

        conn = connect_to_db()
        if conn is None:
            return
        cursor = conn.cursor()
        
        doctor_id = st.session_state.get("user_id")
        try:
            cursor.execute("""
                SELECT DISTINCT p.PatientID, p.FirstName, p.LastName
                FROM Patient p
                JOIN Appointment a ON p.PatientID = a.PatientID
                WHERE a.DoctorID = %s
            """, (doctor_id,))
            patients = cursor.fetchall()
        except Exception as e:
            st.error(f"Error fetching patients: {e}")
            patients = []
        finally:
            conn.close()

        if not patients:
            st.warning("Ensure patients exist before generating an invoice.")
        else:
            patient_options = {f"{patient[1]} {patient[2]} (Patient ID: {patient[0]})": patient[0] for patient in patients}
            selected_patient = st.selectbox("Select a Patient", options=list(patient_options.keys()))
            patient_id = patient_options[selected_patient]

            # Fetch only the unbilled medical records for the selected patient and logged-in doctor
            doctor_id = st.session_state.get("user_id")
            records = fetch_billable_records(patient_id, doctor_id)

            if not records:
                st.info("No unbilled medical records found for this patient under your appointments.")
            else:
                record_options = {f"Record ID: {rec[0]} - Diagnosis: {rec[1]} (Date: {rec[2]})": rec[0] for rec in records}
                selected_record = st.selectbox("Select a Medical Record", options=list(record_options.keys()))
                record_id = record_options[selected_record]

                total_amount = st.number_input("Total Amount", min_value=0.0, format="%.2f")
                payment_status = st.selectbox("Payment Status", options=["Pending", "Completed"])
                
                # Default Transaction ID placeholder
                transaction_id = "0"
            
                if st.button("Create Billing Record"):
                    if total_amount > 0:
                        success = add_billing(patient_id, record_id, total_amount, payment_status, transaction_id)
                        if success:
                            st.success("Billing record created successfully!")
                            st.rerun()
                    else:
                        st.error("Total amount must be greater than zero.")

    with tab2:
        st.subheader("Verify Patient UPI Payments")
        pending_bills = fetch_pending_verification_bills()
        
        if not pending_bills:
            st.info("No payments waiting for verification.")
        else:
            for bill in pending_bills:
                billing_id, amount, utr, payer_name, patient_name, diagnosis = bill
                
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #ffffff; color: #0f172a; padding: 1.2rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.8rem; border-left: 5px solid #0d9488;">
                        <span style="font-weight: 700; color: #0f172a; font-size: 1.05rem;">Bill ID: {billing_id} | Patient: {patient_name}</span><br>
                        <span style="color: #475569; font-size: 0.9rem;"><b>Diagnosis:</b> {diagnosis}</span><br>
                        <span style="color: #0d9488; font-weight: 700; font-size: 1.1rem;">Amount: ₹{amount:.2f}</span><br>
                        <hr style="margin: 0.5rem 0; border: 0; border-top: 1px solid #f1f5f9;">
                        <span style="font-size: 0.9rem; color: #1e293b;">👤 <b>Payer Name:</b> {payer_name}</span><br>
                        <span style="font-size: 0.9rem; color: #1e293b;">💳 <b>UPI UTR / Reference ID:</b> <code style="background-color: #f1f5f9; padding: 0.15rem 0.45rem; border-radius: 4px; color: #0f172a; font-weight: bold;">{utr}</code></span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Verify & Clear Bill #{billing_id}", key=f"verify_{billing_id}"):
                        success = verify_and_clear_bill(billing_id, amount)
                        if success:
                            st.success(f"Payment verified. Bill #{billing_id} has been marked as Completed!")
                            st.rerun()
                        else:
                            st.error("Failed to verify bill. Please try again.")
                st.markdown("---")

# Streamlit UI to process payment
def admin_wallet_ui():
    st.subheader("Admin - Process Payment")

    admin_id = st.session_state.get("user_id")

    if admin_id is None:
        st.error("Admin ID not found! Please log in first.")
        return

    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        query = "SELECT Balance FROM AdminWallets WHERE id = %s"
        cursor.execute(query, (admin_id,))
        result = cursor.fetchone()
    except Exception as e:
        st.error(f"Error fetching admin wallet: {e}")
        result = None
    finally:
        conn.close()

    if result is None:
        st.warning("No wallet found for the admin.")
        if st.button("Create Admin Wallet"):
            create_admin_wallet(admin_id)
            st.success("Admin wallet created successfully!")
    else:
        admin_wallet_balance = result[0]
        st.write(f"### Current Admin Wallet Balance: ₹{admin_wallet_balance:.2f}")

        st.subheader("Add Money to Admin Wallet")
        add_amount = st.number_input("Enter amount to add:", min_value=0.0, step=100.0)
        if st.button("Add Money"):
            if add_amount > 0:
                add_money_to_admin_wallet(admin_id, add_amount)
                st.success(f"₹{add_amount:.2f} added to the admin wallet.")
            else:
                st.warning("Please enter a valid amount.")

# Function to create admin wallet
def create_admin_wallet(admin_id):
    if admin_id is None:
        st.error("Admin ID is not available to create the wallet.")
        return

    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()

    query = "INSERT INTO AdminWallets (id, Balance) VALUES (%s, %s)"
    try:
        cursor.execute(query, (admin_id, 0.0))
        conn.commit()
    except Exception as e:
        st.error(f"Error creating admin wallet: {e}")
    finally:
        conn.close()

# Function to add money to admin wallet
def add_money_to_admin_wallet(admin_id, amount):
    if admin_id is None:
        st.error("Admin ID is not available to add money to the wallet.")
        return

    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()

    query = "UPDATE AdminWallets SET Balance = Balance + %s WHERE id = %s"
    try:
        cursor.execute(query, (amount, admin_id))
        conn.commit()
    except Exception as e:
        st.error(f"Error adding money: {e}")
    finally:
        conn.close()

def fetch_billing_records_for_admin():
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            b.BillingID,
            CONCAT(p.FirstName, ' ', p.LastName) AS PatientName,
            b.TotalAmount,
            b.PaymentStatus,
            b.TransactionID,
            m.Diagnosis
        FROM 
            Billing b
        JOIN 
            Patient p ON b.PatientID = p.PatientID
        JOIN 
            MedicalRecord m ON b.RecordID = m.RecordID
        ORDER BY 
            b.BillingID DESC
    """
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception as e:
        st.error(f"Error fetching billing records: {e}")
        return []
    finally:
        conn.close()

def view_billing_record_ui():
    st.subheader("Admin - View All Billing Records")

    records = fetch_billing_records_for_admin()

    if records:
        st.write("### Billing Records")
        billing_data = [
            {
                "Billing ID": record[0],
                "Patient Name": record[1],
                "Total Amount": f"${record[2]:,.2f}",
                "Payment Status": record[3],
                "Transaction ID": record[4],
                "Diagnosis": record[5],
            }
            for record in records
        ]
        st.dataframe(billing_data)
    else:
        st.info("No billing records found.")
