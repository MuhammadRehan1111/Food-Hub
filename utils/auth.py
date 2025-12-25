"""
Simple authentication utilities for the admin panel.
"""
import streamlit as st
import config


def check_password(role: str = "admin") -> bool:
    """
    Returns True if the user has entered the correct password for the specified role.
    Roles: 'admin', 'cashier'
    """
    if "role" not in st.session_state:
        st.session_state["role"] = "customer"

    # If already logged in as admin, they have access to everything
    if st.session_state.get("authenticated") and st.session_state.get("role") == "admin":
        return True
    
    # If logged in with the requested role
    if st.session_state.get("authenticated") and st.session_state.get("role") == role:
        return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        user = st.session_state.get("username_input")
        pw = st.session_state.get("password_input")
        
        # Load dynamic settings if they exist
        import json
        from pathlib import Path
        settings = {}
        settings_file = Path(__file__).parent.parent / "data" / "settings.json"
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
        except:
            pass
            
        # Admin check (Settings -> Config fallback)
        admin_user = settings.get('admin_username', config.ADMIN_USERNAME)
        admin_pw = settings.get('admin_password', config.ADMIN_PASSWORD)
        
        if user == admin_user and pw == admin_pw:
            st.session_state["authenticated"] = True
            st.session_state["role"] = "admin"
            del st.session_state["username_input"]
            del st.session_state["password_input"]
            return True
        
        # Cashier check (Settings -> Config fallback)
        cashier_user = settings.get('cashier_username', getattr(config, "CASHIER_USERNAME", "cashier"))
        cashier_pw = settings.get('cashier_password', getattr(config, "CASHIER_PASSWORD", "cashier123"))
        
        if user == cashier_user and pw == cashier_pw:
            st.session_state["authenticated"] = True
            st.session_state["role"] = "cashier"
            del st.session_state["username_input"]
            del st.session_state["password_input"]
            return True
            
        st.session_state["authenticated"] = False
        st.error("😕 Invalid username or password")
        return False

    # Login form
    st.markdown(f"### 🔐 {role.capitalize()} Login")
    st.markdown(f'<p style="color: #ffffff; opacity: 0.9;">Please enter your credentials to access the {role} panel.</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.text_input("Username", key="username_input")
        st.text_input("Password", type="password", key="password_input")
        submitted = st.form_submit_button("Login", type="primary")
        
        if submitted:
            if password_entered():
                st.rerun()
    
    return False


def logout():
    """Log out the current user."""
    st.session_state["authenticated"] = False
    st.session_state["role"] = "customer"
    st.rerun()
