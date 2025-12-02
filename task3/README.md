# Task 3: Runtime Serverless Customizado

Este diretório contém a implementação de um runtime serverless customizado que substitui `lucasmsp/serverless:redis` com funcionalidades adicionais.

## 📋 Visão Geral

O runtime customizado mantém compatibilidade com o runtime original e adiciona novas funcionalidades:

### Funcionalidades Originais (Compatíveis)
- ✅ Lê dados de Redis periodicamente
- ✅ Carrega módulo Python via ConfigMap (pyfile)
- ✅ Chama função `handler(input, context)`
- ✅ Persiste `context.env` entre execuções
- ✅ Salva resultado no Redis

### Funcionalidades Adicionais (NOVAS)
- ⭐ **Chave Redis Customizável**: Permite configurar chave de entrada diferente de `metrics`
- ⭐ **Período de Monitoramento Configurável**: Ajusta intervalo de polling (padrão: 5s)
- ⭐ **Suporte a Funções Complexas**: Aceita ZIP com múltiplos módulos Python
- ⭐ **Handler Configurável**: Permite especificar qual função chamar

## 📦 Estrutura de Arquivos

```
task3/
├── runtime.py                  # Código principal do runtime
├── Dockerfile                  # Container do runtime
├── requirements.txt            # Dependências Python
├── deployment.yaml             # Deployment Kubernetes modificado
├── configmap-runtime.yaml      # ConfigMap com novas configurações
├── README.md                   # Este arquivo
└── test/                       # Testes (opcional)
    ├── test_runtime.py
    └── sample_function.py
```

## 🚀 Como Usar

### 1. Build da Imagem Docker

```bash
cd task3

# Build
docker build -t seu-usuario/tp3-runtime:v1 .

# Testar localmente
docker run \
  -e REDIS_HOST=192.168.121.48 \
  -e REDIS_PORT=6379 \
  -e REDIS_INPUT_KEY=metrics \
  -e REDIS_OUTPUT_KEY=seu-id-proj3-output \
  -e MONITORING_PERIOD=5 \
  seu-usuario/tp3-runtime:v1
```

### 2. Push da Imagem

```bash
docker login
docker push seu-usuario/tp3-runtime:v1
```

### 3. Configurar ConfigMaps

#### ConfigMap 1: pyfile (mesma da Task 1)
```bash
kubectl apply -f ../task1/configmap-pyfile.yaml
```

#### ConfigMap 2: outputkey (mesma da Task 1)
```bash
kubectl apply -f ../task1/configmap-outputkey.yaml
```

#### ConfigMap 3: runtime-config (NOVO)
```bash
# Editar configmap-runtime.yaml com suas configurações
kubectl apply -f configmap-runtime.yaml
```

### 4. Editar Deployment

Edite `deployment.yaml`:
```yaml
spec:
  template:
    spec:
      containers:
      - name: runtime
        image: seu-usuario/tp3-runtime:v1  # <-- ATUALIZAR
```

### 5. Deploy no Kubernetes

```bash
kubectl apply -f deployment.yaml

# Verificar
kubectl get pods
kubectl logs -f <runtime-pod>
```

## ⚙️ Configurações

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `REDIS_HOST` | `localhost` | Host do Redis |
| `REDIS_PORT` | `6379` | Porta do Redis |
| `REDIS_INPUT_KEY` | `metrics` | Chave Redis de entrada ⭐ |
| `REDIS_OUTPUT_KEY` | `output` | Chave Redis de saída |
| `MONITORING_PERIOD` | `5` | Período de polling (segundos) ⭐ |
| `HANDLER_FUNCTION` | `handler_module.handler` | Função handler ⭐ |
| `ZIP_URL` | (vazio) | URL do ZIP com código ⭐ |
| `PYFILE_PATH` | `/app/pyfile/pyfile` | Path do pyfile |

⭐ = Nova funcionalidade (não existe no runtime original)

### Exemplo de Configuração

```yaml
# configmap-runtime.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: runtime-config
data:
  REDIS_INPUT_KEY: "metrics"
  MONITORING_PERIOD: "10"
  HANDLER_FUNCTION: "handler_module.handler"
  # ZIP_URL: "https://exemplo.com/function.zip"
```

## 📝 Interface do Handler

Sua função handler deve seguir esta assinatura:

```python
def handler(input: dict, context: object) -> dict:
    """
    Args:
        input: Dados lidos do Redis (JSON)
        context: Objeto com metadados e estado
    
    Returns:
        Dicionário JSON-encodable
    """
    
    # Acessar informações do contexto
    print(f"Host: {context.host}")
    print(f"Port: {context.port}")
    print(f"Input Key: {context.input_key}")
    print(f"Output Key: {context.output_key}")
    
    # Estado persistente
    if 'counter' not in context.env:
        context.env['counter'] = 0
    
    context.env['counter'] += 1
    
    # Processar dados
    result = {
        'status': 'ok',
        'execution_count': context.env['counter']
    }
    
    return result
```

## 🧪 Testes

### Teste Local (Sem Docker)

```bash
# Configurar variáveis
export REDIS_HOST=192.168.121.48
export REDIS_PORT=6379
export REDIS_INPUT_KEY=metrics
export REDIS_OUTPUT_KEY=test-output
export MONITORING_PERIOD=5
export HANDLER_FUNCTION=handler_module.handler

# Copiar handler da Task 1
cp ../task1/handler_module.py .

# Executar runtime
python runtime.py
```

### Teste com Docker

```bash
docker run \
  -e REDIS_HOST=192.168.121.48 \
  -e REDIS_PORT=6379 \
  -e REDIS_INPUT_KEY=metrics \
  -e REDIS_OUTPUT_KEY=test-output \
  -v $(pwd)/../task1/handler_module.py:/app/pyfile/pyfile \
  seu-usuario/tp3-runtime:v1
```

### Teste no Kubernetes

```bash
# Deploy
kubectl apply -f deployment.yaml

# Ver logs
kubectl logs -f deployment/serverless-runtime-custom

# Verificar resultado no Redis
redis-cli -h 192.168.121.48 -p 6379 get seu-id-proj3-output
```

## 🆚 Comparação com Runtime Original

| Feature | Runtime Original | Runtime Customizado |
|---------|-----------------|---------------------|
| Ler dados do Redis | ✅ | ✅ |
| ConfigMap pyfile | ✅ | ✅ |
| Chamar handler | ✅ | ✅ |
| Persistir context.env | ✅ | ✅ |
| Chave entrada configurável | ❌ | ✅ |
| Período configurável | ❌ | ✅ |
| Suporte a ZIP | ❌ | ✅ |
| Handler configurável | ❌ | ✅ |

## 🐛 Troubleshooting

### Runtime não conecta ao Redis
```bash
# Verificar Redis está acessível
redis-cli -h 192.168.121.48 -p 6379 ping

# Verificar variável REDIS_HOST
kubectl describe pod <runtime-pod> | grep REDIS_HOST
```

### Módulo não carregado
```bash
# Verificar pyfile ConfigMap
kubectl get configmap pyfile -o yaml

# Ver logs do runtime
kubectl logs <runtime-pod>
```

### Handler não encontrado
```bash
# Verificar HANDLER_FUNCTION
kubectl get configmap runtime-config -o yaml

# Formato correto: module_name.function_name
# Exemplo: handler_module.handler
```

## 📚 Documentação Adicional

Para mais informações, consulte:

- `runtime.py` - Código comentado do runtime
- `../docs/PLANO_DE_EXECUCAO.md` - Plano completo do projeto
- `../docs/INICIO_RAPIDO.md` - Guia rápido

## ✅ Checklist de Implementação

- [ ] runtime.py implementado
- [ ] Dockerfile criado
- [ ] requirements.txt definido
- [ ] deployment.yaml modificado
- [ ] configmap-runtime.yaml criado
- [ ] Teste local funcionando
- [ ] Imagem Docker buildada e pushed
- [ ] Deploy no Kubernetes
- [ ] Compatibilidade verificada com Task 1
- [ ] Documentação PDF criada

## 👤 Autor

**[SEU NOME]**  
**ID:** [SEU ID]  
**Curso:** Mestrado UFMG - Cloud Computing

