import streamlit as st
from pathlib import Path
from parse_pdf import convert_pdf_to_images
from pdf_mapper import pdf_to_mappings
from get_page_sorting import get_page_sorting
from pypdf import PdfReader


def pdf_sorter_page():
    st.title("PDF-сортировка")
    pdf_file = st.file_uploader("Загрузите документ", type=["pdf"])

    if pdf_file is not None:
        with open("uploaded.pdf", "wb") as temp_input_pdf_file:
            temp_input_pdf_file.write(pdf_file.read())

        image_folder = Path("images")
        image_folder.mkdir(parents=True, exist_ok=True)

        # Конвертация PDF в изображения
        convert_pdf_to_images(pdf_path=Path("uploaded.pdf"), images_folder=image_folder)

        # Получение порядка страниц
        model_answer = get_page_sorting("test.jpg")

        with PdfReader("uploaded.pdf") as reader:
            count_page = len(reader.pages)

        # Сохранение отсортированного PDF
        output_file_path = "sorted_output.pdf"
        pdf_to_mappings(
            pdf_in_path="uploaded.pdf",
            mapping_list=model_answer,
            output_file_path=output_file_path,
        )

        st.success(f"Отсортированный PDF сохранен: {output_file_path}")
