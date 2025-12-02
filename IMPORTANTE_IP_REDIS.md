# ⚠️ IMPORTANTE: IP CORRETO DO REDIS

## 🎯 Informação Crucial do Professor

Para conectar ao Redis **de dentro de um container** (pods Kubernetes), use:

```
IP: 192.168.121.171
Porta: 6379
```

## 📋 Explicação

Conforme orientação do professor:

> Para conectar ao Redis de dentro de um container, é preciso usar o IP que está na VM: **192.168.121.171**. Assim o tráfego de dentro do container vai passar pelo NAT do Docker e vai acessar o Redis executando na VM.

## 🔍 Dois Cenários

### 1️⃣ Acesso de DENTRO do Container/Pod (Kubernetes)
**Use:** `192.168.121.171:6379`

Este é o caso de:
- ✅ Função serverless (Task 1)
- ✅ Dashboard (Task 2)
- ✅ Runtime customizado (Task 3)

### 2️⃣ Acesso DIRETAMENTE da VM (SSH)
**Use:** `localhost` ou `127.0.0.1` ou `192.168.121.171`

Este é o caso de:
- Script Python rodando na VM
- redis-cli rodando na VM

## ✅ Arquivos Já Atualizados

Todos os arquivos do projeto foram atualizados com o IP correto:

- ✅ `task1/serverless-deployment-course.yaml` → `192.168.121.171`
- ✅ `task2/dashboard.py` → `192.168.121.171`
- ✅ `task2/dashboard-deployment.yaml` → `192.168.121.171`
- ✅ `task3/deployment.yaml` → `192.168.121.171`
- ✅ `task3/runtime.py` → `192.168.121.171`
- ✅ `scripts/check_redis.py` → `192.168.121.171`
- ✅ Scripts de build → `192.168.121.171`

## 🔄 Se Você Já Fez Deploy

Se você já aplicou os deployments com o IP antigo, precisa reaplicar:

```bash
# Task 1
cd ~/TP3_Cloud_Computing_UFMG/task1
kubectl delete deployment serverless-redis
kubectl apply -f serverless-deployment-course.yaml

# Verificar
kubectl get pods
kubectl logs -f <nome-do-pod>
```

## 🧪 Testar Conexão

### Da VM (SSH):
```bash
# Com Python
python3 ~/TP3_Cloud_Computing_UFMG/scripts/check_redis.py

# Ou com telnet
telnet 192.168.121.171 6379
```

### De Dentro de um Pod:
```bash
kubectl run redis-test --rm -it --restart=Never --image=redis:latest -- redis-cli -h 192.168.121.171 -p 6379 ping
```

Deve retornar: `PONG`

## 📊 Resumo

| Contexto | IP a Usar | Porta |
|----------|-----------|-------|
| **Pods Kubernetes** | `192.168.121.171` | `6379` |
| **Containers Docker** | `192.168.121.171` | `6379` |
| **Diretamente na VM** | `localhost` ou `192.168.121.171` | `6379` |

## ⚠️ IP Antigo (ERRADO para containers)

~~192.168.121.48~~ ❌ NÃO USE ESTE!

## ✅ IP Correto

**192.168.121.171** ✅ USE ESTE!

---

**Todos os arquivos do projeto já estão atualizados com o IP correto!** 🎉

