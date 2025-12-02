# 🔐 Configuração de Acesso SSH à VM

## Informações do Servidor

- **Hostname:** `pugna.snes.dcc.ufmg.br` (ou `pugna.snes.2advanced.dev`)
- **Porta:** `51927`
- **Redis:** `192.168.121.48:6379` (rede interna) ou `67.159.94.11:6379` (externa)

---

## 🛠️ Configuração do SSH

### Opção 1: Editar ~/.ssh/config (Recomendado)

Adicione esta configuração ao seu arquivo `~/.ssh/config`:

```bash
Host cloud2
    HostName pugna.snes.2advanced.dev
    Port 51927
    User seu-usuario
```

**Substitua `seu-usuario`** pelo seu usuário fornecido pelos instrutores.

Depois disso, você pode conectar simplesmente com:

```bash
ssh cloud2
```

### Opção 2: Comando SSH Direto

Se preferir não configurar o arquivo config:

```bash
ssh -p 51927 seu-usuario@pugna.snes.dcc.ufmg.br
```

ou

```bash
ssh -p 51927 seu-usuario@pugna.snes.2advanced.dev
```

---

## 🔧 SSH Tunnels Úteis

### Tunnel para Redis

Se você precisar acessar o Redis da sua máquina local:

```bash
# Opção 1: Com config
ssh -L 6379:192.168.121.48:6379 cloud2

# Opção 2: Sem config
ssh -L 6379:192.168.121.48:6379 -p 51927 seu-usuario@pugna.snes.dcc.ufmg.br
```

Depois você pode acessar Redis como se estivesse local:

```bash
redis-cli -h localhost -p 6379 get metrics
```

Ou no Python:

```python
import redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
data = r.get('seu-id-proj3-output')
```

### Tunnel para Kubernetes Dashboard (se aplicável)

```bash
ssh -L 8001:localhost:8001 cloud2
kubectl proxy
```

Acesse: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

### Tunnel para Seu Dashboard (Task 2)

Quando criar seu dashboard na Task 2, você precisará de um tunnel. Exemplo:

```bash
# Se seu dashboard roda na porta 8050
ssh -L 8050:localhost:8050 cloud2
```

---

## 📋 Comandos Úteis na VM

### Verificar Kubernetes

```bash
# Ver todos os pods no seu namespace
kubectl get pods

# Ver logs de um pod específico
kubectl logs -f <nome-do-pod>

# Ver deployments
kubectl get deployments

# Ver services
kubectl get services

# Ver configmaps
kubectl get configmaps
```

### Verificar Redis

```bash
# Conectar ao Redis
redis-cli -h 192.168.121.48 -p 6379

# Ou se estiver acessível externamente
redis-cli -h 67.159.94.11 -p 6379
```

Comandos Redis úteis:

```bash
# Listar todas as chaves
keys *

# Listar chaves do projeto
keys *proj3*

# Ver dados de entrada (coletados pelo sistema)
get metrics

# Ver seus dados de saída (calculados pela função)
get seu-id-proj3-output

# Ver uso de memória de uma chave
memory usage metrics
```

---

## 🔍 Troubleshooting

### Problema: Connection refused

```bash
# Verificar se a porta está correta
ssh -v -p 51927 seu-usuario@pugna.snes.dcc.ufmg.br
```

### Problema: Permission denied (publickey)

Certifique-se de que sua chave SSH foi adicionada aos authorized_keys do servidor:

```bash
# Gerar chave SSH se não tiver
ssh-keygen -t rsa -b 4096

# Copiar chave pública para o servidor
ssh-copy-id -p 51927 seu-usuario@pugna.snes.dcc.ufmg.br
```

### Problema: kubectl não funciona

```bash
# Verificar se kubectl está configurado
kubectl config view

# Ver contexto atual
kubectl config current-context

# Listar namespaces
kubectl get namespaces
```

---

## 🎯 Workflow Típico

### 1. Conectar à VM

```bash
ssh cloud2
```

### 2. Verificar/Aplicar ConfigMaps

```bash
# Listar ConfigMaps existentes
kubectl get configmaps

# Aplicar seus ConfigMaps (arquivos locais já transferidos)
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
```

### 3. Aplicar Deployment

```bash
kubectl apply -f serverless-deployment-course.yaml
```

### 4. Monitorar

```bash
# Ver status do pod
kubectl get pods -w

# Ver logs em tempo real
kubectl logs -f <nome-do-pod>
```

### 5. Verificar Resultados

```bash
# No Redis
redis-cli -h 192.168.121.48 -p 6379 get seu-id-proj3-output
```

---

## 📤 Transferir Arquivos para a VM

### Opção 1: SCP com config

```bash
# Copiar arquivo para VM
scp arquivo.yaml cloud2:~/

# Copiar diretório
scp -r pasta/ cloud2:~/
```

### Opção 2: SCP sem config

```bash
scp -P 51927 arquivo.yaml seu-usuario@pugna.snes.dcc.ufmg.br:~/
```

### Opção 3: rsync (mais eficiente)

```bash
rsync -avz -e "ssh -p 51927" ./TP3/ seu-usuario@pugna.snes.dcc.ufmg.br:~/TP3/
```

---

## 🔐 Boas Práticas de Segurança

1. **Use chaves SSH** ao invés de senhas
2. **Não compartilhe** suas credenciais
3. **Não commite** arquivos com senhas/tokens no Git
4. **Use namespaces** separados no Kubernetes para isolar seu trabalho
5. **Limpe recursos** quando não estiver usando (delete pods/deployments)

---

## 📚 Referências Rápidas

### Endereços Importantes

- **VM SSH:** `pugna.snes.dcc.ufmg.br:51927`
- **Redis (interno):** `192.168.121.48:6379`
- **Redis (externo):** `67.159.94.11:6379`

### Chaves Redis

- **Input:** `metrics` (dados coletados)
- **Output:** `seu-id-proj3-output` (seus resultados)

### Recursos Kubernetes

- **ConfigMap pyfile:** Contém seu código Python
- **ConfigMap outputkey:** Contém sua chave Redis de saída
- **Deployment:** `serverless-redis`
- **Pod:** `serverless-redis-xxxxx`

---

**Pronto para começar!** 🚀

Com esta configuração, você tem acesso completo à infraestrutura do TP3.

