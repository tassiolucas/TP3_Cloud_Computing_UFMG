#!/bin/bash
# Script para build e push da imagem do Dashboard (Task 2)
# Autor: [SEU NOME]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Task 2: Build e Push do Dashboard${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Erro: Docker não está rodando!${NC}"
    exit 1
fi

# Solicitar usuário Docker Hub
read -p "Digite seu usuário do Docker Hub: " DOCKER_USER

if [ -z "$DOCKER_USER" ]; then
    echo -e "${RED}❌ Usuário não pode ser vazio!${NC}"
    exit 1
fi

# Definir tag
IMAGE_NAME="$DOCKER_USER/tp3-dashboard"
IMAGE_TAG="v1"
FULL_IMAGE="$IMAGE_NAME:$IMAGE_TAG"

echo -e "${YELLOW}📦 Imagem: $FULL_IMAGE${NC}"
echo

# Fazer login no Docker Hub
echo -e "${YELLOW}🔐 Fazendo login no Docker Hub...${NC}"
docker login

# Build da imagem
echo
echo -e "${YELLOW}🔨 Fazendo build da imagem...${NC}"
docker build -t "$FULL_IMAGE" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build concluído com sucesso!${NC}"
else
    echo -e "${RED}❌ Erro no build!${NC}"
    exit 1
fi

# Testar imagem localmente (opcional)
echo
read -p "Deseja testar a imagem localmente antes do push? (s/N): " TEST_LOCAL

if [[ "$TEST_LOCAL" =~ ^[Ss]$ ]]; then
    echo
    read -p "Digite seu ID de estudante (ex: ifs4): " STUDENT_ID
    
    if [ -z "$STUDENT_ID" ]; then
        echo -e "${RED}❌ ID não pode ser vazio!${NC}"
        exit 1
    fi
    
    REDIS_KEY="$STUDENT_ID-proj3-output"
    
    echo -e "${YELLOW}🧪 Testando imagem localmente...${NC}"
    echo -e "${YELLOW}   Acesse: http://localhost:8501${NC}"
    echo -e "${YELLOW}   Pressione Ctrl+C para parar${NC}"
    echo
    
    docker run --rm \
        -p 8501:8501 \
        -e REDIS_HOST=192.168.121.171 \
        -e REDIS_PORT=6379 \
        -e REDIS_OUTPUT_KEY="$REDIS_KEY" \
        "$FULL_IMAGE"
fi

# Push da imagem
echo
echo -e "${YELLOW}📤 Fazendo push da imagem...${NC}"
        docker push "$FULL_IMAGE"
        
        if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Push concluído com sucesso!${NC}"
else
    echo -e "${RED}❌ Erro no push!${NC}"
    exit 1
fi

# Resumo
echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ Processo Concluído!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "📝 Próximos passos:"
echo -e "  1. Edite dashboard-deployment.yaml:"
echo -e "     ${YELLOW}image: $FULL_IMAGE${NC}"
echo -e "  2. Aplique no Kubernetes:"
echo -e "     ${YELLOW}kubectl apply -f dashboard-deployment.yaml${NC}"
echo -e "     ${YELLOW}kubectl apply -f dashboard-service.yaml${NC}"
echo
