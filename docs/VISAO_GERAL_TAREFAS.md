# 📊 Visão Geral das Tarefas - TP3

Este documento explica o fluxo completo do projeto e como as 3 tasks se conectam.

---

## 🔄 Fluxo Completo do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sistema de Monitoramento                      │
└─────────────────────────────────────────────────────────────────┘

  ┌─────────────┐         ┌──────────────┐         ┌─────────────┐
  │   COLETA    │         │ PROCESSAMENTO│         │ VISUALIZAÇÃO│
  │  (fornecido)│   →→→   │   (Task 1)   │   →→→   │   (Task 2)  │
  └─────────────┘         └──────────────┘         └─────────────┘
        ↓                         ↓                        ↓
   metrics (Redis)      handler_module.py       Dashboard Streamlit
        ↓                         ↓                        ↓
  CPU, Memória,         Calcula métricas:         Gráficos interativos:
  Rede (a cada 5s)      • % rede saída            • Gauges de CPU
                        • % memória cache          • Barras de %
                        • Média móvel CPU          • Histórico

   Chave: metrics       Chave: 2025720437-proj3-output    Lê: 2025720437-proj3-output


┌─────────────────────────────────────────────────────────────────┐
│                    Task 3: Runtime Customizado                   │
│  Substitui o runtime padrão com funcionalidades adicionais       │
└─────────────────────────────────────────────────────────────────┘

       Runtime Customizado (runtime.py)
                    ↓
        ┌───────────────────────┐
        │  Funcionalidades:     │
        │  • Chave configurável │
        │  • Período ajustável  │
        │  • Suporte a ZIP      │
        │  • Handler flexível   │
        └───────────────────────┘
```

---

## 📝 Task 1: Função Serverless

### O que faz?
Processa métricas de sistema e calcula indicadores agregados.

### Input (do Redis - chave `metrics`):
```json
{
  "timestamp": "2025-11-30T10:30:00",
  "cpu_percent-0": 45.5,
  "cpu_percent-1": 32.1,
  "net_io_counters_eth0-bytes_sent1": 1024000,
  "net_io_counters_eth0-bytes_recv1": 4096000,
  "virtual_memory-total": 16000000000,
  "virtual_memory-cached": 2000000000,
  "virtual_memory-buffers": 500000000
}
```

### Processamento:
1. **Tráfego de Rede:** `(bytes_sent / (bytes_sent + bytes_recv)) * 100`
2. **Memória Cache:** `((cached + buffers) / total) * 100`
3. **Média Móvel CPU:** Média dos últimos 12 valores (60s) de cada CPU

### Output (no Redis - chave `2025720437-proj3-output`):
```json
{
  "percent-network-egress": 20.0,
  "percent-memory-cache": 15.62,
  "avg-util-cpu0-60sec": 45.5,
  "avg-util-cpu1-60sec": 32.1,
  "timestamp": "2025-11-30T10:30:00",
  "num_cpus_monitored": 2
}
```

### Implementação:
- **Arquivo:** `task1/handler_module.py`
- **Função:** `handler(input, context)`
- **Estado:** Usa `context.env` para manter histórico de CPU

### Deploy:
```bash
kubectl apply -f task1/configmap-pyfile.yaml
kubectl apply -f task1/configmap-outputkey.yaml
kubectl apply -f task1/serverless-deployment-course.yaml
```

---

## 📊 Task 2: Dashboard de Monitoramento

### O que faz?
Visualiza as métricas processadas pela Task 1 em tempo real.

### Input:
Lê do Redis (chave `2025720437-proj3-output`) o resultado da Task 1.

### Visualizações:
1. **Métricas Gerais:**
   - Barra horizontal: % tráfego de saída
   - Barra horizontal: % memória em cache

2. **CPUs:**
   - Gauges individuais para cada CPU
   - Código de cores: verde → amarelo → vermelho

3. **Dados Brutos:**
   - Tabelas com métricas originais
   - JSON completo expansível

### Tecnologias:
- **Framework:** Streamlit
- **Gráficos:** Plotly
- **Redis:** redis-py
- **Auto-refresh:** A cada 5 segundos

### Deploy:
```bash
# Build
docker build -t seu-usuario/tp3-dashboard:v1 task2/
docker push seu-usuario/tp3-dashboard:v1

# Deploy
kubectl apply -f task2/dashboard-deployment.yaml
kubectl apply -f task2/dashboard-service.yaml

# Acesso
ssh -L 8501:localhost:SUA_PORTA usuario@vm
# http://localhost:8501
```

---

## ⚙️ Task 3: Runtime Serverless Customizado

### O que faz?
Substitui o runtime fornecido (`lucasmsp/serverless:redis`) com versão customizada.

### Funcionalidades Originais (compatíveis):
- ✅ Lê dados do Redis periodicamente
- ✅ Carrega módulo Python do usuário
- ✅ Chama `handler(input, context)`
- ✅ Persiste `context.env`
- ✅ Salva resultado no Redis

### Funcionalidades NOVAS:
- ⭐ **Chave Redis Configurável:** Monitorar chaves diferentes
- ⭐ **Período Ajustável:** Alterar intervalo de polling
- ⭐ **Suporte a ZIP:** Funções com múltiplos arquivos
- ⭐ **Handler Configurável:** Especificar função de entrada

### Arquitetura:

```python
runtime.py
├── Conexão Redis
├── Carregamento de Módulo
│   ├── Modo 1: pyfile (ConfigMap)
│   └── Modo 2: ZIP (download + extract)
├── Classe Context
│   ├── host, port, input_key, output_key
│   └── env (estado persistente)
└── Loop Principal
    ├── Ler dados (REDIS_INPUT_KEY)
    ├── Verificar mudanças
    ├── Chamar handler
    ├── Persistir context.env
    └── Salvar resultado (REDIS_OUTPUT_KEY)
```

### Configuração (via ConfigMap):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: runtime-config
data:
  REDIS_INPUT_KEY: "metrics"           # Chave de entrada
  MONITORING_PERIOD: "5"               # Segundos
  HANDLER_FUNCTION: "handler_module.handler"  # Função
  ZIP_URL: "https://exemplo.com/fn.zip"       # Opcional
```

### Deploy:
```bash
# Build
docker build -t seu-usuario/tp3-runtime:v1 task3/
docker push seu-usuario/tp3-runtime:v1

# Deploy
kubectl apply -f task1/configmap-pyfile.yaml
kubectl apply -f task1/configmap-outputkey.yaml
kubectl apply -f task3/configmap-runtime.yaml
kubectl apply -f task3/deployment.yaml
```

---

## 🔗 Como as Tasks se Conectam

### Cenário 1: Usando Runtime Padrão (Task 1 + Task 2)

```
┌──────────────┐
│  psutil      │ Coleta métricas do sistema
│  (fornecido) │
└──────┬───────┘
       ↓
┌──────────────────────────────────────┐
│  Redis: metrics                      │
│  {cpu, memory, network data...}      │
└──────┬───────────────────────────────┘
       ↓
┌────────────────────────────────────────┐
│  Runtime Padrão                        │
│  (lucasmsp/serverless:redis)           │
│  - Lê "metrics"                        │
│  - Chama handler_module.handler()      │
│  - Salva em "2025720437-proj3-output"  │
└──────┬─────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  Redis: 2025720437-proj3-output              │
│  {percent-egress, percent-cache, avg-cpu...} │
└──────┬───────────────────────────────────────┘
       ↓
┌──────────────────────────┐
│  Dashboard (Streamlit)   │
│  - Lê resultado          │
│  - Renderiza gráficos    │
│  - Auto-refresh          │
└──────────────────────────┘
```

### Cenário 2: Usando Runtime Customizado (Task 1 + Task 2 + Task 3)

```
┌──────────────┐
│  psutil      │
└──────┬───────┘
       ↓
┌──────────────────────────────────────┐
│  Redis: metrics (ou outra chave!)    │
└──────┬───────────────────────────────┘
       ↓
┌─────────────────────────────────────────────┐
│  Runtime Customizado                        │
│  (seu-usuario/tp3-runtime:v1)               │
│  + Chave configurável                       │
│  + Período ajustável                        │
│  + Suporte ZIP                              │
│  + Handler flexível                         │
└──────┬──────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│  Redis: 2025720437-proj3-output              │
└──────┬───────────────────────────────────────┘
       ↓
┌──────────────────────────┐
│  Dashboard               │
└──────────────────────────┘
```

---

## 📦 Estrutura de Dados

### Dados de Entrada (psutil → Redis):
```python
{
  "timestamp": str,                    # ISO 8601
  "cpu_percent-X": float,              # Por CPU (X = 0, 1, 2...)
  "cpu_freq_current": float,           # MHz
  "virtual_memory-total": int,         # Bytes
  "virtual_memory-cached": int,        # Bytes
  "virtual_memory-buffers": int,       # Bytes
  "net_io_counters_eth0-bytes_sent1": int,
  "net_io_counters_eth0-bytes_recv1": int
}
```

### Dados Processados (handler → Redis):
```python
{
  "percent-network-egress": float,     # 0-100
  "percent-memory-cache": float,       # 0-100
  "avg-util-cpuN-60sec": float,        # Por CPU, 0-100
  "timestamp": str,                    # ISO 8601
  "num_cpus_monitored": int            # Quantidade
}
```

### Context Object:
```python
class Context:
    host: str                  # Redis host
    port: int                  # Redis port
    input_key: str             # Chave de entrada
    output_key: str            # Chave de saída
    function_getmtime: float   # Timestamp do módulo
    last_execution: str        # Última execução
    env: dict                  # Estado persistente ⭐
```

---

## 🧪 Testando o Fluxo Completo

### 1. Verificar Coleta (fornecido):
```bash
redis-cli -h 192.168.121.48 -p 6379 get metrics
# Deve retornar JSON com métricas
```

### 2. Verificar Task 1:
```bash
kubectl logs -f <serverless-pod>
redis-cli -h 192.168.121.48 -p 6379 get 2025720437-proj3-output
# Deve retornar JSON processado
```

### 3. Verificar Task 2:
```bash
kubectl logs -f <dashboard-pod>
# Acessar: http://localhost:8501
# Deve mostrar gráficos
```

### 4. Verificar Task 3:
```bash
kubectl logs -f <runtime-custom-pod>
redis-cli -h 192.168.121.48 -p 6379 get 2025720437-proj3-output
# Deve funcionar igual Task 1, mas com logs customizados
```

---

## 📊 Comparação: Runtime Padrão vs Customizado

| Feature | Runtime Padrão | Runtime Customizado |
|---------|---------------|---------------------|
| Lê dados Redis | ✅ `metrics` fixo | ✅ **Configurável** |
| Período polling | ✅ 5s fixo | ✅ **Configurável** |
| Módulo Python | ✅ pyfile | ✅ pyfile **+ ZIP** |
| Handler | ✅ `handler` fixo | ✅ **Configurável** |
| Context.env | ✅ Persiste | ✅ Persiste |
| Logs | ❌ Básicos | ✅ **Detalhados** |
| Healthcheck | ❌ Não | ✅ **Sim** |
| Pacotes pré-instalados | ❌ Básicos | ✅ **numpy, pandas, etc** |

---

## 🎯 Objetivos de Aprendizado

### Task 1:
- ✅ Implementar função stateless
- ✅ Usar contexto para estado persistente
- ✅ Processar streams de dados
- ✅ Trabalhar com Redis

### Task 2:
- ✅ Criar container Docker
- ✅ Deploy em Kubernetes
- ✅ Visualização de dados
- ✅ Frameworks de dashboards

### Task 3:
- ✅ Entender arquitetura serverless
- ✅ Implementar runtime do zero
- ✅ Adicionar funcionalidades
- ✅ Manter compatibilidade

---

## 📚 Recursos Adicionais

- **psutil:** https://psutil.readthedocs.io/
- **Redis:** https://redis.io/docs/
- **Streamlit:** https://docs.streamlit.io/
- **Plotly:** https://plotly.com/python/
- **Kubernetes ConfigMaps:** https://kubernetes.io/docs/concepts/configuration/configmap/

---

## ✅ Checklist Final

- [ ] Task 1 deployada e funcionando
- [ ] Dados visíveis no Redis
- [ ] Task 2 deployada e acessível
- [ ] Dashboard mostrando métricas
- [ ] Task 3 implementada
- [ ] Runtime customizado testado
- [ ] Compatibilidade verificada
- [ ] Documentação PDF criada para cada task

**Boa sorte no seu projeto! 🚀**

