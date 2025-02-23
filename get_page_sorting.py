import streamlit as st
import os
import re
from model_interface.model_factory import ModelFactory
@st.cache_resource
def load_model():
    cache_directory = "model_cache"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_directory = os.path.join(script_dir, cache_directory)
    model_name_1 = "Qwen2.5-VL-7B-Instruct"
    model_family = "Qwen2.5-VL"
    package = "model_qwen2_5_vl"
    module = "models"
    model_class = "Qwen2_5_VLModel"
    model_class_path = f"{package}.{module}:{model_class}"
    ModelFactory.register_model(model_family, model_class_path)
    model_init_params = {
        "model_name": model_name_1,
        "system_prompt": "",
        "cache_dir": cache_directory,
    }
    model = ModelFactory.get_model(model_family, model_init_params)
    return model

# Загрузка модели
model = load_model()


PROMPT = """Перед вами {number_page} изображений страниц одного типа документа, которые находятся в хаотичном порядке.
            Анализируя содержимое предоставленных страниц документа, определите логический порядок страниц и выведите их в виде цифр через запятую.
            Страницы содержат различные разделы договора о беспроцентном займе, включая условия займа, порядок передачи и возврата суммы займа, ответственность сторон, форс-мажорные обстоятельства, разрешение споров, изменения и досрочное расторжение договора, а также заключительные положения.
            Пожалуйста, проанализируйте текст на каждой странице и укажите правильный порядок только в виде порядка страниц через запятую.
"""
def get_page_sorting(image_path):
    model_answer = model.predict_on_images(images=image_path, question=PROMPT.format(number_page=len(image_path)))
    model_answer = re.findall(r'\d+', model_answer)
    model_answer  = list(map(int, model_answer))
    return model_answer


