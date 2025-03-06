import hashlib
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from get_page_sorting import (
    create_topic_mapping,
    create_topic_range_mapping,
    get_page_sorting,
    get_pages_mapping,
)
from parse_pdf import convert_pdf_to_images
from pdf_mapper import pdf_to_mappings

tmp_dir = "tmp"


def pdf_sorter_page():
    st.title("PDF-сортировка")
    os.makedirs(tmp_dir, exist_ok=True)

    # Инициализация сессионных переменных
    if "prev_hash" not in st.session_state:
        st.session_state.prev_hash = None
    if "full_output_path" not in st.session_state:
        st.session_state.full_output_path = None
    if "topic_files" not in st.session_state:
        st.session_state.topic_files = {}
    if "processing" not in st.session_state:
        st.session_state.processing = False

    # Загрузка данных о заполнении форм (один раз при инициализации)
    if "fill_status" not in st.session_state:
        try:
            fill_mapper_path = "topic_mapper/fill_mapper.csv"
            df_fill_mapper = pd.read_csv(
                fill_mapper_path, delimiter=";", dtype={"fill form": str}
            )
            fill_status = df_fill_mapper.set_index("document")["fill form"].to_dict()
            st.session_state.fill_status = fill_status
        except Exception as e:
            st.error(f"Ошибка загрузки fill_mapper: {e}")
            st.session_state.fill_status = {}

    # Выбор фильтра
    filter_option = st.selectbox(
        "Фильтр по заполнению форм:", ["all", "filled", "without fill"]
    )

    # Форма загрузки PDF
    pdf_file = st.file_uploader("Загрузите документ", type=["pdf"])

    if pdf_file is not None:
        try:
            # Вычисление хэша файла
            pdf_file.seek(0)
            current_hash = hashlib.md5(pdf_file.read()).hexdigest()
            pdf_file.seek(0)

            # Проверка на изменение файла
            if st.session_state.prev_hash != current_hash:
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
                    st.session_state.processing = False
                    processing_placeholder.empty()

                st.success("Готово!")

            else:
                st.info("Файл не изменился. Используются старые результаты.")

        except Exception as e:
            st.error(f"Ошибка: {str(e)}")
            st.session_state.processing = False

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

        # Кнопки для PDF по темам с фильтрацией
        if st.session_state.topic_files:
            fill_status = st.session_state.get("fill_status", {})
            filtered_topics = {}
            for topic, path in st.session_state.topic_files.items():
                fill_value = fill_status.get(topic, "0")
                if (
                    filter_option == "all"
                    or (filter_option == "filled" and fill_value == "1")
                    or (filter_option == "without fill" and fill_value == "0")
                ):
                    filtered_topics[topic] = path

            if filtered_topics:
                st.markdown("### PDF по темам:")
                for topic, path in filtered_topics.items():
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
