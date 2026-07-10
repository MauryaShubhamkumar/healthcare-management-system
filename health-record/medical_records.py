import streamlit as st
from database import connect_to_db
from appointments import get_doctor_appointments

def add_medical_record(appointment_id, prescription, diagnosis, test_taken):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = """
        INSERT INTO MedicalRecord (AppointmentID, Prescription, Diagnosis, TestTaken)
        VALUES (%s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (appointment_id, prescription, diagnosis, test_taken))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding medical record: {e}")
        return False
    finally:
        conn.close()

def add_medical_record_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] == "Patient":
        st.warning("You must log in as a doctor to create medical records.")
        return

    st.subheader("Create Medical Record")

    doctor_id = st.session_state.get("user_id")

    appointments = get_doctor_appointments(doctor_id)

    if not appointments:
        st.warning("No appointments found for this doctor.")
        return

    appointment_options = {
        f"Appointment ID: {app[0]}, Patient: {app[1]}, Date: {app[2]}": app[0]
        for app in appointments
    }
    selected_appointment = st.selectbox("Select an Appointment", options=appointment_options.keys())
    appointment_id = appointment_options[selected_appointment]

    prescription = st.text_area("Prescription")
    diagnosis = st.text_area("Diagnosis")
    test_taken = st.checkbox("Test Taken")

    if st.button("Create Medical Record"):
        success = add_medical_record(appointment_id, prescription, diagnosis, test_taken)
        if success:
            st.success("Medical record created successfully!")
        else:
            st.error("Failed to create medical record.")

def view_medical_records(appointment_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT RecordID, Prescription, Diagnosis, TestTaken
        FROM MedicalRecord
        WHERE AppointmentID = %s
    """
    try:
        cursor.execute(query, (appointment_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()

def view_medical_records_for_doctor(doctor_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            MedicalRecord.RecordID, 
            CONCAT(Patient.FirstName, ' ', Patient.LastName) AS PatientName, 
            Appointment.AppointmentDate, 
            MedicalRecord.Prescription, 
            MedicalRecord.Diagnosis, 
            MedicalRecord.TestTaken
        FROM 
            MedicalRecord
        JOIN 
            Appointment ON MedicalRecord.AppointmentID = Appointment.AppointmentID
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        WHERE 
            Appointment.DoctorID = %s;
    """
    try:
        cursor.execute(query, (doctor_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()

def view_medical_records_for_patient(patient_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            mr.RecordID, 
            CONCAT(d.FirstName, ' ', d.LastName) AS DoctorName, 
            a.AppointmentDate, 
            mr.Prescription, 
            mr.Diagnosis, 
            mr.TestTaken
        FROM 
            MedicalRecord mr
        JOIN 
            Appointment a ON mr.AppointmentID = a.AppointmentID
        JOIN 
            Doctor d ON a.DoctorID = d.DoctorID
        WHERE 
            a.PatientID = %s
        ORDER BY 
            a.AppointmentDate DESC;
    """
    try:
        cursor.execute(query, (patient_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records for patient: {e}")
        return []
    finally:
        conn.close()

def view_medical_records_ui():
    if not st.session_state.get("logged_in"):
        st.warning("You must log in to view medical records.")
        return

    st.subheader("View Medical Records")

    user_id = st.session_state.get("user_id")
    role = st.session_state.get("role")

    if role == "Patient":
        records = view_medical_records_for_patient(user_id)
        if records:
            st.write("### Your Medical Records History")
            for record in records:
                st.markdown(f"""
                <div style="background-color: #f8fafc; color: #0f172a; padding: 1.2rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.8rem; border-left: 5px solid #0d9488;">
                    <span style="font-weight: 700; font-size: 1.1rem; color: #0f172a;">Consultation Date: {record[2]}</span><br>
                    <span style="font-size: 0.95rem; color: #475569;">👨‍⚕️ <b>Doctor:</b> {record[1]}</span><br>
                    <span style="font-size: 0.95rem; color: #1e293b;">🩺 <b>Diagnosis:</b> {record[4]}</span><br>
                    <span style="font-size: 0.95rem; color: #1e293b;">💊 <b>Prescription:</b> {record[3]}</span><br>
                    <span style="font-size: 0.95rem; color: #1e293b;">🔬 <b>Lab Tests Ordered:</b> {'Yes' if record[5] else 'No'}</span>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
        else:
            st.info("No medical records found for you yet.")

    elif role == "Doctor":
        records = view_medical_records_for_doctor(user_id)
        if records:
            st.write("### Medical Records")
            for record in records:
                st.markdown(f"""
                <div style="background-color: #ffffff; color: #0f172a; padding: 1.2rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.8rem; border-left: 5px solid #0ea5e9;">
                    <span style="font-weight: 700; font-size: 1.1rem; color: #0f172a;">Record ID: {record[0]}</span><br>
                    <span style="font-size: 0.95rem; color: #475569;">👤 <b>Patient Name:</b> {record[1]}</span><br>
                    <span style="font-size: 0.95rem; color: #475569;">📅 <b>Date:</b> {record[2]}</span><br>
                    <span style="font-size: 0.95rem; color: #1e293b;">🩺 <b>Diagnosis:</b> {record[4]}</span><br>
                    <span style="font-size: 0.95rem; color: #1e293b;">💊 <b>Prescription:</b> {record[3]}</span><br>
                    <span style="font-size: 0.95rem; color: #1e293b;">🔬 <b>Test Taken:</b> {'Yes' if record[5] else 'No'}</span>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
        else:
            st.warning("No medical records found for this doctor.")

def update_medical_record(record_id, prescription, diagnosis, test_taken):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = """
        UPDATE MedicalRecord
        SET Prescription = %s, Diagnosis = %s, TestTaken = %s
        WHERE RecordID = %s
    """
    try:
        cursor.execute(query, (record_id, prescription, diagnosis, test_taken))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating medical record: {e}")
        return False
    finally:
        conn.close()

def get_doctor_medical_records(doctor_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            MedicalRecord.RecordID, 
            CONCAT(Patient.FirstName, ' ', Patient.LastName) AS PatientName, 
            Appointment.AppointmentDate, 
            MedicalRecord.Prescription, 
            MedicalRecord.Diagnosis, 
            MedicalRecord.TestTaken
        FROM 
            MedicalRecord
        JOIN 
            Appointment ON MedicalRecord.AppointmentID = Appointment.AppointmentID
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        WHERE 
            Appointment.DoctorID = %s;
    """
    try:
        cursor.execute(query, (doctor_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()

def update_medical_record_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] == "Patient":
        st.warning("You must log in as a doctor to update medical records.")
        return

    st.subheader("Update Medical Record")

    doctor_id = st.session_state.get("user_id")

    medical_records = get_doctor_medical_records(doctor_id)

    if not medical_records:
        st.warning("No medical records found for this doctor.")
        return

    record_options = {
        f"Record ID: {rec[0]}, Patient: {rec[1]}, Date: {rec[2]}": rec
        for rec in medical_records
    }
    selected_record = st.selectbox("Select a Medical Record", options=record_options.keys())

    record_id, patient_name, appointment_date, existing_prescription, existing_diagnosis, existing_test_taken = record_options[selected_record]

    st.write(f"**Patient Name:** {patient_name}")
    st.write(f"**Appointment Date:** {appointment_date}")
    prescription = st.text_area("Prescription", value=existing_prescription)
    diagnosis = st.text_area("Diagnosis", value=existing_diagnosis)
    test_taken = st.checkbox("Test Taken", value=existing_test_taken)

    if st.button("Update Medical Record"):
        success = update_medical_record(record_id, prescription, diagnosis, test_taken)
        if success:
            st.success("Medical record updated successfully!")
        else:
            st.error("Failed to update medical record.")

def delete_medical_record(record_id):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = """
        DELETE FROM MedicalRecord
        WHERE RecordID = %s
    """
    try:
        cursor.execute(query, (record_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting medical record: {e}")
        return False
    finally:
        conn.close()

def delete_medical_record_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Admin":
        st.warning("You must log in as an admin to delete medical records.")
        return

    st.subheader("Delete Medical Record")

    record_id = st.number_input("Record ID", min_value=1, step=1)

    if st.button("Delete Medical Record"):
        success = delete_medical_record(record_id)
        if success:
            st.success("Medical record deleted successfully!")
        else:
            st.error("Failed to delete medical record.")

def view_medical_records_for_admin():
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            MedicalRecord.RecordID, 
            CONCAT(Patient.FirstName, ' ', Patient.LastName) AS PatientName, 
            Appointment.AppointmentDate, 
            CONCAT(Doctor.FirstName, ' ', Doctor.LastName) AS DoctorName, 
            MedicalRecord.Prescription, 
            MedicalRecord.Diagnosis, 
            MedicalRecord.TestTaken
        FROM 
            MedicalRecord
        JOIN 
            Appointment ON MedicalRecord.AppointmentID = Appointment.AppointmentID
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        JOIN 
            Doctor ON Appointment.DoctorID = Doctor.DoctorID
        ORDER BY 
            Appointment.AppointmentDate DESC;
    """
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching medical records: {e}")
        return []
    finally:
        conn.close()

def view_medical_records_admin_ui():
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Admin":
        st.warning("You must log in as an admin to view medical records.")
        return

    st.subheader("Admin - View All Medical Records")

    records = view_medical_records_for_admin()

    if records:
        st.write("### Medical Records")
        medical_data = [
            {
                "Record ID": record[0],
                "Patient Name": record[1],
                "Appointment Date": record[2],
                "Assigned Doctor": record[3],
                "Prescription": record[4],
                "Diagnosis": record[5],
                "Test Taken": "Yes" if record[6] else "No",
            }
            for record in records
        ]
        st.dataframe(medical_data)

        with st.expander("Filter Records"):
            filter_type = st.selectbox("Filter by", ["None", "Patient Name", "Doctor Name", "Appointment Date"])
            if filter_type == "Patient Name":
                patient_name = st.text_input("Enter Patient Name")
                if patient_name:
                    filtered_data = [
                        record for record in medical_data
                        if patient_name.lower() in record["Patient Name"].lower()
                    ]
                    st.dataframe(filtered_data)
            elif filter_type == "Doctor Name":
                doctor_name = st.text_input("Enter Doctor Name")
                if doctor_name:
                    filtered_data = [
                        record for record in medical_data
                        if doctor_name.lower() in record["Assigned Doctor"].lower()
                    ]
                    st.dataframe(filtered_data)
            elif filter_type == "Appointment Date":
                date = st.date_input("Select Appointment Date")
                if date:
                    filtered_data = [
                        record for record in medical_data
                        if record["Appointment Date"] == str(date)
                    ]
                    st.dataframe(filtered_data)
    else:
        st.warning("No medical records found.")

def medical_record_operations_ui():
    st.subheader("Manage Medical Records")

    if st.session_state["role"] == "Patient":
        operations = ["View"]
    elif st.session_state["role"] == "Doctor":
        operations = ["Create", "View", "Update"]
    elif st.session_state["role"] == "Admin":
        operations = ["View"]
    else:
        st.warning("Invalid role. Please log in again.")
        return

    operation = st.radio("Select Operation", operations)

    if operation == "Create":
        add_medical_record_ui()
    elif operation == "View" and st.session_state["role"] != "Admin":
        view_medical_records_ui()
    elif operation == "View" and st.session_state["role"] == "Admin":
        view_medical_records_admin_ui()
    elif operation == "Update":
        update_medical_record_ui()
    elif operation == "Delete":
        delete_medical_record_ui()
