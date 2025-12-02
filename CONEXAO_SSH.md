# 🔐 Informações de Conexão SSH - TP3

## 📋 Suas Credenciais

**VM:** `pugna.snes.2advanced.dev`  
**Porta:** `51927`  
**Usuário:** `tassioalmeida`  
**Chave SSH:** `~/.ssh/tassioUFMG`  
**ID Estudante:** `2025720437`

---

## 🚀 Conexão Rápida

### Comando Completo
```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

### Com Túnel SSH (para Dashboard)
```bash
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:SUA_PORTA tassioalmeida@pugna.snes.2advanced.dev -p 51927
```
Depois acesse: http://localhost:8501

---

## ⚙️ Configurar SSH Config

Para facilitar, adicione ao seu `~/.ssh/config`:

```bash
Host tp3-cloud
    HostName pugna.snes.2advanced.dev
    Port 51927
    User tassioalmeida
    IdentityFile ~/.ssh/tassioUFMG
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

Depois, conecte simplesmente com:
```bash
ssh tp3-cloud
```

---

## 🔧 Script de Configuração

Execute este script para configurar automaticamente:

```bash
cat >> ~/.ssh/config << 'EOF'

# TP3 Cloud Computing UFMG
Host tp3-cloud
    HostName pugna.snes.2advanced.dev
    Port 51927
    User tassioalmeida
    IdentityFile ~/.ssh/tassioUFMG
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF

echo "✅ Configuração SSH adicionada!"
echo "Agora conecte com: ssh tp3-cloud"
```

---

## 📊 Informações do Redis

### Redis na VM (para acesso de containers)
```bash
Host: 192.168.121.171
Port: 6379
```
**⚠️ IMPORTANTE:** Use `192.168.121.171` para acesso de dentro de containers/pods!

### Redis externo
```bash
Host: 67.159.94.11
Port: 6379
```

### Testar conexão
```bash
# Conectar na VM primeiro
ssh tp3-cloud

# Testar Redis
redis-cli -h 192.168.121.171 -p 6379 ping
redis-cli -h 192.168.121.171 -p 6379 get 2025720437-proj3-output
```

---

## 🔑 Suas Chaves Redis

**Input (métricas coletadas):** `metrics`  
**Output (suas métricas processadas):** `2025720437-proj3-output`

---

## 🎯 Comandos Úteis

### Conectar
```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

### Copiar arquivo para VM
```bash
scp -i ~/.ssh/tassioUFMG -P 51927 arquivo.yaml tassioalmeida@pugna.snes.2advanced.dev:~/
```

### Copiar arquivo da VM
```bash
scp -i ~/.ssh/tassioUFMG -P 51927 tassioalmeida@pugna.snes.2advanced.dev:~/arquivo.log .
```

### Executar comando remoto
```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927 "kubectl get pods"
```

### Túnel SSH para Dashboard (exemplo porta 30600)
```bash
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:30600 tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

---

## 🆘 Troubleshooting

### Erro: Permission denied (publickey)
```bash
# Verificar permissões da chave
chmod 600 ~/.ssh/tassioUFMG

# Testar conexão com verbose
ssh -v -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

### Erro: Connection refused
```bash
# Verificar se Redis está acessível
telnet 192.168.121.171 6379

# Verificar se chave está no lugar correto
ls -la ~/.ssh/tassioUFMG
```

### Erro: Host key verification failed
```bash
# Remover entrada antiga do known_hosts
ssh-keygen -R "[pugna.snes.2advanced.dev]:51927"

# Conectar novamente
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

---

## 📝 Checklist de Primeira Conexão

- [ ] Verificar chave SSH existe: `ls -la ~/.ssh/tassioUFMG`
- [ ] Ajustar permissões: `chmod 600 ~/.ssh/tassioUFMG`
- [ ] Configurar SSH config (opcional)
- [ ] Conectar na VM
- [ ] Verificar kubectl funciona: `kubectl get nodes`
- [ ] Testar Redis: `redis-cli -h 192.168.121.171 -p 6379 ping`
- [ ] Clonar/copiar repositório do projeto
- [ ] Pronto para começar! 🚀

---

## 🎓 Workflows Comuns

### Deploy Task 1
```bash
# Conectar
ssh tp3-cloud

# Navegar e aplicar
cd TP3_Cloud_Computing_UFMG/task1
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
kubectl apply -f serverless-deployment-course.yaml

# Verificar
kubectl get pods
kubectl logs -f <pod-name>

# Testar
redis-cli -h 192.168.121.171 -p 6379 get 2025720437-proj3-output
```

### Acessar Dashboard (Task 2)
```bash
# Terminal 1: Criar túnel (exemplo porta 30600)
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:30600 tassioalmeida@pugna.snes.2advanced.dev -p 51927

# Terminal 2: Abrir navegador
open http://localhost:8501
```

### Ver logs em tempo real
```bash
ssh tp3-cloud "kubectl logs -f deployment/serverless-runtime"
```

---

## ✅ Teste de Conexão

Execute este comando para testar tudo:

```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927 << 'EOF'
echo "✅ Conexão SSH funcionando!"
echo ""
echo "📊 Testando kubectl..."
kubectl get nodes
echo ""
echo "💾 Testando Redis..."
redis-cli -h 192.168.121.171 -p 6379 ping
echo ""
echo "🎯 Tudo funcionando corretamente!"
EOF
```

---

**Salve este arquivo para referência rápida! 📌**

