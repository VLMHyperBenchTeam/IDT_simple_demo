import glob
import os
from natsort import natsorted

def get_images_paths(directory):
    """
    Возвращает список путей ко всем .png файлам в указанной директории и её поддиректориях.

    :param directory: Путь к директории для поиска файлов.
    :return: Список строк с путями до .png файлов.
    """
    if not os.path.exists(directory):
        raise ValueError(f"Директория не существует: {directory}")

    # Рекурсивный поиск .png файлов
    pattern = os.path.join(directory, "**", "*.png")  # Шаблон для поиска
    images_paths = glob.glob(pattern, recursive=True)
    images_paths = natsorted(images_paths)

    return images_paths
