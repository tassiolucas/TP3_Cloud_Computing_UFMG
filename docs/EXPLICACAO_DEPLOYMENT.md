# 📦 Explicação do Deployment Serverless

## Para que serve este arquivo?

O arquivo `serverless-deployment-course.yaml` é o **Deployment do Kubernetes** que executa sua função serverless. Ele:

1. ✅ Cria um Pod com o runtime serverless
2. ✅ Monta seu código Python dentro do container
3. ✅ Configura conexão com Redis
4. ✅ Define onde ler e escrever dados
5. ✅ Chama sua função `handler()` automaticamente a cada 5 segundos

---

## 🔍 Anatomia do Deployment (Linha por Linha)

### Metadados Básicos

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: serverless-redis
```

- Define que é um **Deployment** do Kubernetes
- Nome do deployment: `serverless-redis`

---

### Configuração de Réplicas

```yaml
spec:
  replicas: 1
  selector:
    matchLabels:
      app: serverless-redis
```

- **`replicas: 1`**: Apenas 1 pod rodando (suficiente para este projeto)
- **`selector`**: Identifica quais pods pertencem a este deployment

---

### Template do Pod

```yaml
template:
  metadata:
    labels:
      app: serverless-redis
```

- Define os **labels** do pod criado

---

### 🐳 Container Runtime

```yaml
spec:
  containers:
  - name: serverless-redis
    image: lucasmsp/serverless:redis
    imagePullPolicy: Always
```

- **`image`**: Imagem Docker do runtime fornecida pelos instrutores
  - Contém Python + Redis client + lógica para chamar funções
  - Você **NÃO precisa modificar** esta imagem na Task 1
  - Na Task 3, você vai criar sua própria imagem para substituir esta

- **`imagePullPolicy: Always`**: Sempre baixa a versão mais recente

---

### 💻 Recursos Computacionais

```yaml
resources:
  requests:
    cpu: 100m
    memory: 300Mi
```

- **`cpu: 100m`**: 0.1 CPU core (10% de 1 core)
- **`memory: 300Mi`**: 300 megabytes de RAM
- Recursos suficientes para processar métricas

---

### 📁 Montagem do Seu Código Python

```yaml
volumeMounts:
- name: pyfile
  mountPath: "/opt/usermodule.py"
  subPath: pyfile
```

**🔥 IMPORTANTE:** Aqui é onde seu código entra!

- **`name: pyfile`**: Referência ao volume (definido no final)
- **`mountPath`**: Caminho **dentro** do container onde seu código fica
  - O runtime vai procurar por `/opt/usermodule.py`
  - Vai importar e chamar `handler()` desse arquivo
- **`subPath: pyfile`**: Usa a chave `pyfile` do ConfigMap

---

### 🔧 Variáveis de Ambiente

#### Configuração do Redis

```yaml
env:
- name: REDIS_HOST
  value: "192.168.121.48"
- name: REDIS_PORT
  value: "6379"
```

- **Host e porta do Redis** onde os dados estão
- Estes valores são para a rede interna da VM

#### Chave de Entrada

```yaml
- name: REDIS_INPUT_KEY
  value: "metrics"
```

- **`REDIS_INPUT_KEY`**: Chave Redis onde o coletor de métricas **escreve** os dados
- O runtime lê desta chave a cada 5 segundos

#### Chave de Saída (Seu ConfigMap!)

```yaml
- name: REDIS_OUTPUT_KEY
  valueFrom:
    configMapKeyRef:
      name: outputkey
      key: REDIS_OUTPUT_KEY
```

**🔥 MUITO IMPORTANTE:**

- Aqui o runtime pega o valor do seu **ConfigMap `outputkey`**
- Por isso você criou `configmap-outputkey.yaml`!
- O runtime vai **escrever** os resultados da sua função nesta chave

---

### 📦 Volumes

```yaml
volumes:
- name: pyfile
  configMap:
    name: pyfile
```

- Define o volume `pyfile` que vem do **ConfigMap `pyfile`**
- Por isso você criou `configmap-pyfile.yaml`!
- Este ConfigMap contém todo o código do seu `handler_module.py`

---

## 🔄 Fluxo Completo

Veja como tudo funciona junto:

```
┌─────────────────────────────────────────────────────────────┐
│  1. Coletor de Métricas (já rodando na VM)                 │
│     └─> Escreve em Redis: key="metrics"                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Runtime Serverless (lucasmsp/serverless:redis)         │
│     ├─> Lê REDIS_INPUT_KEY="metrics" (a cada 5s)          │
│     ├─> Carrega /opt/usermodule.py (seu código!)          │
│     ├─> Chama handler(input, context)                      │
│     └─> Escreve resultado em REDIS_OUTPUT_KEY             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Redis                                                   │
│     └─> key="seu-id-proj3-output" (seus resultados!)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Seu Dashboard (Task 2)                                  │
│     └─> Lê e visualiza os resultados                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Por que você precisa dos ConfigMaps?

### ConfigMap `pyfile`
```
Seu código Python → configmap-pyfile.yaml → Volume no Pod → /opt/usermodule.py
```

### ConfigMap `outputkey`
```
Seu ID → configmap-outputkey.yaml → Variável REDIS_OUTPUT_KEY → Runtime sabe onde escrever
```

**Sem estes ConfigMaps, o deployment não funciona!**

---

## 🚀 Como Fazer Deploy (Completo)

### Passo 1: Editar ConfigMap Output Key
```bash
# Abrir configmap-outputkey.yaml
# Substituir 'seu-id' pelo seu ID real (ex: ifs4)
```

### Passo 2: Aplicar ConfigMaps
```bash
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
```

### Passo 3: Aplicar Deployment
```bash
kubectl apply -f serverless-deployment-course.yaml
```

### Passo 4: Verificar
```bash
# Ver se o pod foi criado
kubectl get pods

# Ver logs do runtime
kubectl logs -f <nome-do-pod>

# Verificar resultado no Redis
redis-cli -h 67.159.94.11 -p 6379 get seu-id-proj3-output
```

---

## 🔍 Troubleshooting

### Pod não inicia

```bash
kubectl describe pod <nome-do-pod>
```

**Possíveis causas:**
- ConfigMaps não foram criados
- Erro de sintaxe no YAML
- Imagem não foi baixada

### Pod roda mas sem output

```bash
kubectl logs <nome-do-pod>
```

**Possíveis causas:**
- Erro no seu código Python
- ConfigMap `pyfile` não tem o código correto
- Redis não está acessível

### Output no Redis está errado

```bash
# Verificar o que está sendo escrito
redis-cli -h 67.159.94.11 -p 6379 get seu-id-proj3-output

# Ver logs para debug
kubectl logs <nome-do-pod>
```

---

## 🎓 Task 3: Criar Seu Próprio Runtime

Na **Task 3**, você vai:

1. Substituir `image: lucasmsp/serverless:redis` pela sua própria imagem
2. Adicionar funcionalidades extras:
   - Configurar período de monitoramento
   - Suporte a funções ZIP (multi-arquivo)
   - Configurar function handler customizado
3. Modificar este deployment para usar suas configurações

Mas isso é para depois! Por enquanto, use este deployment como está.

---

## ✅ Resumo

Este deployment:
- ✅ Executa o runtime serverless em um Pod
- ✅ Monta seu código Python do ConfigMap
- ✅ Conecta ao Redis
- ✅ Chama sua função automaticamente
- ✅ Persiste resultados no Redis
- ✅ Está pronto para uso na Task 1

**É o coração do sistema serverless!** 🎉

---

**Próximo Passo:** Aplicar este deployment após criar os ConfigMaps!

