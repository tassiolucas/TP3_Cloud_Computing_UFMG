# Dockerfile para Runtime Serverless Customizado - TP3
# Autor: [SEU NOME]

FROM python:3.9-slim

# Metadados
LABEL maintainer="seu-email@exemplo.com"
LABEL version="1.0"
LABEL description="Runtime Serverless Customizado para TP3 Cloud Computing"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar pacotes Python comuns (conforme especificação)
RUN pip install --no-cache-dir \
    numpy>=1.21.0 \
    pandas>=1.3.0 \
    matplotlib>=3.4.0 \
    scikit-learn>=0.24.0 \
    requests>=2.26.0 \
    tqdm>=4.62.0

# Copiar código do runtime
COPY runtime.py .

# Criar diretório para pyfile (será montado via ConfigMap)
RUN mkdir -p /app/pyfile

# Variáveis de ambiente padrão
ENV REDIS_HOST=localhost
ENV REDIS_PORT=6379
ENV REDIS_INPUT_KEY=metrics
ENV REDIS_OUTPUT_KEY=output
ENV MONITORING_PERIOD=5
ENV HANDLER_FUNCTION=handler_module.handler
ENV PYFILE_PATH=/app/pyfile/pyfile

# Healthcheck (opcional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import redis; r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT}); r.ping()" || exit 1

# Executar runtime
CMD ["python", "-u", "runtime.py"]

