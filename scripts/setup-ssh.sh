#!/bin/bash

# Script para configurar acesso SSH à VM do TP3
# Adiciona configuração ao ~/.ssh/config automaticamente

set -e

echo "=============================================="
echo "  TP3 - Configuração de Acesso SSH"
echo "=============================================="
echo ""

# Verificar se o usuário foi fornecido
if [ -z "$1" ]; then
    echo "❌ ERRO: Usuário não fornecido!"
    echo ""
    echo "Uso: ./setup-ssh.sh <seu-usuario>"
    echo "Exemplo: ./setup-ssh.sh tassmarques"
    echo ""
    exit 1
fi

USERNAME="$1"
SSH_CONFIG="$HOME/.ssh/config"

echo "📋 Configuração:"
echo "   - Usuário: $USERNAME"
echo "   - Servidor: pugna.snes.2advanced.dev"
echo "   - Porta: 51927"
echo ""

# Criar diretório .ssh se não existir
if [ ! -d "$HOME/.ssh" ]; then
    echo "📁 Criando diretório ~/.ssh..."
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
fi

# Verificar se já existe configuração
if [ -f "$SSH_CONFIG" ]; then
    if grep -q "Host cloud2" "$SSH_CONFIG"; then
        echo "⚠️  Configuração 'cloud2' já existe em $SSH_CONFIG"
        echo ""
        read -p "   Deseja sobrescrever? (s/n): " -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
            echo "ℹ️  Configuração mantida como está."
            exit 0
        fi
        
        # Remover configuração antiga
        echo "🗑️  Removendo configuração antiga..."
        # Backup
        cp "$SSH_CONFIG" "$SSH_CONFIG.backup.$(date +%Y%m%d%H%M%S)"
        # Remover seção cloud2 (simplificado - remove apenas as linhas básicas)
        sed -i.tmp '/^Host cloud2$/,/^$/d' "$SSH_CONFIG" 2>/dev/null || true
        rm -f "$SSH_CONFIG.tmp"
    fi
fi

# Adicionar nova configuração
echo "📝 Adicionando configuração ao $SSH_CONFIG..."

cat >> "$SSH_CONFIG" << EOF

# TP3 - Mestrado UFMG
Host cloud2
    HostName pugna.snes.2advanced.dev
    Port 51927
    User $USERNAME
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF

echo "✅ Configuração adicionada com sucesso!"
echo ""

# Ajustar permissões
chmod 600 "$SSH_CONFIG"
echo "🔒 Permissões ajustadas (600)"
echo ""

# Testar conexão
echo "🔍 Deseja testar a conexão agora? (s/n): "
read -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo ""
    echo "🔌 Testando conexão..."
    echo "   (Se solicitar senha, forneça suas credenciais)"
    echo ""
    
    ssh -o ConnectTimeout=10 cloud2 "echo '✅ Conexão estabelecida com sucesso!'"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Tudo funcionando!"
        echo ""
        echo "📋 Agora você pode conectar com:"
        echo "   ssh cloud2"
        echo ""
        echo "🔧 Comandos úteis:"
        echo "   • SSH Tunnel Redis: ssh -L 6379:192.168.121.48:6379 cloud2"
        echo "   • Copiar arquivos: scp arquivo.yaml cloud2:~/"
        echo "   • Sync diretório: rsync -avz ./TP3/ cloud2:~/TP3/"
    fi
else
    echo ""
    echo "ℹ️  Configuração salva. Para conectar, use:"
    echo "   ssh cloud2"
fi

echo ""
echo "✨ Configuração concluída!"
echo ""
echo "📖 Para mais informações, consulte: CONFIGURACAO_SSH.md"

