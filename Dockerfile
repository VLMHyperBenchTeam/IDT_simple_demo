FROM ghcr.io/vlmhyperbenchteam/qwen2.5-vl:ubuntu22.04-cu124-torch2.4.0_v0.1.0

# Создаем рабочую директорию
WORKDIR /workspace

RUN pip install "poetry==1.4.2"

COPY pyproject.toml poetry.lock ./
RUN poetry config installer.max-workers 4 && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Запускаем терминал
CMD ["sh"]