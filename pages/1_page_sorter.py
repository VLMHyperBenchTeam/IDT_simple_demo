
from pathlib import Path

import streamlit as st

from get_page_sorting import get_page_sorting
from parse_pdf import convert_pdf_to_images
from pdf_mapper import pdf_to_mappings
from pypdf import PdfReader

st.set_page_config(page_title="Document sorting demo", page_icon="🧙")

pdf_file = st.file_uploader("Upload document", type=["pdf"])

if pdf_file is not None:
    with open('uploaded.pdf', 'wb') as temp_input_pdf_file:
        temp_input_pdf_file.write(pdf_file.read())
    image_folder = Path('images')
    image_folder.mkdir(parents=True, exist_ok=True)
    convert_pdf_to_images(pdf_path=Path('uploaded.pdf'), images_folder=image_folder)
    model_answer = get_page_sorting('test.jpg')
    with PdfReader('uploaded.pdf') as reader:
        count_page = len(reader.pages)
    if len(model_answer) > count_page:
        model_answer = [i for i in model_answer if i <= count_page]

    pdf_to_mappings('uploaded.pdf', model_answer, 'sorted.pdf')
    with open('sorted.pdf', "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
    download_report = st.sidebar.button("Download file")
    st.download_button(
        label="Download sorted document",
        data=pdf_bytes,
        file_name='sorted.pdf',
        mime='application/pdf',
    )



