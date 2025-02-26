import streamlit as st

def authenticate(email, password):
    actual_email = "" # user@example.com
    actual_password = "" # securepassword
    return email == actual_email and password == actual_password

def login_page():
    placeholder = st.empty()
    
    with placeholder.form("login"):
        st.markdown("#### Введите данные для авторизации")
        email = st.text_input("Email")
        password = st.text_input("Пароль", type="password")
        submit = st.form_submit_button("Войти")
    
    if submit:
        if authenticate(email, password):
            placeholder.empty()
            st.session_state.authenticated = True
            st.success("Авторизовано как {}".format(email))
            st.rerun()
        else:
            st.error("Ошибка авторизации")