# ⚠️ URGENTE: REAPLICAR DEPLOYMENT COM IP CORRETO

## 🎯 Situação

Seu pod está rodando com o **IP ERRADO** do Redis:
- ❌ IP Antigo: `192.168.121.48`
- ✅ IP Correto: `192.168.121.171`

## 🔧 Comandos para Corrigir AGORA

Execute estes comandos na VM:

```bash
# 1. Deletar deployment atual
kubectl delete deployment serverless-redis

# 2. Reaplicar com IP correto
cd ~/TP3_Cloud_Computing_UFMG/task1
kubectl apply -f serverless-deployment-course.yaml

# 3. Verificar novo pod
kubectl get pods

# 4. Ver logs do novo pod
kubectl logs -f <nome-do-novo-pod>

# 5. Testar Redis
python3 ~/TP3_Cloud_Computing_UFMG/scripts/check_redis.py
```

## 📋 Comando Completo (Copy-Paste)

```bash
kubectl delete deployment serverless-redis && \
cd ~/TP3_Cloud_Computing_UFMG/task1 && \
kubectl apply -f serverless-deployment-course.yaml && \
sleep 5 && \
kubectl get pods && \
echo "" && \
echo "✅ Deployment reaplicado! Aguarde o pod iniciar..." && \
echo "Execute: kubectl logs -f <nome-do-pod>"
```

## ✅ O que foi corrigido

Todos os arquivos do projeto foram atualizados para usar `192.168.121.171`:

- ✅ `task1/serverless-deployment-course.yaml`
- ✅ `task2/dashboard.py`
- ✅ `task2/dashboard-deployment.yaml`
- ✅ `task3/deployment.yaml`
- ✅ `task3/runtime.py`
- ✅ `scripts/check_redis.py`

## 📊 Verificar Funcionamento

Depois de reaplicar:

```bash
# Ver logs
kubectl get pods
kubectl logs -f serverless-redis-<novo-id>

# Testar com script Python
python3 ~/TP3_Cloud_Computing_UFMG/scripts/check_redis.py
```

## 🎯 Resultado Esperado

Você deve ver nos logs:
```
✅ Conectado ao Redis com sucesso!
📊 Processando métricas...
💾 Salvando em 2025720437-proj3-output
```

E o script Python deve mostrar suas métricas processadas.

---

**FAÇA ISSO AGORA antes de continuar com o projeto!** ⚠️

