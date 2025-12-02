# ✅ Como Verificar se Está Funcionando - TP3

## 🎯 Seu Status Atual

Vejo que você já tem o pod rodando! ✅
```
serverless-redis-796b57c8f9-tgs5v   1/1   Running   0   5s
```

Agora vamos verificar se está processando dados corretamente.

---

## 📊 Método 1: Ver Logs do Pod (MAIS RÁPIDO)

Este é o jeito mais fácil de ver se está funcionando:

```bash
kubectl logs -f serverless-redis-796b57c8f9-tgs5v
```

**O que procurar nos logs:**
- ✅ Mensagens de execução da função
- ✅ Sem erros de Python
- ✅ Confirmação de que está salvando no Redis

---

## 🐍 Método 2: Script Python (SEM PRECISAR DE redis-cli)

Copie o script para a VM e execute:

```bash
# Já está no seu repositório!
cd ~/TP3_Cloud_Computing_UFMG/scripts
python3 check_redis.py
```

**O script vai mostrar:**
- ✅ Se Redis está acessível
- ✅ Se dados de entrada (metrics) existem
- ✅ Se sua função gerou output (2025720437-proj3-output)
- ✅ Conteúdo completo do resultado

---

## 🔧 Método 3: Usar Pod Temporário com redis-cli

Se quiser ter o redis-cli:

```bash
# Criar pod temporário com redis
kubectl run redis-client --rm -it --restart=Never --image=redis:latest -- bash

# Dentro do pod, execute:
redis-cli -h 192.168.121.171 -p 6379
```

Comandos úteis no redis-cli:
```redis
# Ver sua saída
get 2025720437-proj3-output

# Ver entrada
get metrics

# Listar todas as chaves
keys *

# Sair
exit
```

---

## 📋 Método 4: Instalar redis-cli na VM (opcional)

Se quiser instalar permanentemente:

```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install redis-tools -y

# Depois usar:
redis-cli -h 192.168.121.171 -p 6379 get 2025720437-proj3-output
```

---

## 🎯 Checklist de Verificação

Execute estes comandos na ordem:

### 1. ✅ Verificar Pod Está Rodando
```bash
kubectl get pods | grep serverless
```
**Esperado:** Status "Running"

### 2. ✅ Ver Logs
```bash
kubectl logs serverless-redis-796b57c8f9-tgs5v
```
**Esperado:** Sem erros, mensagens de execução

### 3. ✅ Verificar Redis com Script Python
```bash
cd ~/TP3_Cloud_Computing_UFMG/scripts
python3 check_redis.py
```
**Esperado:** JSON com suas métricas

### 4. ✅ Testar Continuamente
```bash
# Ver logs em tempo real
kubectl logs -f serverless-redis-796b57c8f9-tgs5v

# Executar script a cada 5 segundos
watch -n 5 python3 ~/TP3_Cloud_Computing_UFMG/scripts/check_redis.py
```

---

## 🔍 O Que Você Deve Ver

### Saída Esperada do Script Python:

```
================================================================================
🔍 Verificador de Redis - TP3
================================================================================
📍 Redis: 192.168.121.48:6379
🔑 Output Key: 2025720437-proj3-output
🔑 Input Key: metrics
================================================================================

🔌 Conectando ao Redis...
✅ Conectado ao Redis com sucesso!

📥 Verificando dados de entrada...
--------------------------------------------------------------------------------
✅ Chave 'metrics' existe!
   📊 Timestamp: 2025-11-30T11:20:00
   💻 CPUs monitoradas: 4
   📈 CPU 0: 45.5%
   💾 Memória Total: 15.75 GB

📤 Verificando dados de saída (sua função)...
--------------------------------------------------------------------------------
✅ Chave '2025720437-proj3-output' existe!

📊 Resultado da sua função:
{
  "percent-network-egress": 20.0,
  "percent-memory-cache": 15.62,
  "avg-util-cpu0-60sec": 45.5,
  "avg-util-cpu1-60sec": 32.1,
  "avg-util-cpu2-60sec": 67.8,
  "avg-util-cpu3-60sec": 21.4,
  "timestamp": "2025-11-30T11:20:00",
  "num_cpus_monitored": 4
}

📈 Análise:
   ⏰ Timestamp: 2025-11-30T11:20:00
   💻 CPUs: 4
   🌐 Tráfego Saída: 20.00%
   💾 Memória Cache: 15.62%
   📊 Médias de CPU:
      CPU 0: 45.50%
      CPU 1: 32.10%
      CPU 2: 67.80%
      CPU 3: 21.40%

================================================================================
✅ Verificação concluída!
================================================================================
```

---

## 🆘 Problemas Comuns

### ❌ Pod não está rodando
```bash
kubectl get pods
kubectl describe pod serverless-redis-796b57c8f9-tgs5v
```

### ❌ Erros nos logs
```bash
kubectl logs serverless-redis-796b57c8f9-tgs5v
```
Procure por:
- `ImportError` - falta de módulos
- `KeyError` - problema no código
- `ConnectionError` - problema com Redis

### ❌ Chave de saída não existe
Verifique ConfigMap:
```bash
kubectl get configmap outputkey -o yaml
```
Deve mostrar: `REDIS_OUTPUT_KEY: "2025720437-proj3-output"`

### ❌ Redis não conecta
```bash
# Testar conectividade
telnet 192.168.121.48 6379

# Ou com Python
python3 -c "import redis; r = redis.Redis(host='192.168.121.48', port=6379); print(r.ping())"
```

---

## 🎯 Comandos Úteis para Copy-Paste

```bash
# Ver status geral
kubectl get pods,configmaps,deployments

# Ver logs continuamente
kubectl logs -f serverless-redis-796b57c8f9-tgs5v

# Verificar Redis
python3 ~/TP3_Cloud_Computing_UFMG/scripts/check_redis.py

# Reiniciar pod se necessário
kubectl delete pod serverless-redis-796b57c8f9-tgs5v

# Ver ConfigMaps
kubectl get configmap pyfile -o yaml
kubectl get configmap outputkey -o yaml

# Descrever deployment
kubectl describe deployment serverless-redis
```

---

## ✅ Tudo Funcionando?

Se você ver:
- ✅ Pod em "Running"
- ✅ Logs sem erros
- ✅ Script Python mostra JSON com métricas
- ✅ Timestamp atualiza a cada ~5 segundos

**Parabéns! Task 1 está funcionando perfeitamente! 🎉**

Próximo passo: **Task 2 - Dashboard**

---

## 📱 Monitoramento Contínuo

Deixe rodando em um terminal separado:

```bash
# Terminal 1: Logs
kubectl logs -f serverless-redis-796b57c8f9-tgs5v

# Terminal 2: Verificação Redis
watch -n 5 python3 ~/TP3_Cloud_Computing_UFMG/scripts/check_redis.py
```

---

**Dica:** Use o script Python - é mais fácil que redis-cli e mostra mais informações! 🐍

