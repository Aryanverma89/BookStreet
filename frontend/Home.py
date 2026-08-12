import streamlit as st
import requests

st.set_page_config(page_title="Online Book Store", page_icon="📚")

API_URL = "http://127.0.0.1:5000"

# -------------------------
# Session State
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# -------------------------
# Dashboard
# -------------------------
if st.session_state.logged_in:

    st.title("📚 Online Second-Hand Book Store")

    st.success(f"Welcome, {st.session_state.user_name} 👋")

    st.write("You are logged in successfully.")

    st.button("📖 Buy Books")
    st.button("📚 Sell Book")
    st.button("📋 My Books")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.rerun()

# -------------------------
# Login & Register
# -------------------------
else:

    st.title("📚 Online Second-Hand Book Store")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    # ===========================
    # LOGIN
    # ===========================
    with login_tab:

        st.subheader("Login")

        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):

            data = {
                "email": login_email,
                "password": login_password
            }

            response = requests.post(
                f"{API_URL}/login",
                json=data
            )

            if response.status_code == 200:

                user = response.json()["user"]

                st.session_state.logged_in = True
                st.session_state.user_name = user["name"]

                st.success(response.json()["message"])

                st.rerun()

            else:
                st.error(response.json()["message"])

    # ===========================
    # REGISTER
    # ===========================
    with register_tab:

        st.subheader("Register")

        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")

        if st.button("Register"):

            data = {
                "name": name,
                "email": email,
                "phone": phone,
                "password": password
            }

            response = requests.post(
                f"{API_URL}/register",
                json=data
            )

            if response.status_code == 200:
                st.success(response.json()["message"])
            else:
                st.error(response.json()["message"])