# TP3 - Serverless Computing e Dashboard de Monitoramento

Este repositório contém a implementação completa do Projeto 3 do curso de Mestrado da UFMG.

## 📋 Estrutura do Projeto

```
TP3/
├── handler_module.py                    # Módulo Python com função serverless
├── configmap-pyfile.yaml                # ConfigMap com código Python
├── configmap-outputkey.yaml             # ConfigMap com chave de saída Redis
├── serverless-deployment-course.yaml    # Deployment Kubernetes fornecido
├── TASK1_DOCUMENTACAO.md                # Documentação detalhada Task 1
├── EXPLICACAO_DEPLOYMENT.md             # Explicação do deployment
├── CONFIGURACAO_SSH.md                  # Guia de configuração SSH
├── GUIA_RAPIDO.md                       # Guia rápido de uso
├── README.md                            # Este arquivo
├── deploy-task1.sh                      # Script de deploy automático
├── setup-ssh.sh                         # Script de configuração SSH
└── test_redis_connection.py             # Script de teste Redis
```

## 🚀 Task 1: Função Serverless

### Visão Geral

A Task 1 implementa uma função serverless que processa métricas de sistema (CPU, memória, rede) e calcula:

1. **Porcentagem de tráfego de saída de rede**
2. **Porcentagem de memória em cache** (buffers + cached)
3. **Média móvel de utilização de CPU** nos últimos 60 segundos

### Arquivos

- **`handler_module.py`**: Código fonte do módulo Python
- **`configmap-pyfile.yaml`**: ConfigMap Kubernetes contendo o código
- **`configmap-outputkey.yaml`**: ConfigMap com a chave Redis de saída

### Como Usar

#### 1. Configurar Output Key

O arquivo `configmap-outputkey.yaml` já está configurado com seu ID:

```yaml
REDIS_OUTPUT_KEY: "2025720437-proj3-output"
```

#### 2. Testar Localmente (Opcional)

```bash
python handler_module.py
```

#### 3. Aplicar ConfigMaps no Kubernetes

```bash
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
```

#### 4. Fazer Deploy da Aplicação

```bash
# Assumindo que você tem o deployment.yaml fornecido pelos instrutores
kubectl apply -f deployment.yaml
```

#### 5. Verificar Funcionamento

```bash
# Ver status dos pods
kubectl get pods

# Ver logs do pod
kubectl logs -f <nome-do-pod>

# Verificar dados no Redis
redis-cli -h 192.168.121.48 -p 6379 get 2025720437-proj3-output
# ou externamente:
redis-cli -h 67.159.94.11 -p 6379 get 2025720437-proj3-output
```

### Exemplo de Saída

```json
{
  "percent-network-egress": 20.0,
  "percent-memory-cache": 15.625,
  "avg-util-cpu0-60sec": 45.5,
  "avg-util-cpu1-60sec": 32.1,
  "avg-util-cpu2-60sec": 67.8,
  "avg-util-cpu3-60sec": 21.4,
  "timestamp": "2025-11-23T10:30:00",
  "num_cpus_monitored": 4
}
```

## 📊 Task 2: Dashboard de Monitoramento

**Status:** A ser implementado

## ⚙️ Task 3: Runtime Serverless Customizado

**Status:** A ser implementado

## 🔧 Requisitos

- Python 3.8+
- Acesso SSH à VM (pugna.snes.2advanced.dev:51927)
- Kubernetes cluster configurado
- kubectl configurado
- Redis (disponível em 192.168.121.48:6379 ou 67.159.94.11:6379)

## 🔐 Configuração de Acesso

### Configurar SSH

Use o script fornecido para configurar acesso rápido:

```bash
./setup-ssh.sh seu-usuario
```

Ou configure manualmente seu `~/.ssh/config`:

```bash
Host cloud2
    HostName pugna.snes.2advanced.dev
    Port 51927
    User seu-usuario
```

Depois, conecte com:

```bash
ssh cloud2
```

📖 **Para detalhes completos, veja:** [CONFIGURACAO_SSH.md](CONFIGURACAO_SSH.md)

## 📚 Documentação

Para detalhes completos sobre a implementação, especialmente sobre a abordagem de manutenção de estado para a média móvel, consulte:

- **[TASK1_DOCUMENTACAO.md](TASK1_DOCUMENTACAO.md)**: Documentação técnica detalhada

## 👤 Autor

**ID:** 2025720437  
**Curso:** Mestrado UFMG - Cloud Computing

## 📝 Notas

- A coleta de métricas ocorre a cada 5 segundos
- A janela da média móvel contém os últimos 12 valores (60 segundos)
- O estado é mantido usando `context.env` do runtime serverless
- O número de CPUs é detectado dinamicamente

## 🔗 Links Úteis

- [Redis Python Documentation](https://redis-py.readthedocs.io/)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [Kubernetes ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)

