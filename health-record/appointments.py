import streamlit as st
from datetime import datetime
from database import connect_to_db
from auth import fetch_doctors

def create_appointment(patient_id, doctor_id, date, time):
    conn = connect_to_db()
    if conn is None:
        return False
        
    cursor = conn.cursor()
    query = """
        INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime)
        VALUES (%s, %s, %s, %s)
    """
    try:
        # Convert date and time to strings if they aren't already
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else date
        time_str = time.strftime('%H:%M:%S') if hasattr(time, 'strftime') else time
        
        cursor.execute(query, (patient_id, doctor_id, date_str, time_str))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating appointment: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def create_appointment_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to create an appointment.")
        return

    st.subheader("Create an Appointment")

    # Fetch and display doctors
    doctors = fetch_doctors()
    if not doctors:
        st.warning("No doctors available.")
        return

    doctor_options = {f"{doc[1]} {doc[2]} ({doc[3]})": doc[0] for doc in doctors}
    selected_doctor = st.selectbox("Select a Doctor", options=list(doctor_options.keys()))
    doctor_id = doctor_options[selected_doctor]

    # Appointment Details
    current_date = datetime.now().date()
    date = st.date_input("Select Appointment Date", 
                        min_value=current_date,
                        value=current_date,
                        key="create_appt_date")
    
    time = st.time_input("Select Appointment Time", 
                        key="create_appt_time")

    if st.button("Create Appointment"): 
        if date < current_date:
            st.error("Please select a future date.")
            return
            
        try:
            patient_id = st.session_state["user_id"]
            success = create_appointment(patient_id, doctor_id, date, time)
            if success:
                st.success("Appointment created successfully!")
            else:
                st.error("Failed to create appointment. Please try again.")
        except Exception as e:
            st.error(f"Error creating appointment: {str(e)}")
            print(f"Detailed error: {e}")

def fetch_patient_appointments(patient_id):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            a.AppointmentID, 
            a.AppointmentDate, 
            a.AppointmentTime, 
            d.FirstName AS DoctorFirstName, 
            d.LastName AS DoctorLastName, 
            d.Specialization
        FROM 
            Appointment a
        JOIN 
            Doctor d ON a.DoctorID = d.DoctorID
        WHERE 
            a.PatientID = %s
        ORDER BY 
            a.AppointmentDate DESC, a.AppointmentTime DESC
    """
    try:
        cursor.execute(query, (patient_id,))
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []
    finally:
        conn.close()

def view_patient_appointments_ui():
    st.subheader("Your Appointments")

    patient_id = st.session_state["user_id"]
    appointments = fetch_patient_appointments(patient_id)

    if not appointments:
        st.info("You have no appointments.")
        return

    st.write("### Your Appointments (Latest at the Top)")
    appointment_data = [
        {
            "Appointment ID": appt[0],
            "Date": appt[1],
            "Time": appt[2],
            "Doctor": f"{appt[3]} {appt[4]}",
            "Specialization": appt[5],
        }
        for appt in appointments
    ]
    st.dataframe(appointment_data)

def fetch_doctor_appointments(doctor_id):
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            a.AppointmentID, 
            a.AppointmentDate, 
            a.AppointmentTime, 
            p.FirstName AS PatientFirstName, 
            p.LastName AS PatientLastName, 
            p.Email AS PatientEmail
        FROM 
            Appointment a
        JOIN 
            Patient p ON a.PatientID = p.PatientID
        WHERE 
            a.DoctorID = %s
        ORDER BY 
            a.AppointmentDate DESC, a.AppointmentTime DESC
    """
    try:
        cursor.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []
    finally:
        conn.close()

def view_doctor_appointments_ui():
    st.subheader("Your Appointments")

    if not st.session_state.get("logged_in") or st.session_state["role"] != "Doctor":
        st.warning("You must log in as a doctor to view your appointments.")
        return

    doctor_id = st.session_state["user_id"]
    appointments = fetch_doctor_appointments(doctor_id)

    if not appointments:
        st.info("You have no appointments scheduled.")
        return

    st.write("### Your Appointments (Latest at the Top)")
    appointment_data = [
        {
            "Appointment ID": appt[0],
            "Date": appt[1],
            "Time": appt[2],
            "Patient": f"{appt[3]} {appt[4]}",
            "Patient Email": appt[5],
        }
        for appt in appointments
    ]
    st.dataframe(appointment_data)

def update_appointment(appointment_id, new_date, new_time):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()
    query = """
        UPDATE Appointment
        SET AppointmentDate = %s, AppointmentTime = %s
        WHERE AppointmentID = %s
    """
    try:
        cursor.execute(query, (new_date, new_time, appointment_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating appointment: {e}")
        return False
    finally:
        conn.close()

def update_appointment_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to manage appointments.")
        return

    st.subheader("Update an Appointment")

    patient_id = st.session_state["user_id"]
    appointments = fetch_patient_appointments(patient_id)

    if not appointments:
        st.info("You have no appointments to update.")
        return

    appointment_options = {
        f"Appointment {appt[0]}: {appt[1]} {appt[2]} with Dr. {appt[3]} {appt[4]} ({appt[5]})": appt[0]
        for appt in appointments
    }
    selected_appointment = st.selectbox("Select an Appointment", list(appointment_options.keys()))
    appointment_id = appointment_options[selected_appointment]

    current_date = datetime.now().date()
    new_date = st.date_input("New Appointment Date", min_value=current_date, key="update_appt_date")
    new_time = st.time_input("New Appointment Time", key="update_appt_time")

    if st.button("Update Appointment"):
        if new_date < current_date:
            st.error("Please select a future date.")
            return

        success = update_appointment(appointment_id, new_date, new_time)
        if success:
            st.success("Appointment updated successfully!")
        else:
            st.error("Failed to update appointment. Please try again.")

def delete_appointment(appointment_id):
    conn = connect_to_db()
    if conn is None:
        return False

    cursor = conn.cursor()
    try:
        conn.begin()

        # 1. Fetch related MedicalRecord (RecordID) list if they exist
        cursor.execute("SELECT RecordID FROM MedicalRecord WHERE AppointmentID = %s", (appointment_id,))
        medical_records = cursor.fetchall()

        for record_res in medical_records:
            record_id = record_res[0]
            # 2. Delete test results associated with this RecordID
            cursor.execute("DELETE FROM TestResults WHERE RecordID = %s", (record_id,))
            # 3. Delete billing records associated with this RecordId
            cursor.execute("DELETE FROM Billing WHERE RecordId = %s", (record_id,))
            # 4. Delete the medical record itself
            cursor.execute("DELETE FROM MedicalRecord WHERE RecordID = %s", (record_id,))

        # 5. Delete the appointment
        cursor.execute("DELETE FROM Appointment WHERE AppointmentID = %s", (appointment_id,))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting appointment: {e}")
        return False
    finally:
        conn.close()

def delete_appointment_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to manage appointments.")
        return

    st.subheader("Delete an Appointment")

    patient_id = st.session_state["user_id"]
    appointments = fetch_patient_appointments(patient_id)

    if not appointments:
        st.info("You have no appointments to delete.")
        return

    appointment_options = {
        f"Appointment {appt[0]}: {appt[1]} {appt[2]} with Dr. {appt[3]} {appt[4]} ({appt[5]})": appt[0]
        for appt in appointments
    }
    selected_appointment = st.selectbox("Select an Appointment to Delete", list(appointment_options.keys()))
    appointment_id = appointment_options[selected_appointment]

    if st.button("Delete Appointment"):
        success = delete_appointment(appointment_id)
        if success:
            st.success("Appointment deleted successfully!")
        else:
            st.error("Failed to delete appointment. Please try again.")

def fetch_all_appointments():
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT 
            a.AppointmentID, 
            a.AppointmentDate, 
            a.AppointmentTime, 
            p.FirstName AS PatientFirstName, 
            p.LastName AS PatientLastName, 
            p.Email AS PatientEmail, 
            d.FirstName AS DoctorFirstName, 
            d.LastName AS DoctorLastName, 
            d.Specialization
        FROM 
            Appointment a
        JOIN 
            Patient p ON a.PatientID = p.PatientID
        JOIN 
            Doctor d ON a.DoctorID = d.DoctorID
        ORDER BY 
            a.AppointmentDate DESC, a.AppointmentTime DESC
    """
    try:
        cursor.execute(query)
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        st.error(f"Error fetching appointments: {e}")
        return []
    finally:
        conn.close()

def admin_view_patient_appointments_ui():
    st.subheader("Admin - All Appointments")
    
    appointments = fetch_all_appointments()

    if not appointments:
        st.info("No appointments found.")
        return

    st.write("### All Appointments (Latest at the Top)")
    appointment_data = [
        {
            "Appointment ID": appt[0],
            "Date": appt[1],
            "Time": appt[2],
            "Patient": f"{appt[3]} {appt[4]}",
            "Patient Email": appt[5],
            "Doctor": f"{appt[6]} {appt[7]}",
            "Specialization": appt[8],
        }
        for appt in appointments
    ]
    st.dataframe(appointment_data)

    with st.expander("Filter Appointments"):
        filter_type = st.selectbox("Filter by", ["None", "Patient Name", "Doctor Name", "Date"])
        if filter_type == "Patient Name":
            patient_name = st.text_input("Enter Patient Name")
            if patient_name:
                filtered_data = [
                    appt for appt in appointment_data
                    if patient_name.lower() in appt["Patient"].lower()
                ]
                st.dataframe(filtered_data)
        elif filter_type == "Doctor Name":
            doctor_name = st.text_input("Enter Doctor Name")
            if doctor_name:
                filtered_data = [
                    appt for appt in appointment_data
                    if doctor_name.lower() in appt["Doctor"].lower()
                ]
                st.dataframe(filtered_data)
        elif filter_type == "Date":
            date = st.date_input("Select Date")
            if date:
                filtered_data = [
                    appt for appt in appointment_data
                    if appt["Date"] == str(date)
                ]
                st.dataframe(filtered_data)

def appointment_operations_ui():
    st.subheader("Manage Your Appointments")

    if st.session_state["role"] == "Patient":
        operations = ["Create", "View", "Update", "Delete"]
    elif st.session_state["role"] == "Admin":
        operations = ["View"]
    elif st.session_state["role"] == "Doctor":
        operations = ["View"]
    else:
        st.warning("Invalid role. Please log in again.")
        return

    operation = st.radio("Select Operation", operations)

    if operation == "Create":
        create_appointment_ui()
    elif operation == "View" and st.session_state["role"] == "Patient":
        view_patient_appointments_ui()
    elif operation == "View" and st.session_state["role"] == "Admin":
        admin_view_patient_appointments_ui()   
    elif operation == "View" and st.session_state["role"] == "Doctor":
        view_doctor_appointments_ui()
    elif operation == "Update":
        update_appointment_ui()
    elif operation == "Delete":
        delete_appointment_ui()

def get_doctor_appointments(doctor_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            Appointment.AppointmentID, 
            Patient.FirstName, 
            Appointment.AppointmentDate
        FROM 
            Appointment
        JOIN 
            Patient ON Appointment.PatientID = Patient.PatientID
        WHERE 
            Appointment.DoctorID = %s
    """
    try:
        cursor.execute(query, (doctor_id,))
        appointments = cursor.fetchall()
        return appointments
    except Exception as e:
        print(f"Error fetching doctor appointments: {e}")
        return []
    finally:
        conn.close()
