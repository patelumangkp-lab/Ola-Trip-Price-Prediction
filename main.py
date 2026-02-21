"""
Main application entry point for India Cab Service
"""

import streamlit as st
from ui.user_interface import UserInterface
from ui.admin_interface import AdminInterface
from services.auth_service import AuthService
from config import PAGE_CONFIG


def main():
    """Main application function"""
    # Set page config first (must be first Streamlit command)
    st.set_page_config(**PAGE_CONFIG)

    # Initialize auth service
    auth_service = AuthService()

    # Check if user is logged in
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
        st.session_state.user_logged_in = False

    # Sidebar for authentication and mode selection
    with st.sidebar:
        st.title("🚗 India Cab Service")
        st.markdown("---")

        if not st.session_state.user_logged_in:
            # Authentication section
            auth_tab = st.selectbox("Authentication", ["Sign Up", "Sign In"])

            if auth_tab == "Sign Up":
                render_signup_form(auth_service)
            else:
                render_signin_form(auth_service)
        else:
            # User is logged in
            user = auth_service.get_user(st.session_state.user_id)
            if user:
                st.success(f"Welcome, {user.get('name', 'User')}!")
                st.write(
                    f"📍 {user.get('city', 'Unknown City')}, {user.get('state', 'Unknown State')}"
                )

                if user.get("is_admin"):
                    st.info("👑 Admin Access")

                if st.button("Logout"):
                    st.session_state.user_id = None
                    st.session_state.user_logged_in = False
                    st.rerun()

            st.markdown("---")

            # Mode selection for logged-in users
            if user and user.get("is_admin"):
                mode = st.radio(
                    "Select Mode",
                    ["User Interface", "Admin Panel"],
                    index=0 if not st.session_state.get("admin_mode", False) else 1,
                )

                if mode == "Admin Panel":
                    st.session_state.admin_mode = True
                else:
                    st.session_state.admin_mode = False
            else:
                st.session_state.admin_mode = False

    # Run appropriate interface
    if not st.session_state.user_logged_in:
        render_welcome_page()
    elif st.session_state.admin_mode and st.session_state.user_logged_in:
        user = auth_service.get_user(st.session_state.user_id)
        if user and user.get("is_admin"):
            admin_ui = AdminInterface()
            admin_ui.run()
        else:
            st.error("You don't have admin access")
            user_ui = UserInterface()
            user_ui.run()
    else:
        user_ui = UserInterface()
        user_ui.run()


def render_signup_form(auth_service):
    """Render sign up form"""
    st.subheader("📝 Create Account")

    with st.form("signup_form"):
        name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email address")
        phone = st.text_input("Phone Number", placeholder="Enter your phone number")
        password = st.text_input(
            "Password", type="password", placeholder="Enter your password"
        )
        confirm_password = st.text_input(
            "Confirm Password", type="password", placeholder="Confirm your password"
        )

        # State and City selection
        col1, col2 = st.columns(2)
        with col1:
            state = st.selectbox("State", ["Select State"] + auth_service.get_states())
        with col2:
            if state != "Select State":
                cities = auth_service.get_cities_for_state(state)
                city = st.selectbox("City", ["Select City"] + cities)
            else:
                city = "Select City"

        submit_button = st.form_submit_button("Create Account", type="primary")

        if submit_button:
            # Validate all fields
            if (
                not all([name, email, phone, password, confirm_password, state, city])
                or state == "Select State"
                or city == "Select City"
            ):
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "password": password,
                    "state": state,
                    "city": city,
                }

                # Check if email already exists
                existing_user = auth_service.get_user_by_email(email)
                if existing_user:
                    st.error("Email already exists. Please sign in instead.")
                else:
                    user = auth_service.create_user(user_data)
                    st.session_state.user_id = user["id"]
                    st.session_state.user_logged_in = True

                    if user.get("is_admin"):
                        st.success(
                            "🎉 Account created successfully! You are the first user and have been granted admin access."
                        )
                    else:
                        st.success("🎉 Account created successfully!")

                    st.rerun()


def render_signin_form(auth_service):
    """Render sign in form"""
    st.subheader("🔐 Sign In")

    with st.form("signin_form"):
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input(
            "Password", type="password", placeholder="Enter your password"
        )
        submit_button = st.form_submit_button("Sign In", type="primary")

        if submit_button:
            if not email or not password:
                st.error("Please enter both email and password")
            else:
                user = auth_service.authenticate_user(email, password)
                if user:
                    st.session_state.user_id = user["id"]
                    st.session_state.user_logged_in = True
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")


def render_welcome_page():
    """Render welcome page for non-logged-in users"""
    st.title("🚗 Welcome to India Cab Service")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.header("🌟 Features")
        st.markdown(
            """
        - **Smart Route Planning**: AI-powered route optimization
        - **Real-time Pricing**: Dynamic pricing based on conditions
        - **Multiple Vehicle Options**: Bike, Car, Premium, and 6-Seater
        - **City-based Suggestions**: Get suggestions for famous places in your city
        - **Transparent Pricing**: Clear breakdown of all costs
        """
        )

    with col2:
        st.header("🚀 Get Started")
        st.markdown(
            """
        1. **Sign Up**: Create your account with state and city selection
        2. **Book Rides**: Get suggestions for famous places in your city
        3. **Track Bookings**: View your booking history
        4. **Admin Access**: First user gets admin privileges automatically
        """
        )

    st.markdown("---")
    st.info("👈 Please use the sidebar to sign up or sign in to continue")


if __name__ == "__main__":
    main()
