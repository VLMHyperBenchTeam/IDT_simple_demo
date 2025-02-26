import streamlit as st

st.set_page_config(page_title="Document sorting demo", page_icon="🧙")

from pathlib import Path
from parse_pdf import convert_pdf_to_images
from pdf_mapper import pdf_to_mappings
from pypdf import PdfReader
from get_page_sorting import get_page_sorting

# Инициализация аутентификации
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login_page():
    """Форма входа."""
    placeholder = st.empty()
    
    with placeholder.form("login"):
        st.markdown("#### Введите данные для авторизации")
        email = st.text_input("Email")
        password = st.text_input("Пароль", type="password")
        submit = st.form_submit_button("Войти")
    
    actual_email = "" #"user@example.com"
    actual_password = "" #"securepassword"
    
    if submit:
        if email == actual_email and password == actual_password:
            placeholder.empty()
            st.session_state.authenticated = True
            st.success("Авторизовано как {}".format(email))
            st.rerun()
        else:
            st.error("Ошибка авторизации")

def home_page():
    """Домашняя страница."""
    st.title("Домашняя страница")
    st.write("Здесь может быть ваш основной контент.")

def pdf_sorter_page():
    """Страница для обработки PDF."""
    pdf_file = st.file_uploader("Загрузите документ", type=["pdf"])
    if pdf_file is not None:
        with open('uploaded.pdf', 'wb') as temp_input_pdf_file:
            temp_input_pdf_file.write(pdf_file.read())
        image_folder = Path('images')
        image_folder.mkdir(parents=True, exist_ok=True)
        convert_pdf_to_images(pdf_path=Path('uploaded.pdf'), images_folder=image_folder)
        model_answer = get_page_sorting('test.jpg')
        with PdfReader('uploaded.pdf') as reader:
            count_page = len(reader.pages)
        # ... остальной код ...

def about_page():
    """Страница 'О приложении'."""
    st.title("О приложении")
    st.write("Информация о вашем приложении.")

# Основное приложение
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        selected = st.sidebar.radio(
            "Меню",
            ["Домашняя страница", "PDF-сортировка", "О приложении"],
            key="navigation"  # Добавьте ключ, чтобы избежать конфликтов
        )
        
        if selected == "Домашняя страница":
            home_page()
        elif selected == "PDF-сортировка":
            pdf_sorter_page()
        elif selected == "О приложении":
            about_page()

if __name__ == "__main__":
    main()