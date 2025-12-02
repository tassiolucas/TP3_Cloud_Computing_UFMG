# 📋 Plano de Execução - TP3 Cloud Computing

Este documento divide o projeto em partes gerenciáveis para facilitar a implementação e teste.

---

## 🎯 Visão Geral do Projeto

O projeto está dividido em 3 tarefas principais:

1. **Task 1**: Função Serverless (✅ Implementada)
2. **Task 2**: Dashboard de Monitoramento (✅ Implementada)
3. **Task 3**: Runtime Serverless Customizado (⏳ A fazer)

---

## 📦 TASK 1: Função Serverless

### Status: ✅ IMPLEMENTADA

### O que foi feito:
- ✅ `handler_module.py` - Função serverless que calcula:
  - Porcentagem de tráfego de rede de saída
  - Porcentagem de memória em cache
  - Média móvel de CPU (60 segundos)
- ✅ `configmap-pyfile.yaml` - ConfigMap com código Python
- ✅ `configmap-outputkey.yaml` - ConfigMap com chave Redis

### Próximos Passos:

#### 1.1 Configurar Credenciais
- [ ] Editar `task1/configmap-outputkey.yaml`
- [ ] Substituir `seu-id` pelo seu ID de estudante (ex: `ifs4-proj3-output`)

#### 1.2 Testar Localmente (Opcional)
```bash
cd task1
python handler_module.py
```
**Resultado esperado**: Saída JSON com as métricas calculadas

#### 1.3 Conectar na VM
```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

#### 1.4 Aplicar ConfigMaps no Kubernetes
```bash
kubectl apply -f task1/configmap-pyfile.yaml
kubectl apply -f task1/configmap-outputkey.yaml
```

#### 1.5 Fazer Deploy da Função Serverless
```bash
kubectl apply -f task1/serverless-deployment-course.yaml
```

#### 1.6 Verificar Funcionamento
```bash
# Ver pods
kubectl get pods

# Ver logs
kubectl logs -f <nome-do-pod>

# Testar Redis (na VM)
redis-cli -h 192.168.121.48 -p 6379 get seu-id-proj3-output
```

#### 1.7 Criar Documentação PDF
- [ ] Criar PDF explicando a abordagem de média móvel
- [ ] Descrever uso do `context.env` para persistir histórico
- [ ] Incluir explicação da janela de 12 valores (60s / 5s)

---

## 📊 TASK 2: Dashboard de Monitoramento

### Status: ✅ IMPLEMENTADA

### O que foi feito:
- ✅ `task2/dashboard.py` - Dashboard Streamlit com visualizações
- ✅ `task2/Dockerfile` - Container para o dashboard
- ✅ `task2/requirements.txt` - Dependências Python
- ✅ `task2/dashboard-deployment.yaml` - Deployment Kubernetes
- ✅ `task2/dashboard-service.yaml` - Service Kubernetes

### Próximos Passos:

#### 2.1 Configurar Variáveis
- [ ] Editar `task2/dashboard.py` linha 27
- [ ] Substituir `seu-id-proj3-output` pelo seu ID

#### 2.2 Testar Localmente (Opcional)
```bash
cd task2

# Instalar dependências
pip install -r requirements.txt

# Testar dashboard
streamlit run dashboard.py
```
**Acesso**: http://localhost:8501

#### 2.3 Calcular Porta do Dashboard
Sua porta = Porta do DevOps + 100

**Exemplo**: Se sua porta no DevOps era `30500`, use `30600`

#### 2.4 Editar Service
- [ ] Editar `task2/dashboard-service.yaml`
- [ ] Definir `nodePort: SUA_PORTA` (calculada acima)

#### 2.5 Build da Imagem Docker
```bash
cd task2

# Login no Docker Hub (se necessário)
docker login

# Build
docker build -t seu-usuario/tp3-dashboard:v1 .

# Testar localmente
docker run -p 8501:8501 seu-usuario/tp3-dashboard:v1
```
**Acesso**: http://localhost:8501

#### 2.6 Push da Imagem
```bash
docker push seu-usuario/tp3-dashboard:v1
```

#### 2.7 Editar Deployment
- [ ] Editar `task2/dashboard-deployment.yaml`
- [ ] Substituir `seu-usuario/tp3-dashboard:v1` pela sua imagem
- [ ] Atualizar `REDIS_OUTPUT_KEY` com seu ID

#### 2.8 Deploy no Kubernetes
```bash
# Aplicar deployment
kubectl apply -f task2/dashboard-deployment.yaml

# Aplicar service
kubectl apply -f task2/dashboard-service.yaml

# Verificar
kubectl get pods
kubectl get services
```

#### 2.9 Acessar Dashboard
```bash
# Na sua máquina local (criar túnel SSH)
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:SUA_PORTA tassioalmeida@pugna.snes.2advanced.dev -p 51927
```
**Acesso**: http://localhost:8501

#### 2.10 Criar Documentação PDF
- [ ] Tirar screenshots do dashboard funcionando
- [ ] Explicar cada métrica visualizada
- [ ] Descrever escolha do framework (Streamlit)
- [ ] Documentar configuração e deploy

---

## ⚙️ TASK 3: Runtime Serverless Customizado

### Status: ⏳ A IMPLEMENTAR

### Objetivo:
Criar um runtime customizado que substitua `lucasmsp/serverless:redis` com funcionalidades adicionais.

### Funcionalidades Requeridas:

#### 3.1 Funcionalidades Básicas (compatíveis com runtime original)
- [ ] Ler dados do Redis periodicamente
- [ ] Carregar módulo Python do usuário
- [ ] Chamar função `handler(input, context)`
- [ ] Persistir contexto (`context.env`) entre execuções
- [ ] Salvar resultado no Redis

#### 3.2 Funcionalidades Adicionais (NOVAS)
- [ ] **Chave Redis Customizável**: Permitir configurar chave de entrada via ConfigMap
- [ ] **Período de Monitoramento Configurável**: Permitir ajustar intervalo de polling
- [ ] **Suporte a Funções Complexas**: Aceitar arquivo ZIP com múltiplos módulos Python
- [ ] **Handler Configurável**: Permitir especificar qual função chamar

### Estrutura de Arquivos a Criar:

```
task3/
├── runtime.py              # Código principal do runtime
├── Dockerfile              # Container do runtime
├── requirements.txt        # Dependências
├── deployment.yaml         # Deployment modificado
├── configmap-runtime.yaml  # ConfigMaps de configuração
└── README.md              # Documentação
```

### Passos de Implementação:

#### 3.3.1 Criar runtime.py
**Arquivo**: `task3/runtime.py`

**Funcionalidades**:
```python
# 1. Conectar ao Redis
# 2. Ler variáveis de ambiente:
#    - REDIS_HOST
#    - REDIS_PORT
#    - REDIS_INPUT_KEY (NOVA)
#    - REDIS_OUTPUT_KEY
#    - MONITORING_PERIOD (NOVA)
#    - HANDLER_FUNCTION (NOVA)
#    - ZIP_URL (NOVA - opcional)
# 3. Carregar módulo do usuário:
#    - Se ZIP_URL existe: baixar e descompactar
#    - Senão: usar pyfile do ConfigMap
# 4. Loop principal:
#    - Ler dados do Redis
#    - Verificar se mudou (comparar com last_execution)
#    - Chamar handler
#    - Persistir context.env
#    - Salvar resultado
#    - Sleep(MONITORING_PERIOD)
```

#### 3.3.2 Criar Dockerfile
**Arquivo**: `task3/Dockerfile`

**Conteúdo base**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar pacotes comuns
RUN pip install redis numpy pandas matplotlib requests

# Copiar runtime
COPY runtime.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "runtime.py"]
```

#### 3.3.3 Criar requirements.txt
**Arquivo**: `task3/requirements.txt`

```
redis>=4.0.0
requests>=2.28.0
```

#### 3.3.4 Criar deployment.yaml modificado
**Arquivo**: `task3/deployment.yaml`

Adicionar suporte aos novos ConfigMaps:
- `REDIS_INPUT_KEY`
- `MONITORING_PERIOD`
- `HANDLER_FUNCTION`
- `ZIP_URL`

#### 3.3.5 Criar ConfigMaps de exemplo
**Arquivo**: `task3/configmap-runtime.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: runtime-config
data:
  REDIS_INPUT_KEY: "metrics"
  MONITORING_PERIOD: "5"
  HANDLER_FUNCTION: "handler_module.handler"
  # ZIP_URL: "http://exemplo.com/function.zip"  # Opcional
```

#### 3.3.6 Implementar Contexto (context object)
```python
class Context:
    def __init__(self, ...):
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.input_key = REDIS_INPUT_KEY
        self.output_key = REDIS_OUTPUT_KEY
        self.function_getmtime = ...
        self.last_execution = ...
        self.env = {}  # Persistir entre chamadas
```

#### 3.3.7 Testar Localmente
```bash
cd task3

# Definir variáveis de ambiente
export REDIS_HOST=192.168.121.48
export REDIS_PORT=6379
export REDIS_INPUT_KEY=metrics
export REDIS_OUTPUT_KEY=seu-id-proj3-output
export MONITORING_PERIOD=5
export HANDLER_FUNCTION=handler_module.handler

# Copiar handler_module.py para task3 (para teste)
cp task1/handler_module.py task3/

# Executar runtime
python runtime.py
```

#### 3.3.8 Build e Push da Imagem
```bash
cd task3

docker build -t seu-usuario/tp3-runtime:v1 .
docker push seu-usuario/tp3-runtime:v1
```

#### 3.3.9 Deploy no Kubernetes
```bash
kubectl apply -f task3/configmap-runtime.yaml
kubectl apply -f task3/deployment.yaml
```

#### 3.3.10 Verificar Funcionamento
```bash
kubectl get pods
kubectl logs -f <runtime-pod>
```

#### 3.3.11 Criar Documentação PDF
- [ ] Explicar arquitetura do runtime
- [ ] Documentar novas funcionalidades
- [ ] Mostrar compatibilidade com runtime original
- [ ] Incluir exemplos de uso das novas features
- [ ] Comparar com `lucasmsp/serverless:redis`

---

## 🧪 Checklist de Testes

### Task 1
- [ ] Handler processa métricas corretamente
- [ ] Média móvel funciona (testar múltiplas execuções)
- [ ] Dados aparecem no Redis
- [ ] Logs do pod não mostram erros

### Task 2
- [ ] Dashboard conecta ao Redis
- [ ] Métricas são visualizadas corretamente
- [ ] Auto-refresh funciona
- [ ] Gráficos de CPU mostram todas as CPUs
- [ ] Acessível via túnel SSH

### Task 3
- [ ] Runtime carrega módulo do usuário
- [ ] Runtime chama handler corretamente
- [ ] Context.env persiste entre execuções
- [ ] Novas funcionalidades funcionam:
  - [ ] Chave Redis customizável
  - [ ] Período configurável
  - [ ] Suporte a ZIP
  - [ ] Handler configurável
- [ ] Compatível com handler da Task 1

---

## 📦 O que Entregar

### Task 1
- [ ] `handler_module.py`
- [ ] `configmap-pyfile.yaml`
- [ ] `configmap-outputkey.yaml`
- [ ] PDF com explicação da média móvel

### Task 2
- [ ] `dashboard.py`
- [ ] `Dockerfile`
- [ ] `requirements.txt`
- [ ] `dashboard-deployment.yaml`
- [ ] `dashboard-service.yaml`
- [ ] PDF com screenshots e explicações

### Task 3
- [ ] `runtime.py`
- [ ] `Dockerfile`
- [ ] `requirements.txt`
- [ ] `deployment.yaml` (modificado)
- [ ] `configmap-runtime.yaml`
- [ ] PDF com documentação técnica

---

## 🆘 Troubleshooting

### Redis não conecta
```bash
# Testar conexão
redis-cli -h 192.168.121.48 -p 6379 ping

# Ver todas as chaves
redis-cli -h 192.168.121.48 -p 6379 keys "*"
```

### Pod não inicia
```bash
kubectl describe pod <nome-pod>
kubectl logs <nome-pod>
```

### ConfigMap não aplica
```bash
kubectl get configmaps
kubectl describe configmap <nome>
kubectl delete configmap <nome>
kubectl apply -f <arquivo.yaml>
```

### Dashboard não atualiza
- Verificar `REDIS_OUTPUT_KEY` está correto
- Verificar função serverless está rodando
- Ver logs do dashboard: `kubectl logs <dashboard-pod>`

---

## 📚 Referências Úteis

- [Redis Python Docs](https://redis-py.readthedocs.io/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Docker Build](https://docs.docker.com/engine/reference/commandline/build/)
- [kubectl Cheatsheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

---

## ⏱️ Estimativa de Tempo

| Task | Tempo Estimado |
|------|---------------|
| Task 1 - Deploy e teste | 1-2 horas |
| Task 1 - Documentação | 30 min |
| Task 2 - Deploy e teste | 2-3 horas |
| Task 2 - Documentação | 30 min |
| Task 3 - Implementação | 4-6 horas |
| Task 3 - Documentação | 1 hora |
| **TOTAL** | **9-13 horas** |

---

## 🎯 Próximos Passos Recomendados

1. **Primeiro**: Complete Task 1 (deploy e teste)
2. **Segundo**: Complete Task 2 (dashboard)
3. **Terceiro**: Implemente Task 3 (runtime)
4. **Por último**: Crie todas as documentações PDF

**Boa sorte! 🚀**

