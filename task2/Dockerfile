# Dockerfile para Dashboard TP3
FROM python:3.9-slim

# Metadados
LABEL maintainer="TP3 UFMG"
LABEL description="Dashboard de monitoramento para TP3"

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do dashboard
COPY dashboard.py .

# Expor porta padrão do Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Comando para executar o dashboard
CMD ["streamlit", "run", "dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.serverAddress=0.0.0.0", \
     "--browser.gatherUsageStats=false", \
     "--server.fileWatcherType=none"]

