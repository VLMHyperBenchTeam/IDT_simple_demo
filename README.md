# IDT_simple_demo

# Презентация возможностей по работе с документам с помощью VLM

# Отключение авторизации
В сервисе включена авторизация.

Чтобы убрать авторизацию на время теста, замените значения `actual_email` [4](https://github.com/VLMHyperBenchTeam/IDT_simple_demo/blob/main/utils/auth.py#L4) и `actual_password` [5](https://github.com/VLMHyperBenchTeam/IDT_simple_demo/blob/main/utils/auth.py#L5) на на пустые строки.

```
actual_email = "" # user@example.com
actual_password = "" # securepassword
```

При запуске сервиса, оставьте поля для ввода данных пользователя пустыми и просто нажмите на кнопку "Войти".

# Docker контейнер модели

Поддерживаются модели семейства Qwen2.5-VL:

* Qwen2.5-VL-3B-Instruct
* Qwen2.5-VL-7B-Instruct

## Build Docker image

Для сборки `Docker image` выполним команду:
```
docker build -t idt-demo-qwen2.5-vl:ubuntu22.04-cu124-torch2.4.0_demo_v0.1.0 -f docker/Dockerfile-cu124 .
```

## Run Docker Container

Для запуска `Docker Container` выполним команду:
```
docker run \
    --gpus all \
    -it \
    -v .:/workspace \
    -p 8501:8501 \
    idt-demo-qwen2.5-vl:ubuntu22.04-cu124-torch2.4.0_demo_v0.1.0 sh
```

Нам откроется терминал внутри `Docker Container`.

Для запуска предсказаний выполним в нем команду:
```
streamlit run main.py --server.port=8501 --server.address=0.0.0.0
```

Переходим по адресу ГПУ сервера `<ip-адрес-сервера>:8501/`

# Создание и запуск сервиса в виртуальном окружении poetry

Запуск:
1. Активируйте poetry shell
2. Установите библиотеки командой
```
poetry install --no-root
```
3. Запустите streamlit командой
```
streamlit run main.py
```