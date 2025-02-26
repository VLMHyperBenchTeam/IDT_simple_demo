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


def get_page_sorting(images_dir):
    images_paths = get_images_paths(images_dir)
    
    # Создаем progress bar
    progress_bar = st.progress(0)  # Инициализируем progress bar с 0%
    progress_text = st.empty()  # Добавляем текст для отображения текущего статуса
    
    # считываем промпты из коллекции
    current_prompt_collection = "JuliaJu_en_Qwen2_5-VL-7B.csv"
    prompt_adapter = PromptAdapter(
        current_prompt_collection, file_dir="PromptCollection"
    )
    page_num_prompt = prompt_adapter.get_prompt("doc", "Номер страницы")
    page_topic_prompt = prompt_adapter.get_prompt("doc", "Название блока")
    pages_data = {"src_page_num": [], "page_num": [], "page_topic": []}
    
    total_images = len(images_paths)  # Общее количество изображений
    
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
    
    # обработка
    df_pages = pd.DataFrame(pages_data)
    df_pages.sort_values(
        by=["page_topic", "page_num"], ascending=[True, True], inplace=True
    )
    
    # pages_mapping = df_pages[['src_page_num', 'page_num']].values.tolist()
    pages_mapping = df_pages['src_page_num'].values - 1
    pages_mapping = pages_mapping.astype(int)
    pages_mapping = pages_mapping.tolist()
    
    return pages_mapping
    
    
   
