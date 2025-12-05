# TP3: Serverless Computing e Dashboard de Monitoramento

## Relatório Técnico

**Aluno:** Tássio Almeida  
**ID:** 2025720437  
**Disciplina:** Cloud Computing - Mestrado UFMG  
**Data:** Dezembro 2025

---

# PARTE I: Task 1 - Função Serverless

## 1. Introdução

A Task 1 implementa uma função serverless para processar métricas de recursos do sistema coletadas periodicamente pela VM. A função calcula indicadores agregados de CPU, memória e rede, que são posteriormente visualizados no dashboard da Task 2.

---

## 2. Métricas Implementadas

### 2.1 Porcentagem de Tráfego de Rede (Egress)

**Descrição:** Porcentagem de bytes enviados em relação ao total de tráfego

**Fórmula:**
```
percent_egress = (bytes_sent / (bytes_sent + bytes_recv)) × 100
```

**Implementação:**
```python
bytes_sent = input.get('net_io_counters_eth0-bytes_sent1', 0)
bytes_recv = input.get('net_io_counters_eth0-bytes_recv1', 0)
total_bytes = bytes_sent + bytes_recv

if total_bytes > 0:
    percent_egress = (bytes_sent / total_bytes) * 100.0
else:
    percent_egress = 0.0

results['percent-network-egress'] = round(percent_egress, 2)
```

### 2.2 Porcentagem de Memória em Cache

**Descrição:** Porcentagem da memória total usada para cache (buffers + cached)

**Fórmula:**
```
percent_cache = ((cached + buffers) / total) × 100
```

**Implementação:**
```python
memory_total = input.get('virtual_memory-total', 1)
memory_cached = input.get('virtual_memory-cached', 0)
memory_buffers = input.get('virtual_memory-buffers', 0)

memory_cache_total = memory_cached + memory_buffers
percent_memory_cache = (memory_cache_total / memory_total) * 100.0

results['percent-memory-cache'] = round(percent_memory_cache, 2)
```

### 2.3 Média Móvel de Utilização de CPU

**Descrição:** Média de utilização de cada CPU nos últimos 60 segundos

**Janela:** 12 valores (60 segundos ÷ 5 segundos/medição = 12 medições)

**Implementação:** Ver seção 3 deste relatório

---

## 3. Abordagem para Manutenção de Estado (Média Móvel)

### 3.1 Desafio

A função serverless é **stateless** por natureza, mas o cálculo de média móvel requer:
- Histórico dos últimos 12 valores de cada CPU
- Persistência entre execuções sucessivas
- Detecção dinâmica do número de CPUs do sistema

### 3.2 Solução: Uso de `context.env`

O objeto `context` fornecido pelo runtime serverless possui um campo especial chamado `env` que **persiste entre execuções**:

```python
context.env = {}  # Dicionário que mantém estado entre chamadas
```

**Por que `context.env`?**

1. **Persiste automaticamente:** O runtime gerencia a persistência
2. **Sem dependências externas:** Não precisa de Redis ou banco de dados
3. **Acesso rápido:** Em memória, sem latência de rede
4. **Interface padrão:** Compatível com AWS Lambda

### 3.3 Estrutura de Dados

```python
context.env = {
    'cpu_history': {
        '0': [45.5, 43.2, 47.1, 44.8, 46.2, ...],  # últimos 12 valores
        '1': [32.1, 31.5, 33.0, 30.8, 32.5, ...],
        '2': [67.8, 65.3, 68.9, 66.1, 69.2, ...],
        ...
        '7': [21.4, 22.1, 20.8, 21.9, 22.3, ...]
    }
}
```

### 3.4 Implementação Completa

#### Passo 1: Inicialização do Estado

```python
# Inicializar estado persistente se não existir
if not hasattr(context, 'env'):
    context.env = {}

if 'cpu_history' not in context.env:
    context.env['cpu_history'] = {}
```

#### Passo 2: Identificação Dinâmica de CPUs

```python
# Identificar todas as CPUs presentes no input
cpu_keys = [key for key in input.keys() if key.startswith('cpu_percent-')]

# Exemplo: ['cpu_percent-0', 'cpu_percent-1', ..., 'cpu_percent-7']
```

#### Passo 3: Processamento e Atualização do Histórico

```python
WINDOW_SIZE = 12  # 60 segundos / 5 segundos por medição

for cpu_key in cpu_keys:
    cpu_value = input.get(cpu_key, 0.0)
    
    # Extrair ID da CPU (ex: 'cpu_percent-0' -> '0')
    cpu_id = cpu_key.replace('cpu_percent-', '')
    
    # Inicializar histórico para esta CPU se não existir
    if cpu_id not in context.env['cpu_history']:
        context.env['cpu_history'][cpu_id] = []
    
    # Adicionar valor atual ao histórico
    context.env['cpu_history'][cpu_id].append(cpu_value)
    
    # Manter apenas os últimos WINDOW_SIZE valores (janela deslizante)
    if len(context.env['cpu_history'][cpu_id]) > WINDOW_SIZE:
        context.env['cpu_history'][cpu_id] = \
            context.env['cpu_history'][cpu_id][-WINDOW_SIZE:]
```

#### Passo 4: Cálculo da Média Móvel

```python
    # Obter histórico atualizado
    cpu_history = context.env['cpu_history'][cpu_id]
    
    # Calcular média aritmética simples
    avg_cpu_util = sum(cpu_history) / len(cpu_history)
    
    # Adicionar ao resultado
    results[f'avg-util-cpu{cpu_id}-60sec'] = round(avg_cpu_util, 2)
```

### 3.5 Exemplo de Evolução do Estado

**Execução 1:**
```python
Input: cpu0 = 45.5
History: [45.5]
Média: 45.5
```

**Execução 5:**
```python
Input: cpu0 = 44.2
History: [45.5, 47.0, 46.3, 44.8, 44.2]
Média: 45.56
```

**Execução 12:**
```python
Input: cpu0 = 46.8
History: [45.5, 47.0, 46.3, ..., 46.8]  (12 valores)
Média: 46.12
```

**Execução 13 (janela completa):**
```python
Input: cpu0 = 48.1
History: [47.0, 46.3, ..., 46.8, 48.1]  (12 valores - remove o mais antigo)
Média: 46.85
```

### 3.6 Vantagens da Abordagem

| Aspecto | Vantagem |
|---------|----------|
| **Simplicidade** | Sem dependências externas (DB, Redis adicional) |
| **Performance** | Acesso em memória O(1), sem latência de rede |
| **Compatibilidade** | Interface padrão AWS Lambda |
| **Escalabilidade** | Detecta CPUs dinamicamente |
| **Eficiência** | ~2 KB de memória para 8 CPUs |

### 3.7 Limitações e Adequação

**Limitações:**
- Estado perdido se pod for destruído
- Não compartilhado entre múltiplas réplicas
- Limitado a dados pequenos (< 1 MB recomendado)

**Por que é adequado:**
- ✅ Janela de 60s é pequena (~96 floats total)
- ✅ Pod único suficiente para monitoramento
- ✅ Perda de estado recuperável em 60s
- ✅ Não requer alta disponibilidade

**Alternativa (se necessário):**
```python
# Para estado durável, usar Redis:
redis_client.set(f'cpu_history_{cpu_id}', json.dumps(history))
history = json.loads(redis_client.get(f'cpu_history_{cpu_id}'))
```

---

## 4. ConfigMaps Kubernetes

### 4.1 ConfigMap: pyfile

Contém o código-fonte completo do módulo Python:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pyfile
data:
  pyfile: |
    [código completo de handler_module.py]
```

### 4.2 ConfigMap: outputkey

Define a chave Redis para armazenar resultados:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: outputkey
data:
  REDIS_OUTPUT_KEY: "2025720437-proj3-output"
```

---

## 5. Deployment e Resultados

### 5.1 Deploy

```bash
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
kubectl apply -f serverless-deployment-course.yaml
```

### 5.2 Verificação

```bash
kubectl get pods
# OUTPUT: serverless-redis-6c4d756456-7pqrg   1/1   Running

kubectl logs -f serverless-redis-6c4d756456-7pqrg
# OUTPUT: Environment loaded. Starting execution...
```

### 5.3 Resultado no Redis

**Chave:** `2025720437-proj3-output`

**Dados:**
```json
{
  "percent-network-egress": 0.0,
  "percent-memory-cache": 63.68,
  "avg-util-cpu0-60sec": 100.0,
  "avg-util-cpu1-60sec": 18.69,
  "avg-util-cpu2-60sec": 13.48,
  "avg-util-cpu3-60sec": 13.23,
  "avg-util-cpu4-60sec": 13.99,
  "avg-util-cpu5-60sec": 100.0,
  "avg-util-cpu6-60sec": 13.04,
  "avg-util-cpu7-60sec": 12.24,
  "timestamp": "2025-11-30 15:03:43.211280",
  "num_cpus_monitored": 8
}
```

**Análise:**
- 8 CPUs detectadas automaticamente
- CPUs 0 e 5 em alta utilização (100%)
- Demais CPUs com utilização normal
- Média móvel calculada corretamente para todas

---

# PARTE II: Task 2 - Dashboard de Monitoramento

## 6. Framework e Tecnologias

### 6.1 Streamlit

**Framework Principal:** Streamlit  
**Versão:** Latest (Python 3.9)

**Justificativa:**
1. **Desenvolvimento Rápido:** Interface declarativa, sem HTML/CSS
2. **Python Nativo:** Integração direta com redis-py
3. **Componentes Prontos:** Gauges, gráficos, tabelas
4. **Auto-refresh:** Atualização automática integrada

### 6.2 Bibliotecas Complementares

- **Plotly:** Gráficos interativos (gauges e barras)
- **Pandas:** Manipulação de dados tabulares
- **redis-py:** Conexão com Redis

---

## 7. Screenshots do Dashboard

### 7.1 Tela Principal - Visão Geral

**[INSERIR PRINT: Dashboard completo com header, métricas e gauges]**

![Dashboard - Visão Geral](prints/dashboard-overview.png)

**Elementos Visíveis:**
- 📊 **Header:** "TP3 - Dashboard de Monitoramento de Recursos"
- 📅 **Timestamp:** 2025-12-04 22:19:47 (atualizando a cada 5s)
- 💻 **CPUs Monitoradas:** 8
- 💾 **Memória Usada:** 22.9%
- ⚙️ **Configurações na Sidebar:**
  - Redis Server: 192.168.121.171:6379
  - Key: 2025720437-proj3-output
  - Auto-refresh: Ativado

---

### 7.2 Métricas Gerais

**[INSERIR PRINT: Seção de Métricas Gerais]**

![Métricas Gerais](prints/metricas-gerais.png)

**Visualizações:**

1. **🌐 Tráfego de Saída de Rede**
   - Tipo: Barra horizontal azul
   - Valor: 0%
   - Análise: Tráfego predominantemente de entrada

2. **💾 Memória em Cache**
   - Tipo: Barra horizontal verde
   - Valor: 70.52%
   - Análise: Cache: 31.43 GB, Buffers: 1.74 GB

---

### 7.3 Utilização de CPU (Média Móvel 60s)

**[INSERIR PRINT: Grid com 8 gauges de CPU]**

![Gauges de CPU](prints/cpu-gauges.png)

**Descrição dos Gauges:**
- **Escala:** 0-100%
- **Código de Cores:**
  - 🟢 Verde (0-50%): Utilização normal
  - 🟡 Amarelo (50-75%): Utilização média
  - 🔴 Vermelho (75-100%): Utilização alta

**Valores Observados:**
- CPU 0: 15.4%
- CPU 1: 11.8%
- CPU 2: 11.1%
- CPU 3: 12.3%
- CPU 4: 100% (alta carga constante)
- CPU 5: 12.3%
- CPU 6: 11.35%
- CPU 7: 64.7%

**Análise:**
- CPUs 4 e 7 com cargas elevadas
- Demais CPUs com utilização baixa/média
- Distribuição desbalanceada (provável processo pinned)

---

### 7.4 Dados Brutos (Métricas de Entrada)

**[INSERIR PRINT: Seção expandida "Ver Métricas Brutas"]**

![Dados Brutos](prints/dados-brutos.png)

**Conteúdo:**

**💻 CPU:**
- Tabela com utilização instantânea de cada CPU
- Valores em porcentagem

**💾 Memória:**
- Total: 47.04 GB
- Usada: 10.54 GB
- Cache: 31.43 GB
- Buffers: 1.74 GB

**🌐 Rede:**
- Bytes Enviados: 0.00 MB
- Bytes Recebidos: 0.00 MB

---

### 7.5 JSON Completo (Métricas Processadas)

**[INSERIR PRINT: Seção expandida "Ver JSON Completo"]**

![JSON Completo](prints/json-completo.png)

**Dados Completos:**
```json
{
  "percent-network-egress": 0,
  "percent-memory-cache": 70.52,
  "avg-util-cpu0-60sec": 16.37,
  "avg-util-cpu1-60sec": 15.54,
  "avg-util-cpu2-60sec": 13.07,
  "avg-util-cpu3-60sec": 12.6,
  "avg-util-cpu4-60sec": 100,
  "avg-util-cpu5-60sec": 14.52,
  "avg-util-cpu6-60sec": 11.35,
  "avg-util-cpu7-60sec": 12.53,
  "timestamp": "2025-12-04 22:23:13.242303",
  "num_cpus_monitored": 8
}
```

---

## 8. Implementação do Dashboard

### 8.1 Conexão com Redis

```python
import redis
import json
import os

# Configuração via variáveis de ambiente
REDIS_HOST = os.getenv('REDIS_HOST', '192.168.121.171')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', '2025720437-proj3-output')
REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', 5))

# Conexão com cache
@st.cache_resource
def get_redis_connection():
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=5
    )
    r.ping()
    return r

# Busca de métricas
def fetch_metrics(redis_conn):
    data = redis_conn.get(REDIS_OUTPUT_KEY)
    if data:
        return json.loads(data)
    return None
```

**Nota Importante:** O IP `192.168.121.171` é necessário para acesso de dentro de containers, permitindo que o tráfego passe pelo NAT do Docker.

### 8.2 Visualizações Plotly

#### Gauge de CPU

```python
def create_cpu_gauge(cpu_id, value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"CPU {cpu_id}"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    return fig
```

#### Gráfico de Barras

```python
def create_percentage_chart(title, value, color):
    fig = go.Figure(go.Bar(
        x=[value],
        y=[title],
        orientation='h',
        marker=dict(color=color),
        text=[f"{value:.2f}%"],
        textposition='inside'
    ))
    fig.update_layout(xaxis=dict(range=[0, 100]))
    return fig
```

### 8.3 Auto-refresh

```python
placeholder = st.empty()

while True:
    with placeholder.container():
        metrics = fetch_metrics(redis_conn)
        
        # Renderizar visualizações
        st.metric("Timestamp", metrics.get('timestamp'))
        # ... outros componentes
    
    if auto_refresh:
        time.sleep(REFRESH_INTERVAL)
    else:
        break
```

---

## 9. Containerização

### 9.1 Dockerfile

```dockerfile
FROM python:3.9-slim

# Instalar curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY dashboard.py .

EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Executar (com file watcher desabilitado)
CMD ["streamlit", "run", "dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.fileWatcherType=none"]
```

**Observação Crítica:** O parâmetro `--server.fileWatcherType=none` é **essencial** para evitar o erro `inotify instance limit reached` em ambientes Kubernetes.

### 9.2 Dependências

```
streamlit>=1.28.0
redis>=4.0.0
pandas>=1.5.0
plotly>=5.17.0
```

### 9.3 Build e Push

```bash
# Build na VM (arquitetura AMD64)
docker build -t tassiolucas/tp3-dashboard:v1 .

# Push para Docker Hub
docker login -u tassiolucas
docker push tassiolucas/tp3-dashboard:v1
```

**Imagem Final:**
- Repositório: `docker.io/tassiolucas/tp3-dashboard:v1`
- Digest: `sha256:2dcde9fdd89a67509b56dd85d93613922fa829a2bac41e26430931b32a6bf8a4`
- Tamanho: ~450 MB

---

## 10. Deploy no Kubernetes

### 10.1 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tp3-dashboard
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: dashboard
        image: tassiolucas/tp3-dashboard:v1
        ports:
        - containerPort: 8501
        env:
        - name: REDIS_HOST
          value: "192.168.121.171"
        - name: REDIS_OUTPUT_KEY
          value: "2025720437-proj3-output"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

### 10.2 Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tp3-dashboard
spec:
  type: NodePort
  ports:
  - port: 8501
    targetPort: 8501
    nodePort: 30600
  selector:
    app: tp3-dashboard
```

**Cálculo da Porta:** Porta DevOps (30500) + 100 = **30600**

### 10.3 Status Final

```bash
kubectl get pods
```
```
NAME                             READY   STATUS    RESTARTS   AGE
tp3-dashboard-6f4fd94d45-mtgz5   1/1     Running   0          5m
```

```bash
kubectl get svc tp3-dashboard
```
```
NAME            TYPE       CLUSTER-IP    EXTERNAL-IP   PORT(S)          AGE
tp3-dashboard   NodePort   10.43.54.82   <none>        8501:30600/TCP   4d6h
```

---

## 11. Desafios Encontrados e Soluções

### 11.1 Incompatibilidade de Arquitetura

**Problema:** Imagem buildada em Mac M1 (ARM64) não funcionava na VM (AMD64)

**Erro:**
```
exec /usr/local/bin/streamlit: exec format error
```

**Tentativas:**
1. `docker build --platform linux/amd64` (não funcionou no Colima)
2. `docker buildx` (não disponível no Colima)

**Solução Final:** Build realizado diretamente na VM (AMD64 nativa)

### 11.2 Limite de File Watchers

**Problema:** Streamlit atingindo limite de inotify

**Erro:**
```
OSError: [Errno 24] inotify instance limit reached
```

**Solução:** Desabilitar file watcher via `--server.fileWatcherType=none`

### 11.3 IP do Redis

**Problema Inicial:** Uso de IP incorreto para acesso de containers

**IP Errado:** `192.168.121.48`  
**IP Correto:** `192.168.121.171`

**Explicação:** Para acesso de dentro de containers, é necessário usar o IP da interface pública da VM (eth0), permitindo que o tráfego passe pelo NAT do Docker.

### 11.4 Credenciais Docker Hub

**Problema:** Erro `docker-credential-desktop not found`

**Solução:** 
```bash
echo '{"auths":{}}' > ~/.docker/config.json
docker login -u tassiolucas
```

---

## 12. Análise dos Dados Monitorados

### 12.1 Utilização de CPU

**Observações:**
- **CPU 4:** Constantemente em 100%
- **CPU 7:** Variando entre 60-100%
- **CPUs 0-3, 5-6:** Utilização baixa (10-20%)

**Interpretação:**
- Processos específicos consumindo cores dedicados
- Possível process pinning ou workloads específicos
- Distribuição desbalanceada de carga

### 12.2 Memória

**Cache:** 70.52% (~31.43 GB + 1.74 GB)

**Análise:**
- Comportamento normal para Linux
- Cache melhora performance de I/O
- Sistema otimizando acesso a disco

### 12.3 Rede

**Tráfego de Saída:** 0%

**Análise:**
- VM predominantemente recebendo dados
- Serviços internos (Kubernetes, dashboard)
- Pouco tráfego externo

---

## 13. Acesso ao Dashboard

### 13.1 Túnel SSH

```bash
ssh -i ~/.ssh/tassioUFMG \
  -L 8501:localhost:30600 \
  tassioalmeida@pugna.snes.2advanced.dev \
  -p 51927
```

### 13.2 Navegador

```
http://localhost:8501
```

### 13.3 Verificação

```bash
# Logs
kubectl logs tp3-dashboard-6f4fd94d45-mtgz5

# Output:
# You can now view your Streamlit app in your browser.
# URL: http://0.0.0.0:8501
```

---

## 14. Conclusões

### 14.1 Objetivos Alcançados

**Task 1:**
✅ Função serverless implementada e deployada  
✅ Três métricas calculadas corretamente  
✅ Média móvel com estado persistente via `context.env`  
✅ Detecção dinâmica de CPUs  
✅ Integração com Redis funcionando  

**Task 2:**
✅ Dashboard interativo implementado  
✅ Framework Streamlit escolhido e justificado  
✅ Leitura de dados do Redis  
✅ Visualizações com Plotly  
✅ Containerização e deploy no Kubernetes  
✅ Auto-refresh funcionando  
✅ Acessível via túnel SSH  

### 14.2 Competências Desenvolvidas

1. **Serverless Computing:**
   - Paradigma stateless vs stateful
   - Uso de contexto para estado temporário
   - Interface AWS Lambda

2. **Visualização de Dados:**
   - Streamlit para dashboards
   - Plotly para gráficos interativos
   - UX para monitoramento em tempo real

3. **DevOps e Cloud:**
   - Containerização com Docker
   - Deployment no Kubernetes
   - Troubleshooting de arquitetura
   - ConfigMaps e Services

4. **Análise de Performance:**
   - Interpretação de métricas de sistema
   - Identificação de bottlenecks
   - Monitoramento contínuo

### 14.3 Lições Aprendidas

1. **Arquitetura de Containers:**
   - Importância de build para arquitetura correta
   - Cross-compilation vs build nativo

2. **Redis em Containers:**
   - Uso de IP correto para NAT do Docker
   - Diferença entre acesso interno e externo

3. **Streamlit em Produção:**
   - Desabilitar file watchers para evitar limites do sistema
   - Healthchecks para robustez

4. **Estado em Serverless:**
   - `context.env` adequado para janelas pequenas
   - Trade-offs entre simplicidade e durabilidade

### 14.4 Melhorias Futuras

1. **Persistência de Histórico:**
   - Armazenar histórico em TimescaleDB ou InfluxDB
   - Gráficos de tendência temporal

2. **Alertas Proativos:**
   - Notificações via Slack/Email
   - Thresholds configuráveis

3. **Múltiplas VMs:**
   - Dashboard agregado
   - Comparação entre servidores

4. **Otimizações:**
   - Cache de queries Redis
   - Compressão de histórico

---

## Referências

1. AWS Lambda Documentation. Amazon Web Services. Disponível em: https://aws.amazon.com/lambda/
2. Kubernetes ConfigMaps. Kubernetes Documentation. Disponível em: https://kubernetes.io/docs/concepts/configuration/configmap/
3. Streamlit Documentation. Disponível em: https://docs.streamlit.io/
4. Plotly Python Documentation. Disponível em: https://plotly.com/python/
5. Redis-py Documentation. Disponível em: https://redis-py.readthedocs.io/
6. psutil Documentation. Python Package Index. Disponível em: https://psutil.readthedocs.io/

---

## Anexos

### A. Arquivos Entregues

**Task 1:**
- `handler_module.py` - Código da função serverless
- `configmap-pyfile.yaml` - ConfigMap com código Python
- `configmap-outputkey.yaml` - ConfigMap com chave de saída

**Task 2:**
- `dashboard.py` - Código do dashboard
- `Dockerfile` - Container do dashboard
- `requirements.txt` - Dependências Python
- `dashboard-deployment.yaml` - Deployment Kubernetes
- `dashboard-service.yaml` - Service Kubernetes

### B. Configurações do Sistema

**VM:**
- Host: pugna.snes.2advanced.dev
- Porta SSH: 51927
- Usuário: tassioalmeida

**Redis:**
- Host: 192.168.121.171
- Porta: 6379
- Chave Input: `metrics`
- Chave Output: `2025720437-proj3-output`

**Kubernetes:**
- Namespace: tassioalmeida
- Dashboard NodePort: 30600

### C. Repositório Docker Hub

- **Task 2:** `tassiolucas/tp3-dashboard:v1`

---

**Fim do Relatório**

