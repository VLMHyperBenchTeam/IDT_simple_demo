# IDT_simple_demo

# Презентация возможностей по работе с документам с помощью VLM

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

# Инструкция от Насти

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
4. Чтобы убрать регистрацию на время теста, удалите значения на строках [69](https://github.com/VLMHyperBenchTeam/IDT_simple_demo/blob/dev/main.py#L69) и [70](https://github.com/VLMHyperBenchTeam/IDT_simple_demo/blob/dev/main.py#L70)
