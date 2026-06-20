FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# numpy/scipy/sympy 均有预编译 wheel，无需 apt 装 gcc（避免卡在 debian 源下载）
ARG PIP_INDEX=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
COPY requirements.txt .
RUN pip install --no-cache-dir -i "$PIP_INDEX" -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
