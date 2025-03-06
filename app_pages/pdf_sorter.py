import hashlib
import os
from pathlib import Path
import streamlit as st
from get_page_sorting import (
    create_topic_mapping,
    get_page_sorting,
    get_pages_mapping,
    create_topic_range_mapping,
)
from parse_pdf import convert_pdf_to_images
from pdf_mapper import pdf_to_mappings

tmp_dir = "tmp"


def pdf_sorter_page():
    st.title("PDF-сортировка")
    os.makedirs(tmp_dir, exist_ok=True)  # Создание tmp директории

    # Инициализация сессионных переменных
    if "prev_hash" not in st.session_state:
        st.session_state.prev_hash = None
    if "full_output_path" not in st.session_state:
        st.session_state.full_output_path = None
    if "topic_files" not in st.session_state:
        st.session_state.topic_files = {}
    if "processing" not in st.session_state:
        st.session_state.processing = False  # Флаг обработки

    # Форма загрузки PDF (остается доступной даже во время обработки)
    pdf_file = st.file_uploader("Загрузите документ", type=["pdf"])

    if pdf_file is not None:
        try:
            # Вычисление хэша файла
            pdf_file.seek(0)
            current_hash = hashlib.md5(pdf_file.read()).hexdigest()
            pdf_file.seek(0)

            # Проверка на изменение файла
            if st.session_state.prev_hash != current_hash:
                # Установка флага обработки
                st.session_state.processing = True

                # Очистка предыдущих файлов
                for f in os.listdir(tmp_dir):
                    os.remove(os.path.join(tmp_dir, f))

                # Сохранение временного файла
                temp_pdf_path = os.path.join(tmp_dir, "uploaded.pdf")
                with open(temp_pdf_path, "wb") as f:
                    f.write(pdf_file.read())

                # Проверка размера файла
                if os.path.getsize(temp_pdf_path) == 0:
                    st.error("Файл пустой.")
                    st.session_state.processing = False
                    return

                # Создание папки для изображений
                image_folder = Path("images")
                image_folder.mkdir(parents=True, exist_ok=True)

                # Индикатор обработки
                processing_placeholder = st.empty()
                processing_placeholder.info("Идет обработка...")

                try:
                    # Конвертация PDF в изображения
                    convert_pdf_to_images(
                        pdf_path=Path(temp_pdf_path), images_folder=image_folder
                    )

                    # Обработка страниц
                    df_pages = get_page_sorting(image_folder)
                    pages_mapping = get_pages_mapping(df_pages)

                    # Создание полного PDF
                    full_output_path = os.path.join(tmp_dir, "sorted_full.pdf")
                    pdf_to_mappings(
                        pdf_in_path=temp_pdf_path,
                        mapping_list=pages_mapping,
                        output_file_path=full_output_path,
                    )

                    # Создание PDF по темам
                    dfs_by_topic = create_topic_mapping(df_pages)
                    dfs_by_topic = create_topic_range_mapping(dfs_by_topic)
                    topic_files = {}
                    for topic in dfs_by_topic:
                        topic_pages = get_pages_mapping(dfs_by_topic[topic])
                        topic_output = os.path.join(tmp_dir, f"{topic}.pdf")
                        pdf_to_mappings(
                            pdf_in_path=temp_pdf_path,
                            mapping_list=topic_pages,
                            output_file_path=topic_output,
                        )
                        topic_files[topic] = topic_output

                    # Сохранение результатов в сессию
                    st.session_state.full_output_path = full_output_path
                    st.session_state.topic_files = topic_files
                    st.session_state.prev_hash = current_hash

                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
                finally:
                    st.session_state.processing = False  # Сброс флага
                    processing_placeholder.empty()

                st.success("Готово!")

            else:
                st.info("Файл не изменился. Используются старые результаты.")

        except Exception as e:
            st.error(f"Ошибка: {str(e)}")
            st.session_state.processing = False  # Сброс флага при ошибке

    # Вывод кнопок только если обработка завершена
    if not st.session_state.processing:
        # Кнопка для полного PDF
        if st.session_state.full_output_path and os.path.exists(
            st.session_state.full_output_path
        ):
            with open(st.session_state.full_output_path, "rb") as f:
                st.download_button(
                    label="Скачать полный PDF",
                    data=f.read(),
                    file_name="sorted_full.pdf",
                    mime="application/pdf",
                )

        # Кнопки по темам
        if st.session_state.topic_files:
            st.markdown("### PDF по темам:")
            for topic, path in st.session_state.topic_files.items():
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        st.download_button(
                            label=f"Скачать {topic}",
                            data=f.read(),
                            file_name=f"{topic}.pdf",
                            mime="application/pdf",
                        )
    else:
        st.info("Идет обработка... Пожалуйста, подождите.")
