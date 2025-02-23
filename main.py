import json
from pathlib import Path

import streamlit as st
from streamlit.source_util import _on_pages_changed, get_pages
from streamlit_extras.switch_page_button import switch_page

DEFAULT_PAGE = "main.py"
SECOND_PAGE_NAME = "page_sorter"

def get_all_pages():
    default_pages = get_pages(DEFAULT_PAGE)

    pages_path = Path("pages.json")

    if pages_path.exists():
        saved_default_pages = json.loads(pages_path.read_text())
    else:
        saved_default_pages = default_pages.copy()
        pages_path.write_text(json.dumps(default_pages, indent=4))

    return saved_default_pages


def clear_all_except_first_page():
    current_pages = get_pages(DEFAULT_PAGE)

    if len(current_pages.keys()) == 1:
        return

    get_all_pages()

    # Remove all but the first page
    page, page_data = list(current_pages.items())[0]
    current_pages.clear()
    current_pages[page] = page_data

    _on_pages_changed.send()


def show_all_pages():
    current_pages = get_pages(DEFAULT_PAGE)

    saved_pages = get_all_pages()
    # Replace all the missing pages
    for page in saved_pages:
        if page not in current_pages:
            current_pages[page] = saved_pages[page]

    _on_pages_changed.send()


def hide_page(name: str):
    current_pages = get_pages(DEFAULT_PAGE)

    for page, page_data in current_pages.items():
        if page_data["page_name"] == name:
            current_pages.pop(page)
            _on_pages_changed.send()
            break


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

clear_all_except_first_page()
placeholder = st.empty()

actual_email = "email@email.com"
actual_password = "password"

# Insert a form in the container
with placeholder.form("login"):
    st.markdown("#### Введите данные для авторизации")
    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")
    submit = st.form_submit_button("Войти")

if submit and email == actual_email and password == actual_password:
    # If the form is submitted and the email and password are correct,
    # clear the form/container and display a success message
    placeholder.empty()
    st.session_state["logged_in"] = True
    st.success("Авторизовано как {}".format(email))
elif submit and email != actual_email and password != actual_password:
    st.error("Ошибка авторизации")
else:
    pass

if st.session_state["logged_in"]:
    show_all_pages()
    hide_page(DEFAULT_PAGE.replace(".py", ""))
    switch_page(SECOND_PAGE_NAME)
else:
    clear_all_except_first_page()


