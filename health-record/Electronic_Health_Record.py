import streamlit as st

# Configure the page setting at the very top
st.set_page_config(
    page_title="Health Records Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Injection
st.markdown("""
<style>
    /* Fonts & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Main Container Styling */
    div.block-container {
        padding: 3rem 5rem;
        max-width: 1250px;
    }

    /* Custom Cards for UI Elements */
    div.element-container, div.stAlert, div.stForm {
        border-radius: 12px;
    }

    /* Button Styling */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.25s ease;
        box-shadow: 0 4px 6px -1px rgba(13, 148, 136, 0.2);
    }
    
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #0f766e 0%, #115e59 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(13, 148, 136, 0.35);
    }

    div.stButton > button:first-child:active {
        transform: translateY(0px);
    }

    /* Sidebar Customizations */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #f8fafc !important;
    }

    /* Input Field Styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 0.5rem 0.8rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #0d9488 !important;
        box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
    }

    /* Headings Styling */
    h1 {
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.025em;
        margin-bottom: 1.5rem !important;
    }

    h2, h3 {
        font-weight: 700 !important;
        color: #1e293b !important;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.6rem;
        margin-top: 2rem !important;
        margin-bottom: 1.2rem !important;
    }

    /* Metric Layout Card styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #f1f5f9;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Import modular UIs
from database import migrate_database
from auth import (
    login_ui, logout_ui, sign_up_patient_ui, sign_up_doctor_ui, sign_up_admin_ui
)
from appointments import appointment_operations_ui
from medical_records import medical_record_operations_ui
from lab_tests import (
    patient_view_tests_ui, doctor_assign_tests_ui, doctor_add_results_ui, 
    lab_test_ui, admin_lab_tests_ui
)
from billing_wallet import (
    pay_bill_ui, doctor_add_billing_ui, view_billing_record_ui, admin_wallet_ui
)

def main():
    # Run DB schema migration on startup
    migrate_database()

    # Sidebar App Branding
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1.5rem; border-bottom: 1px solid #1e293b;">
        <h2 style="margin: 0; color: #0d9488 !important; font-size: 1.6rem; font-weight: 800;">🏥 HealthCare MS</h2>
        <p style="color: #64748b !important; font-size: 0.85rem; margin-top: 0.2rem;">Secure Health Portal</p>
    </div>
    """, unsafe_allow_html=True)

    # Check for redirection after login or sign-up
    if not st.session_state.get("logged_in"):
        menu = ["Home", "Login", "Sign Up"]
        choice = st.sidebar.selectbox("Navigation Menu", menu)

        if choice == "Home":
            st.title("Health Records Management System")
            
            # Welcome Hero Banner
            st.markdown("""
            <div style="background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%); padding: 3rem; border-radius: 16px; color: white; margin-bottom: 2.5rem; box-shadow: 0 10px 15px -3px rgba(13, 148, 136, 0.15);">
                <h1 style="color: white !important; margin: 0; font-size: 2.5rem; font-weight: 800;">Welcome to your healthcare partner.</h1>
                <p style="font-size: 1.1rem; opacity: 0.9; margin-top: 0.8rem; font-weight: 400; max-width: 700px;">
                    A web-based Electronic Health Record (EHR) management system designed to streamline consultations, appointments, billing, lab results, and histories with maximum ease.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Feature Cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div style="background-color: white; border: 1px solid #f1f5f9; padding: 1.8rem; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);">
                    <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">📅</div>
                    <h4 style="margin: 0; color: #0f172a; font-weight: 700; font-size: 1.15rem;">Appointments</h4>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.5;">Book, update or cancel appointments with qualified doctors in just a few clicks.</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div style="background-color: white; border: 1px solid #f1f5f9; padding: 1.8rem; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);">
                    <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">🔬</div>
                    <h4 style="margin: 0; color: #0f172a; font-weight: 700; font-size: 1.15rem;">Lab Results</h4>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.5;">Direct integration of laboratory tests and results. Patients can view reports securely as soon as doctors upload them.</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown("""
                <div style="background-color: white; border: 1px solid #f1f5f9; padding: 1.8rem; border-radius: 12px; height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);">
                    <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">💳</div>
                    <h4 style="margin: 0; color: #0f172a; font-weight: 700; font-size: 1.15rem;">Wallet & Billing</h4>
                    <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem; line-height: 1.5;">Built-in secure digital wallets for instant consulting fee payouts, invoice tracking, and bill settlements.</p>
                </div>
                """, unsafe_allow_html=True)

            st.info("💡 Please log in or create an account using the sidebar menu to get started.")

        elif choice == "Login":
            login_ui()

        elif choice == "Sign Up":
            role = st.radio("Sign-Up As", ["Patient", "Doctor", "Admin"])
            if role == "Patient":
                sign_up_patient_ui()
            elif role == "Doctor":
                sign_up_doctor_ui()
            elif role == "Admin":
                sign_up_admin_ui()

    else:
        # Display Role Header
        st.sidebar.markdown(f"""
        <div style="background-color: #1e293b; padding: 0.8rem 1.2rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #0d9488;">
            <p style="margin: 0; font-size: 0.75rem; color: #94a3b8 !important; text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em;">Active Session</p>
            <p style="margin: 0; font-size: 1.05rem; color: #f8fafc !important; font-weight: 700;">{st.session_state['role']}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state["role"] == "Patient":
            menu = ["Home", "Appointment", "Medical Record", "LabResults", "Pay Bill", "Logout"]
            choice = st.sidebar.selectbox("Navigation Menu", menu)

            if choice == "Home":
                st.title("Patient Dashboard")
                st.subheader(f"Welcome back, Patient #{st.session_state['user_id']}!")
                st.info("Use the sidebar navigation menu to schedule appointments, view your medical history, check lab reports, or pay your pending bills.")
                
            elif choice == "Appointment":
                appointment_operations_ui()
            elif choice == "Medical Record":
                medical_record_operations_ui()
            elif choice == "LabResults": 
                patient_view_tests_ui()
            elif choice == "Pay Bill":
                pay_bill_ui()
            elif choice == "Logout":
                logout_ui()

        elif st.session_state["role"] == "Doctor":
            menu = ["Home", "Medical Record", "LabResults", "Appointment", "Billing", "Logout"]
            choice = st.sidebar.selectbox("Navigation Menu", menu)

            if choice == "Home":
                st.title("Doctor Dashboard")
                st.subheader(f"Welcome back, Dr. Doctor #{st.session_state['user_id']}!")
                st.info("Access doctor controls including appointment schedules, updating patient files, assigning laboratory tests, and raising invoices.")
                
            elif choice == "Appointment":
                appointment_operations_ui()
            elif choice == "Medical Record":
                medical_record_operations_ui()
            elif choice == "LabResults":
                action = st.sidebar.radio("Choose Action", ["Assign Tests", "Add Results"])
                if action == "Assign Tests":
                    doctor_assign_tests_ui()
                elif action == "Add Results":
                    doctor_add_results_ui()
            elif choice == "Billing":
                doctor_add_billing_ui()
            elif choice == "Logout":
                logout_ui()

        elif st.session_state["role"] == "Admin":
            menu = ["Home", "Appointment", "Medical Record", "View Billing Record", "LabTests", "LabResults", "AdminWallet", "Logout"]
            choice = st.sidebar.selectbox("Navigation Menu", menu)

            if choice == "Home":
                st.title("System Administrator Console")
                st.subheader("Welcome back, Administrator!")
                st.info("Access platform-wide configurations, audit active appointments, view generated invoices, create lab packages, and manage admin wallets.")
                
            elif choice == "Appointment":
                appointment_operations_ui()
            elif choice == "Medical Record":
                medical_record_operations_ui()
            elif choice == "View Billing Record":
                view_billing_record_ui()
            elif choice == "LabTests":
                lab_test_ui()
            elif choice == "LabResults":
                admin_lab_tests_ui()
            elif choice == "AdminWallet":
                admin_wallet_ui()
            elif choice == "Logout":
                logout_ui()

if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["role"] = None
        st.session_state["admin_email"] = None

    main()