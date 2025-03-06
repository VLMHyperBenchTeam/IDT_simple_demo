import os

import pandas as pd
import streamlit as st
from model_interface.model_factory import ModelFactory
from prompt_adapter.prompt_adapter import PromptAdapter

from utils.files import get_images_paths


@st.cache_resource
def load_model():
    cache_directory = "model_cache"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_directory = os.path.join(script_dir, cache_directory)
    model_name = "Qwen2.5-VL-7B-Instruct"
    model_family = "Qwen2.5-VL"
    package = "model_qwen2_5_vl"
    module = "models"
    model_class = "Qwen2_5_VLModel"
    model_class_path = f"{package}.{module}:{model_class}"
    ModelFactory.register_model(model_family, model_class_path)
    model_init_params = {
        "model_name": model_name,
        "system_prompt": "",
        "cache_dir": cache_directory,
    }
    model = ModelFactory.get_model(model_family, model_init_params)
    return model


# Загрузка модели
model = load_model()


def create_topic_mapping(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Создает отображение (mapping) между уникальными темами (page_topic) и соответствующими DataFrame.

    Args:
        df (pd.DataFrame): Входной DataFrame, содержащий столбец "page_topic".

    Returns:
        Dict[str, pd.DataFrame]: Словарь, где:
            - Ключи (str) — уникальные значения из столбца "page_topic".
            - Значения (pd.DataFrame) — фреймы данных, содержащие только строки с соответствующей темой.

    Examples:
        >>> import pandas as pd
        >>> data = {
        ...     "page_topic": ["Topic1", "Topic1", "Topic2"],
        ...     "src_page_num": [1, 2, 3],
        ...     "page_num": [4, 5, 6]
        ... }
        >>> df = pd.DataFrame(data)
        >>> topic_mapping = create_topic_mapping(df)
        >>> len(topic_mapping)  # Должно быть 2 уникальных темы
        2
        >>> topic_mapping["Topic1"].shape  # Размер DataFrame для "Topic1"
        (2, 3)
    """
    # unique_topics = df["page_topic"].unique()
    # dataframes_by_topic = {topic: df[df["page_topic"] == topic] for topic in unique_topics}

    dataframes_by_topic = {topic: group for topic, group in df.groupby("page_topic")}
    return dataframes_by_topic


def get_pages_mapping(df_pages: pd.DataFrame) -> list[int]:
    """
    Создает pages_mapping отображение исходных номеров страниц. Результат нужен для функции pdf_to_mappings.
    Чтобы создать из отсортированого DataFrame с номерами исходных страницс pdf, где они в правильном порядке.

    Args:
        df_pages (pd.DataFrame): Входной DataFrame, содержащий столбец "src_page_num" с исходными номерами страниц.

    Returns:
        list[int]: Список целых чисел, где каждый элемент равен соответствующему значению из "src_page_num" минус 1.

    Examples:
        >>> import pandas as pd
        >>> data = {"src_page_num": [29, 19, 34]}
        >>> df = pd.DataFrame(data)
        >>> get_pages_mapping(df)
        [28, 18, 33]
    """
    pages_mapping = df_pages["src_page_num"].values - 1
    pages_mapping = pages_mapping.astype(int)
    pages_mapping = pages_mapping.tolist()

    return pages_mapping


def get_page_sorting(images_dir):
    images_paths = get_images_paths(images_dir)

    # Создаем progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()

    # считываем промпты из коллекции
    current_prompt_collection = "JuliaJu_en_Qwen2_5-VL-7B.csv"
    prompt_adapter = PromptAdapter(
        current_prompt_collection, file_dir="PromptCollection"
    )

    page_num_prompt = prompt_adapter.get_prompt("doc", "Номер страницы")
    page_topic_prompt = prompt_adapter.get_prompt("doc", "Название блока")
    pages_data = {"src_page_num": [], "page_num": [], "page_topic": []}

    total_images = len(images_paths)

    # получаем предсказания от модели
    for idx, image_path in enumerate(images_paths):
        page_num = model.predict_on_image(image=image_path, question=page_num_prompt)
        page_topic = model.predict_on_image(
            image=image_path, question=page_topic_prompt
        )

        # Обновляем данные
        pages_data["src_page_num"].append(idx + 1)
        pages_data["page_num"].append(page_num)
        pages_data["page_topic"].append(page_topic)

        # Обновляем progress bar
        progress_percent = (idx + 1) / total_images
        progress_bar.progress(progress_percent)
        progress_text.text(f"Обработано {idx + 1} из {total_images} изображений")

    progress_text.text("Обработка завершена!")

    # Сортировка страниц pdf-документаА
    df_pages = pd.DataFrame(pages_data)
    df_pages.sort_values(
        by=["page_topic", "page_num"], ascending=[True, True], inplace=True
    )

    # Чтобы навания тем не содержали "/" он будет воприниматься как вложеная папка
    df_pages["page_topic"] = df_pages["page_topic"].str.replace("/", "-", regex=False)

    return df_pages
