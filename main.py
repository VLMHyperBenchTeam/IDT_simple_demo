import streamlit as st

from app_pages.home import home_page
from app_pages.pdf_sorter import pdf_sorter_page
from app_pages.about import about_page
from utils.auth import login_page

# Инициализация аутентификации
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# Основное приложение
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        selected = st.sidebar.radio(
            "Меню",
            ["Домашняя страница", "PDF-сортировка", "О приложении"],
            key="navigation",  # Добавьте ключ, чтобы избежать конфликтов
        )

        if selected == "Домашняя страница":
            home_page()
        elif selected == "PDF-сортировка":
            pdf_sorter_page()
        elif selected == "О приложении":
            about_page()


if __name__ == "__main__":
    main()
