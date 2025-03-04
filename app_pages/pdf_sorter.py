import hashlib
import os
from pathlib import Path

import streamlit as st

from get_page_sorting import get_page_sorting
from parse_pdf import convert_pdf_to_images
from pdf_mapper import pdf_to_mappings


def pdf_sorter_page():
    st.title("PDF-сортировка")

    # Форма для загрузки PDF
    pdf_file = st.file_uploader("Загрузите документ", type=["pdf"])
    
    output_file_path = "sorted_output.pdf"

    # Инициализация состояния
    if "prev_hash" not in st.session_state:
        st.session_state.prev_hash = None

    if pdf_file is not None:
        try:
            # Вычисляем MD5 хэш текущего файла
            pdf_file.seek(0)
            current_hash = hashlib.md5(pdf_file.read()).hexdigest()
            pdf_file.seek(0)

            # Проверяем изменение файла
            if st.session_state.prev_hash != current_hash:
                # Удаляем предыдущий отсортированный PDF
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)

                # Сохраняем временный файл
                temp_pdf_path = "uploaded.pdf"
                with open(temp_pdf_path, "wb") as f:
                    f.write(pdf_file.read())

                # Проверяем размер файла
                if os.path.getsize(temp_pdf_path) == 0:
                    st.error("Файл пустой. Проверьте корректность загрузки PDF.")
                    return

                # Создаем папку для изображений
                image_folder = Path("images")
                image_folder.mkdir(parents=True, exist_ok=True)

                # Индикатор обработки
                processing_placeholder = st.empty()
                processing_placeholder.info("Идет обработка PDF...")

                try:
                    # Конвертация PDF в изображения
                    convert_pdf_to_images(
                        pdf_path=Path(temp_pdf_path), images_folder=image_folder
                    )

                    # Получение порядка страниц
                    pages_mapping = get_page_sorting(image_folder)

                    # Создание отсортированного PDF
                    pdf_to_mappings(
                        pdf_in_path=temp_pdf_path,
                        mapping_list=pages_mapping,
                        output_file_path=output_file_path,
                    )

                    st.session_state.prev_hash = current_hash
                except Exception as e:
                    st.error(f"Ошибка при обработке PDF: {str(e)}")
                finally:
                    processing_placeholder.empty()

                st.success("PDF обработан успешно!")

            else:
                st.info("Файл не изменился. Используется предыдущий результат.")

            # Показываем кнопку для скачивания
            if Path(output_file_path).exists():
                with open(output_file_path, "rb") as file:
                    pdf_bytes = file.read()
                st.download_button(
                    label="Скачать отсортированный PDF",
                    data=pdf_bytes,
                    file_name="sorted_output.pdf",
                    mime="application/pdf",
                )

        except Exception as e:
            st.error(f"Произошла ошибка: {str(e)}")
    else:
        st.warning("Пожалуйста, загрузите PDF-файл.")
