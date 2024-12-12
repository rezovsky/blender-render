FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    wget \
    libegl1 \
    libgl1-mesa-dev \
    libglu1-mesa \
    libxi6 \
    libxrender1 \
    libsm6 \
    libxrandr2 \
    xz-utils \
    libxkbcommon0 \
    python3-pip \
    && apt-get clean

RUN wget https://download.blender.org/release/Blender4.3/blender-4.3.0-linux-x64.tar.xz -O blender.tar.xz && \
    tar -xf blender.tar.xz && \
    mv blender-4.3.0-linux-x64 /opt/blender && \
    rm blender.tar.xz

RUN pip3 install --no-cache-dir fastapi uvicorn

# Указываем рабочую директорию для FastAPI
WORKDIR /app

# Устанавливаем переменную окружения для Blender
ENV PATH="/opt/blender:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

