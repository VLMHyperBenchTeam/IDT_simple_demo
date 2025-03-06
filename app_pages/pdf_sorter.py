import hashlib
import os
import glob
from pathlib import Path
import streamlit as st
from get_page_sorting import (create_topic_mapping, get_page_sorting, get_pages_mapping)
from pdf_mapper import pdf_to_mappings
from utils.files import get_images_paths

tmp_dir = "tmp"

def pdf_sorter_page():
    st.title("PDF-сортировка")
    
    # Создаём директорию tmp
    os.makedirs(tmp_dir, exist_ok=True)

    pdf_file = st.file_uploader("Загрузите документ", type=["pdf"])

    # Инициализация состояния
    if "prev_hash" not in st.session_state:
        st.session_state.prev_hash = None

    if pdf_file is not None:
        try:
            # Вычисление MD5 хэша текущего файла
            pdf_file.seek(0)
            current_hash = hashlib.md5(pdf_file.read()).hexdigest()
            pdf_file.seek(0)

            # Очистка временных файлов при новом файле
            if st.session_state.prev_hash != current_hash:
                for f in glob.glob(f"{tmp_dir}/*"):
                    os.remove(f)

                # Сохранение загруженного файла
                temp_pdf_path = os.path.join(tmp_dir, "uploaded.pdf")
                with open(temp_pdf_path, "wb") as f:
                    f.write(pdf_file.read())

                # Проверка корректности файла
                if os.path.getsize(temp_pdf_path) == 0:
                    st.error("Файл пустой. Проверьте корректность загрузки.")
                    return

                # Создание временной папки для изображений
                image_folder = Path("images")
                image_folder.mkdir(parents=True, exist_ok=True)

                # Индикатор обработки
                processing_placeholder = st.empty()
                processing_placeholder.info("Идет обработка PDF...")

                try:
                    # Конвертация PDF в изображения
                    from parse_pdf import convert_pdf_to_images
                    convert_pdf_to_images(
                        pdf_path=Path(temp_pdf_path),
                        images_folder=image_folder
                    )

                    # Получение отсортированных данных
                    df_pages = get_page_sorting(image_folder)
                    pages_mapping = get_pages_mapping(df_pages)

                    # Создание полного PDF
                    full_output_path = os.path.join(tmp_dir, "sorted_full.pdf")
                    pdf_to_mappings(
                        pdf_in_path=temp_pdf_path,
                        mapping_list=pages_mapping,
                        output_file_path=full_output_path
                    )

                    # Создание PDF по темам
                    dfs_by_topic = create_topic_mapping(df_pages)
                    topic_files = {}
                    for topic in dfs_by_topic:
                        topic_pages = get_pages_mapping(dfs_by_topic[topic])
                        topic_output = os.path.join(tmp_dir, f"{topic}.pdf")
                        pdf_to_mappings(
                            pdf_in_path=temp_pdf_path,
                            mapping_list=topic_pages,
                            output_file_path=topic_output
                        )
                        topic_files[topic] = topic_output

                    st.session_state.prev_hash = current_hash

                except Exception as e:
                    st.error(f"Ошибка при обработке: {str(e)}")
                finally:
                    processing_placeholder.empty()

                st.success("PDF обработан успешно!")

            else:
                st.info("Файл не изменился. Используется предыдущий результат.")

            # Вывод ссылок
            if os.path.exists(full_output_path):
                st.markdown("### Скачать отсортированные PDF:")
                st.download_button(
                    label="Полный PDF",
                    data=open(full_output_path, "rb").read(),
                    file_name="sorted_full.pdf",
                    mime="application/pdf"
                )

                st.markdown("### PDF по темам:")
                for topic, path in topic_files.items():
                    if os.path.exists(path):
                        st.download_button(
                            label=f"Тема: {topic}",
                            data=open(path, "rb").read(),
                            file_name=f"{topic}.pdf",
                            mime="application/pdf"
                        )

        except Exception as e:
            st.error(f"Произошла ошибка: {str(e)}")
    else:
        st.warning("Пожалуйста, загрузите PDF-файл.")