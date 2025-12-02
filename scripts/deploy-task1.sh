#!/bin/bash

# Script de deploy para Task 1 do TP3
# Este script facilita o processo de criação e aplicação dos ConfigMaps

set -e  # Parar em caso de erro

echo "=============================================="
echo "  TP3 - Task 1: Deploy da Função Serverless"
echo "=============================================="
echo ""

# Verificar se o ID do estudante foi fornecido
if [ -z "$1" ]; then
    echo "❌ ERRO: ID do estudante não fornecido!"
    echo ""
    echo "Uso: ./deploy-task1.sh <seu-id-estudante>"
    echo "Exemplo: ./deploy-task1.sh ifs4"
    echo ""
    exit 1
fi

STUDENT_ID="$1"
OUTPUT_KEY="${STUDENT_ID}-proj3-output"

echo "📋 Configuração:"
echo "   - ID do Estudante: $STUDENT_ID"
echo "   - Redis Output Key: $OUTPUT_KEY"
echo ""

# Determinar diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TASK1_DIR="$PROJECT_ROOT/task1"

# Verificar se os arquivos necessários existem
if [ ! -f "$TASK1_DIR/handler_module.py" ]; then
    echo "❌ ERRO: task1/handler_module.py não encontrado!"
    echo "   Certifique-se de estar executando este script da raiz do projeto"
    exit 1
fi

echo "✅ Arquivos verificados"
echo ""

# Criar ConfigMap pyfile
echo "📦 Criando ConfigMap 'pyfile'..."
kubectl create configmap pyfile \
    --from-file pyfile="$TASK1_DIR/handler_module.py" \
    --dry-run=client \
    --output yaml > "$TASK1_DIR/configmap-pyfile-generated.yaml"

echo "✅ ConfigMap 'pyfile' gerado em task1/configmap-pyfile-generated.yaml"
echo ""

# Criar ConfigMap outputkey
echo "📦 Criando ConfigMap 'outputkey'..."
kubectl create configmap outputkey \
    --from-literal REDIS_OUTPUT_KEY="$OUTPUT_KEY" \
    --dry-run=client \
    --output yaml > "$TASK1_DIR/configmap-outputkey-generated.yaml"

echo "✅ ConfigMap 'outputkey' gerado em task1/configmap-outputkey-generated.yaml"
echo ""

# Perguntar se deve aplicar
read -p "🚀 Deseja aplicar os ConfigMaps no cluster? (s/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo ""
    echo "📤 Aplicando ConfigMaps no Kubernetes..."
    
    kubectl apply -f "$TASK1_DIR/configmap-pyfile-generated.yaml"
    kubectl apply -f "$TASK1_DIR/configmap-outputkey-generated.yaml"
    
    echo ""
    echo "✅ ConfigMaps aplicados com sucesso!"
    echo ""
    
    # Perguntar se deve aplicar o deployment
    if [ -f "$TASK1_DIR/serverless-deployment-course.yaml" ]; then
        read -p "🚀 Deseja aplicar o deployment também? (s/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[SsYy]$ ]]; then
            echo ""
            echo "📤 Aplicando deployment..."
            kubectl apply -f "$TASK1_DIR/serverless-deployment-course.yaml"
            echo ""
            echo "✅ Deployment aplicado!"
            echo ""
            
            # Aguardar um pouco
            echo "⏳ Aguardando pod iniciar (10 segundos)..."
            sleep 10
            
            # Mostrar status
            echo ""
            echo "📊 Status dos pods:"
            kubectl get pods -l app=serverless-redis
            echo ""
            
            # Obter nome do pod
            POD_NAME=$(kubectl get pods -l app=serverless-redis -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
            
            if [ ! -z "$POD_NAME" ]; then
                echo "📋 Ver logs do pod:"
                echo "   kubectl logs -f $POD_NAME"
            fi
        fi
    else
        echo "⚠️  Arquivo serverless-deployment-course.yaml não encontrado"
        echo "   O deployment precisa ser aplicado manualmente"
    fi
    
    echo ""
    echo "📋 Comandos úteis:"
    echo "   • Ver pods: kubectl get pods"
    echo "   • Ver logs: kubectl logs -f <nome-do-pod>"
    echo "   • Verificar Redis: redis-cli -h 67.159.94.11 -p 6379 get $OUTPUT_KEY"
    echo ""
else
    echo ""
    echo "ℹ️  ConfigMaps gerados mas não aplicados."
    echo "   Para aplicar manualmente, execute:"
    echo "   kubectl apply -f configmap-pyfile-generated.yaml"
    echo "   kubectl apply -f configmap-outputkey-generated.yaml"
    echo ""
fi

echo "✨ Concluído!"

