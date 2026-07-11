import streamlit as st
import pymysql
from database import connect_to_db, hash_password, verify_password
import datetime

def sign_up_patient(first_name, last_name, dob, address, phone, email, password):
    conn = connect_to_db()
    if conn is None:
        return False, "Failed to connect to the database."
    
    cursor = conn.cursor()
    hashed_pw = hash_password(password)

    query = """
        INSERT INTO Patient (FirstName, LastName, DOB, Address, PhoneNumber, Email, Password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (first_name, last_name, dob, address, phone, email, hashed_pw))
        conn.commit()
        return True, "Patient account created successfully!"
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            return False, f"An account with the email '{email}' already exists. Please log in or use a different email."
        return False, f"Database Integrity Error: {e.args[1]}"
    except Exception as e:
        return False, f"Failed to create account: {str(e)}"
    finally:
        conn.close()

def sign_up_doctor(first_name, last_name, specialization, phone, email, password):
    conn = connect_to_db()
    if conn is None:
        return False, "Failed to connect to the database."
    cursor = conn.cursor()
    hashed_pw = hash_password(password)

    query = """
        INSERT INTO Doctor (FirstName, LastName, Specialization, PhoneNumber, Email, Password)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (first_name, last_name, specialization, phone, email, hashed_pw))
        conn.commit()
        return True, "Doctor account created successfully!"
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            return False, f"An account with the email '{email}' already exists. Please log in or use a different email."
        return False, f"Database Integrity Error: {e.args[1]}"
    except Exception as e:
        return False, f"Failed to create account: {str(e)}"
    finally:
        conn.close()

def fetch_patient_id(email):
    conn = connect_to_db()
    if conn is None:
        return None
    cursor = conn.cursor()

    query = "SELECT PatientID FROM Patient WHERE Email = %s"
    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("No patient found with this email.")
            return None
    except Exception as e:
        print(f"Error fetching PatientID: {e}")
        return None
    finally:
        conn.close()

def sign_up_patient_ui():
    st.subheader("Patient Sign-Up")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    dob = st.date_input(
        "Date of Birth",
        value=datetime.date(2000, 1, 1),
        min_value=datetime.date(1900, 1, 1),
        max_value=datetime.date.today()
    )
    address = st.text_area("Address")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not all([first_name, last_name, dob, address, phone, email, password]):
            st.error("All fields are required!")
        else:
            success, message = sign_up_patient(first_name, last_name, dob, address, phone, email, password)
            if success:
                st.success(message)
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = fetch_patient_id(email)
                st.session_state["role"] = "Patient"
                st.session_state["redirect_to_create"] = True
                st.rerun()
            else:
                st.error(message)

def sign_up_doctor_ui():
    st.subheader("Doctor Sign-Up")

    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    specialization = st.text_input("Specialization")
    phone = st.text_input("PhoneNumber")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not all([first_name, last_name, specialization, phone, email, password]):
            st.error("All fields are required!")
        else:
            success, message = sign_up_doctor(first_name, last_name, specialization, phone, email, password)
            if success:
                st.success(message)
            else:
                st.error(message)

def login_user(email, password, role):
    conn = connect_to_db()
    if conn is None:
        return None, False, "Failed to connect to the database."
    cursor = conn.cursor()

    if role == "Patient":
        query = "SELECT PatientID, Password FROM Patient WHERE Email=%s"
    elif role == "Doctor":
        query = "SELECT DoctorID, Password FROM Doctor WHERE Email=%s"
    elif role == "Admin":
        query = "SELECT id, password FROM admin WHERE Email=%s"
    else:
        conn.close()
        return None, False, "Invalid role selected."

    try:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
    except Exception as e:
        return None, False, f"Database error: {str(e)}"
    finally:
        conn.close()

    if not result:
        return None, False, f"No account found with the email '{email}'. Please sign up first."

    if verify_password(password, result[1]):
        return result[0], True, "Login successful!"
    return None, False, "Incorrect password. Please try again."

def login_ui():
    st.subheader("Login")
    role = st.radio("Role", ["Patient", "Doctor", "Admin"])
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id, success, message = login_user(email, password, role)
        if success:
            st.success(message)
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user_id
            st.session_state["role"] = role
            st.session_state["redirect_to_create"] = True
            st.rerun()
        else:
            st.error(message)

def logout_ui():
    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["role"] = None
        st.success("You have been logged out.")
        st.rerun()

def fetch_doctors():
    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()
    query = "SELECT DoctorID, FirstName, LastName, Specialization FROM Doctor"
    try:
        cursor.execute(query)
        doctors = cursor.fetchall()
        return doctors
    except Exception as e:
        print(f"Error fetching doctors: {e}")
        return []
    finally:
        conn.close()

def sign_up_admin(email, password):
    conn = connect_to_db()
    if conn is None:
        return False, "Failed to connect to the database."
    
    cursor = conn.cursor()
    hashed_pw = hash_password(password)

    query = """
        INSERT INTO admin (Email, Password)
        VALUES ( %s, %s)
    """
    try:
        cursor.execute(query, (email, hashed_pw))
        conn.commit()
        return True, "Admin account created successfully!"
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            return False, f"An account with the email '{email}' already exists. Please log in or use a different email."
        return False, f"Database Integrity Error: {e.args[1]}"
    except Exception as e:
        return False, f"Failed to create account: {str(e)}"
    finally:
        conn.close()

def sign_up_admin_ui():
    st.subheader("Admin Sign-Up")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not all([email, password]):
            st.error("All fields are required!")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long!")
        else:
            success, message = sign_up_admin(email, password)
            if success:
                st.success(message)
                st.session_state["logged_in"] = True
                st.session_state["role"] = "Admin"
                st.session_state["admin_email"] = email
                st.session_state["redirect_to_home"] = True
                st.rerun()
            else:
                st.error(message)
