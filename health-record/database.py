import streamlit as st
import pymysql
import bcrypt

def connect_to_db():
    try:
        conn = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            port=int(st.secrets["mysql"]["port"]),
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            ssl={}
        )
        return conn
    except pymysql.MySQLError as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Hash Password
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

# Verify Password
def verify_password(password, hashed):
    if not hashed:
        print("No hashed password provided.")
        return False
    
    # Ensure the hash is in bytes format
    hashed = hashed.encode('utf-8') if isinstance(hashed, str) else hashed

    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    except ValueError as e:
        print(f"Error verifying password: {e}")
        return False

# Database Schema Migration Helper
def migrate_database():
    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()
    
    # 1. Modify TransactionID type
    try:
        cursor.execute("ALTER TABLE Billing MODIFY COLUMN TransactionID VARCHAR(50) NULL;")
        conn.commit()
    except Exception as e:
        pass

    # 2. Modify PaymentStatus type from ENUM to VARCHAR
    try:
        cursor.execute("ALTER TABLE Billing MODIFY COLUMN PaymentStatus VARCHAR(30) NOT NULL;")
        conn.commit()
    except Exception as e:
        pass

    # 3. Add PayerName column
    try:
        cursor.execute("ALTER TABLE Billing ADD COLUMN PayerName VARCHAR(100) NULL;")
        conn.commit()
    except Exception as e:
        pass

    conn.close()


