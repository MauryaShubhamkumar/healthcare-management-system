import streamlit as st
from datetime import datetime
from database import connect_to_db

# Function to add a lab test
def add_lab_test(test_name, description, cost):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = """
        INSERT INTO LabTests (TestName, Description, Cost)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.execute(query, (test_name, description, cost))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding lab test: {e}")
        return False
    finally:
        conn.close()

# UI for adding a lab test
def add_lab_test_ui():
    st.subheader("Add Lab Test")

    test_name = st.text_input("Test Name")
    description = st.text_area("Description")
    cost = st.number_input("Cost", min_value=0.0, step=0.01)

    if st.button("Add Lab Test"):
        success = add_lab_test(test_name, description, cost)
        if success:
            st.success("Lab test added successfully!")
        else:
            st.error("Failed to add lab test.")

# Function to view all lab tests
def view_lab_tests():
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = "SELECT LabTestID, TestName, Description, Cost, CreatedAt, UpdatedAt FROM LabTests"
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching lab tests: {e}")
        return []
    finally:
        conn.close()

# UI for viewing lab tests
def view_lab_tests_ui():
    st.subheader("View Lab Tests")

    records = view_lab_tests()
    if records:
        for record in records:
            st.write(f"**Lab Test ID:** {record[0]}")
            st.write(f"**Test Name:** {record[1]}")
            st.write(f"**Description:** {record[2]}")
            st.write(f"**Cost:** {record[3]}")
            st.write(f"**Created At:** {record[4]}")
            st.write(f"**Updated At:** {record[5]}")
            st.write("---")
    else:
        st.warning("No lab tests found.")

# Function to update a lab test
def update_lab_test(lab_test_id, test_name, description, cost):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = """
        UPDATE LabTests
        SET TestName = %s, Description = %s, Cost = %s, UpdatedAt = %s
        WHERE LabTestID = %s
    """
    try:
        cursor.execute(query, (test_name, description, cost, datetime.now(), lab_test_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating lab test: {e}")
        return False
    finally:
        conn.close()

# UI for updating a lab test
def update_lab_test_ui():
    st.subheader("Update Lab Test")

    records = view_lab_tests()
    if not records:
        st.warning("No lab tests found to update.")
        return

    lab_test_options = {f"Lab Test ID: {rec[0]}, Name: {rec[1]}": rec for rec in records}
    selected_lab_test = st.selectbox("Select a Lab Test", options=lab_test_options.keys())

    lab_test_id, test_name, description, cost, _, _ = lab_test_options[selected_lab_test]

    test_name = st.text_input("Test Name", value=test_name)
    description = st.text_area("Description", value=description)
    cost = st.number_input("Cost", value=float(cost), min_value=0.0, step=0.01)

    if st.button("Update Lab Test"):
        success = update_lab_test(lab_test_id, test_name, description, cost)
        if success:
            st.success("Lab test updated successfully!")
        else:
            st.error("Failed to update lab test.")

# Function to delete a lab test
def delete_lab_test(lab_test_id):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = "DELETE FROM LabTests WHERE LabTestID = %s"
    try:
        cursor.execute(query, (lab_test_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting lab test: {e}")
        return False
    finally:
        conn.close()

# UI for deleting a lab test
def delete_lab_test_ui():
    st.subheader("Delete Lab Test")

    records = view_lab_tests()
    if not records:
        st.warning("No lab tests found to delete.")
        return

    lab_test_options = {f"Lab Test ID: {rec[0]}, Name: {rec[1]}": rec[0] for rec in records}
    selected_lab_test = st.selectbox("Select a Lab Test", options=lab_test_options.keys())

    lab_test_id = lab_test_options[selected_lab_test]

    if st.button("Delete Lab Test"):
        success = delete_lab_test(lab_test_id)
        if success:
            st.success("Lab test deleted successfully!")
        else:
            st.error("Failed to delete lab test.")

# Main UI for Lab Test operations (Admin / Generic)
def lab_test_operations_ui():
    st.subheader("Manage Lab Tests")

    operations = ["Create", "View", "Update", "Delete"]
    operation = st.radio("Select Operation", operations)

    if operation == "Create":
        add_lab_test_ui()
    elif operation == "View":
        view_lab_tests_ui()
    elif operation == "Update":
        update_lab_test_ui()
    elif operation == "Delete":
        delete_lab_test_ui()

def add_test_results(record_id, test_name, test_result):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = """
        INSERT INTO TestResults (RecordID, TestName, Result)
        VALUES (%s, %s, %s)
    """
    try:
        cursor.execute(query, (record_id, test_name, test_result))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding test results: {e}")
        return False
    finally:
        conn.close()

def add_test_results_ui():
    if not st.session_state.get("logged_in") or st.session_state["role"] != "Doctor":
        st.warning("You must log in as a doctor to add test results.")
        return

    st.subheader("Add Test Results")

    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        # Fixed the JOIN issue by joining through Appointment table
        cursor.execute("""
            SELECT MedicalRecord.RecordID, Patient.FirstName, Patient.LastName
            FROM MedicalRecord
            INNER JOIN Appointment ON MedicalRecord.AppointmentID = Appointment.AppointmentID
            INNER JOIN Patient ON Appointment.PatientID = Patient.PatientID
        """)
        records = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching medical records: {e}")
        conn.close()
        return
    finally:
        conn.close()

    if not records:
        st.warning("No medical records available.")
        return

    record_options = {f"Record {r[0]} - {r[1]} {r[2]}": r[0] for r in records}
    selected_record = st.selectbox("Select Medical Record", options=list(record_options.keys()))

    test_name = st.text_input("Enter Test Name")
    test_result = st.text_area("Enter Test Result")

    if st.button("Add Test Results"):
        record_id = record_options[selected_record]
        success = add_test_results(record_id, test_name, test_result)

        if success:
            st.success("Test results added successfully!")
        else:
            st.error("Failed to add test results. Please try again.")

def get_appointments_with_tests(doctor_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT mr.AppointmentID, mr.RecordID, CONCAT(p.FirstName, ' ', p.LastName) AS PatientName, a.AppointmentDate
        FROM MedicalRecord mr
        JOIN Appointment a ON mr.AppointmentID = a.AppointmentID
        JOIN Patient p ON a.PatientID = p.PatientID
        WHERE mr.TestTaken = TRUE AND a.DoctorID = %s
    """
    try:
        cursor.execute(query, (doctor_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching appointments with tests: {e}")
        return []
    finally:
        conn.close()

def add_lab_tests_for_appointment(record_id, lab_tests):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    try:
        for test_id in lab_tests:
            query = """
                INSERT INTO TestResults (LabTestID, RecordID)
                VALUES (%s, %s)
            """
            cursor.execute(query, (test_id, record_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding lab tests: {e}")
        return False
    finally:
        conn.close()

def doctor_assign_tests_ui():
    st.subheader("Assign Lab Tests to Patient")

    doctor_id = st.session_state.get("user_id")
    appointments = get_appointments_with_tests(doctor_id)
    if not appointments:
        st.warning("No appointments with pending tests.")
        return

    appointment_options = {f"Patient: {app[2]} | Appointment ID: {app[0]} | Record ID: {app[1]} (Date: {app[3]})": app[1] for app in appointments}
    selected_record = st.selectbox("Select an Appointment", options=appointment_options.keys())
    record_id = appointment_options[selected_record]

    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT LabTestID, TestName FROM LabTests")
        lab_tests = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching available tests: {e}")
        lab_tests = []
    finally:
        conn.close()

    if not lab_tests:
        st.warning("No lab tests available.")
        return

    test_options = {f"{test[1]} (ID: {test[0]})": test[0] for test in lab_tests}
    selected_tests = st.multiselect("Select Lab Tests", options=test_options.keys())

    if st.button("Assign Tests"):
        if selected_tests:
            lab_test_ids = [test_options[test] for test in selected_tests]
            success = add_lab_tests_for_appointment(record_id, lab_test_ids)
            if success:
                st.success("Lab tests assigned successfully!")
        else:
            st.error("No tests selected.")

def add_test_result(test_id, result):
    conn = connect_to_db()
    if conn is None:
        return False
    cursor = conn.cursor()

    query = "UPDATE TestResults SET Result = %s WHERE TestID = %s"
    try:
        cursor.execute(query, (result, test_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating test result: {e}")
        return False
    finally:
        conn.close()

def doctor_add_results_ui():
    st.subheader("Add Lab Test Results")

    doctor_id = st.session_state.get("user_id")

    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT tr.TestID, lt.TestName, tr.RecordID, tr.Result, CONCAT(p.FirstName, ' ', p.LastName) AS PatientName
            FROM TestResults tr
            JOIN LabTests lt ON tr.LabTestID = lt.LabTestID
            JOIN MedicalRecord mr ON tr.RecordID = mr.RecordID
            JOIN Appointment a ON mr.AppointmentID = a.AppointmentID
            JOIN Patient p ON a.PatientID = p.PatientID
            WHERE tr.Result IS NULL AND a.DoctorID = %s
        """, (doctor_id,))
        pending_tests = cursor.fetchall()
    except Exception as e:
        st.error(f"Error fetching pending tests: {e}")
        pending_tests = []
    finally:
        conn.close()

    if not pending_tests:
        st.warning("No pending lab tests.")
        return

    test_options = {f"{test[1]} for Patient: {test[4]} (Record ID: {test[2]})": test for test in pending_tests}
    selected_test = st.selectbox("Select a Test", options=test_options.keys())
    test_id, test_name, record_id, _, _ = test_options[selected_test]

    result = st.text_area(f"Enter Result for {test_name}")
    if st.button("Submit Result"):
        if result.strip():
            success = add_test_result(test_id, result)
            if success:
                st.success("Result added successfully!")
                st.rerun()
        else:
            st.error("Result cannot be empty.")

def view_patient_tests(patient_id):
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()

    query = """
        SELECT 
            a.AppointmentID,
            a.AppointmentDate,
            CONCAT(d.FirstName, ' ', d.LastName) AS DoctorName,
            lt.TestName,
            tr.Result
        FROM TestResults tr
        JOIN MedicalRecord mr ON tr.RecordID = mr.RecordID
        JOIN LabTests lt ON tr.LabTestID = lt.LabTestID
        JOIN Appointment a ON mr.AppointmentID = a.AppointmentID
        JOIN Doctor d ON a.DoctorID = d.DoctorID
        WHERE a.PatientID = %s
    """
    try:
        cursor.execute(query, (patient_id,))
        records = cursor.fetchall()
        return records
    except Exception as e:
        print(f"Error fetching patient tests: {e}")
        return []
    finally:
        conn.close()

def patient_view_tests_ui():
    st.subheader("View Lab Test Results")

    if not st.session_state.get("logged_in") or st.session_state["role"] != "Patient":
        st.warning("You must log in as a patient to view lab test results.")
        return

    patient_id = st.session_state["user_id"]

    if st.button("View Tests"):
        results = view_patient_tests(patient_id)
        if results:
            for record in results:
                st.write(f"**Appointment ID:** {record[0]}")
                st.write(f"**Appointment Date:** {record[1]}")
                st.write(f"**Doctor's Name:** {record[2]}")
                st.write(f"**Test Name:** {record[3]}")
                st.write(f"**Result:** {record[4]}")
                st.write("---")
        else:
            st.warning("No test results found.")

def admin_lab_tests_ui():
    st.subheader("Manage Lab Tests (Admin)")

    operations = ["Create", "View", "Update", "Delete"]
    operation = st.radio("Select Operation", operations)

    if operation == "Create":
        add_lab_test_ui()
    elif operation == "View":
        view_lab_tests_ui()
    elif operation == "Update":
        update_lab_test_ui()
    elif operation == "Delete":
        delete_lab_test_ui()

def fetch_lab_tests():
    conn = connect_to_db()
    if conn is None:
        return []

    cursor = conn.cursor()
    query = """
        SELECT LabTestID, TestName, Description, Cost, CreatedAt, UpdatedAt
        FROM LabTests
        ORDER BY CreatedAt DESC
    """
    try:
        cursor.execute(query)
        lab_tests = cursor.fetchall()
        return lab_tests
    except Exception as e:
        st.error(f"Error fetching lab tests: {e}")
        return []
    finally:
        conn.close()

def lab_test_ui():
    st.subheader("Admin - Lab Test Management")

    lab_tests = fetch_lab_tests()

    if lab_tests:
        st.write("### Lab Test List")
        lab_test_data = [
            {
                "Lab Test ID": test[0],
                "Test Name": test[1],
                "Description": test[2],
                "Cost": f"${test[3]:,.2f}",
                "Created At": test[4],
                "Updated At": test[5],
            }
            for test in lab_tests
        ]
        st.dataframe(lab_test_data)
    else:
        st.info("No lab tests found.")

    st.write("### Add a New Lab Test")

    test_name = st.text_input("Test Name")
    description = st.text_area("Description")
    cost = st.number_input("Cost", min_value=0.0, format="%.2f")

    if st.button("Add Lab Test"):
        if test_name and description and cost > 0:
            success = add_lab_test(test_name, description, cost)
            if success:
                st.success("Lab test added successfully!")
        else:
            st.error("Please fill in all fields and ensure cost is greater than zero.")
