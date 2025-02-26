import streamlit as st
from pathlib import Path
from parse_pdf import convert_pdf_to_images
from pdf_mapper import pdf_to_mappings
from get_page_sorting import get_page_sorting
from pypdf import PdfReader

def pdf_sorter_page():
    st.title("PDF-сортировка")
    
    # Форма для загрузки PDF
    pdf_file = st.file_uploader("Загрузите документ", type=["pdf"])
    
    if pdf_file is not None:
        with open("uploaded.pdf", "wb") as temp_input_pdf_file:
            temp_input_pdf_file.write(pdf_file.read())
        
        image_folder = Path("images")
        image_folder.mkdir(parents=True, exist_ok=True)
        
        # Путь к выходному файлу
        output_file_path = "sorted_output.pdf"
        
        # Если отсортированный PDF уже существует, не выполняем повторную обработку
        if not Path(output_file_path).exists():
            # Конвертация PDF в изображения
            convert_pdf_to_images(pdf_path=Path("uploaded.pdf"), images_folder=image_folder)
            
            # Получение порядка страниц
            pages_mapping = get_page_sorting(image_folder)
            
            with PdfReader("uploaded.pdf") as reader:
                count_page = len(reader.pages)
            
            # Создание отсортированного PDF
            pdf_to_mappings(
                pdf_in_path="uploaded.pdf",
                mapping_list=pages_mapping,
                output_file_path=output_file_path,
            )
        
        # Если файл существует, показываем кнопку для скачивания
        if Path(output_file_path).exists():
            st.success(f"Отсортированный PDF готов!")
            
            # Считываем содержимое отсортированного PDF
            with open(output_file_path, "rb") as file:
                pdf_bytes = file.read()
            
            # Предлагаем пользователю скачать файл
            st.download_button(
                label="Скачать отсортированный PDF",
                data=pdf_bytes,
                file_name="sorted_output.pdf",
                mime="application/pdf"
            )