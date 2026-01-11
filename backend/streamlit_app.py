import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import requests
import json
from io import BytesIO

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Streamlit page config
st.set_page_config(page_title="Job Matching System", page_icon=":briefcase:", layout="wide")

# Custom CSS for white and green theme
st.markdown("""
<style>
    .main {
        background-color: #ffffff;
        color: #000000;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    .stTextInput>div>div>input {
        border: 1px solid #4CAF50;
    }
    .stFileUploader>div>div>div>button {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Authentication
def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return None

def signup_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return response
    except Exception as e:
        st.error(f"Signup failed: {str(e)}")
        return None

def logout_user():
    supabase.auth.sign_out()
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# Main app
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None

    if not st.session_state.logged_in:
        st.title("Job Profile Matching System")
        st.subheader("Login or Sign Up")

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                response = login_user(email, password)
                if response:
                    st.session_state.logged_in = True
                    st.session_state.user = response.user
                    st.success("Logged in successfully!")
                    st.rerun()

        with tab2:
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up"):
                response = signup_user(email, password)
                if response:
                    st.success("Signed up successfully! Please check your email to confirm.")
    else:
        dashboard()

def dashboard():
    st.title("Dashboard")
    st.write(f"Welcome, {st.session_state.user.email}!")

    if st.button("Logout"):
        logout_user()

    st.header("Upload Resume")
    uploaded_file = st.file_uploader("Choose a PDF resume", type="pdf")
    if uploaded_file is not None and st.button("Upload Resume"):
        try:
            # Get access token
            session = supabase.auth.get_session()
            access_token = session.access_token

            # Prepare file
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.post(f"{BACKEND_URL}/resumes/upload", files=files, headers=headers)
            if response.status_code == 200:
                st.success("Resume uploaded successfully!")
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.header("Compute Matches")
    if st.button("Find Matching Jobs"):
        try:
            session = supabase.auth.get_session()
            access_token = session.access_token
            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.post(f"{BACKEND_URL}/matches/compute", headers=headers)
            if response.status_code == 200:
                st.success("Matches computed!")
            else:
                st.error(f"Failed to compute matches: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.header("Your Matches")
    try:
        session = supabase.auth.get_session()
        access_token = session.access_token
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(f"{BACKEND_URL}/matches/", headers=headers)
        if response.status_code == 200:
            matches = response.json()
            if matches:
                for match in matches:
                    st.write(f"Job: {match['job_title']} - Score: {match['score']:.2f}")
            else:
                st.write("No matches found.")
        else:
            st.error("Failed to fetch matches.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

    st.header("Notifications")
    try:
        session = supabase.auth.get_session()
        access_token = session.access_token
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(f"{BACKEND_URL}/notifications/", headers=headers)
        if response.status_code == 200:
            notifications = response.json()
            if notifications:
                for notif in notifications:
                    st.write(f"{notif['message']} - {notif['created_at']}")
            else:
                st.write("No notifications.")
        else:
            st.error("Failed to fetch notifications.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()