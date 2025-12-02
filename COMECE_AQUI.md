# 🚀 COMECE AQUI - TP3 Cloud Computing

## 👤 Seu ID: 2025720437

**Chave Redis:** `2025720437-proj3-output`

---

## ✨ Tudo Pronto para Você!

Preparei uma estrutura completa do projeto com:
- ✅ **3 Tasks implementadas e documentadas**
- ✅ **Seu ID já configurado em todos os arquivos**
- ✅ **Scripts de automação prontos**
- ✅ **Documentação completa em português**

---

## 📂 Estrutura do Projeto

```
TP3_Cloud_Computing_UFMG/
│
├── 📄 RESUMO_PERSONALIZADO.md     ⭐ LEIA ESTE PRIMEIRO!
├── 📄 README.md                   Visão geral do projeto
│
├── 📁 docs/
│   ├── PLANO_DE_EXECUCAO.md      Plano completo detalhado
│   ├── INICIO_RAPIDO.md          Guia rápido passo a passo
│   └── ...
│
├── 📁 task1/                      ✅ PRONTO PARA DEPLOY
│   ├── handler_module.py         Função serverless
│   ├── configmap-pyfile.yaml     ConfigMap com código
│   ├── configmap-outputkey.yaml  ✅ Configurado: 2025720437
│   └── serverless-deployment-course.yaml
│
├── 📁 task2/                      ✅ PRONTO PARA BUILD
│   ├── dashboard.py               ✅ Configurado: 2025720437
│   ├── Dockerfile                 Container pronto
│   ├── dashboard-deployment.yaml  ✅ Configurado: 2025720437
│   ├── dashboard-service.yaml     Service Kubernetes
│   ├── requirements.txt           Dependências
│   └── build-and-push.sh          🤖 Script automático
│
└── 📁 task3/                      ✅ IMPLEMENTADO COMPLETO
    ├── runtime.py                 Runtime customizado (300+ linhas!)
    ├── Dockerfile                 Container pronto
    ├── deployment.yaml            Deployment modificado
    ├── configmap-runtime.yaml     Configurações novas
    ├── requirements.txt           Dependências
    ├── build-and-push.sh          🤖 Script automático
    └── README.md                  Documentação completa
```

---

## 🎯 Seus Próximos 3 Passos

### 1️⃣ Task 1 (30 minutos) - COMECE POR AQUI

```bash
# Conectar na VM
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927

# Aplicar configurações
cd TP3_Cloud_Computing_UFMG/task1
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
kubectl apply -f serverless-deployment-course.yaml

# Verificar
kubectl get pods
kubectl logs -f <pod-name>

# Testar no Redis
redis-cli -h 192.168.121.48 -p 6379 get 2025720437-proj3-output
```

**✅ Sucesso se**: Ver JSON com métricas de CPU, memória e rede

---

### 2️⃣ Task 2 (2 horas)

```bash
# Na sua máquina local
cd task2

# Usar script automático (recomendado)
./build-and-push.sh

# Depois, na VM:
# 1. Editar dashboard-deployment.yaml (linha 21: sua imagem Docker)
# 2. Editar dashboard-service.yaml (linha com nodePort: sua porta)
kubectl apply -f dashboard-deployment.yaml
kubectl apply -f dashboard-service.yaml

# Acessar via SSH tunnel
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:SUA_PORTA tassioalmeida@pugna.snes.2advanced.dev -p 51927
# Abrir: http://localhost:8501
```

**✅ Sucesso se**: Dashboard mostra gráficos com suas métricas

---

### 3️⃣ Task 3 (4-6 horas)

```bash
# Na sua máquina local
cd task3

# Usar script automático (recomendado)
./build-and-push.sh

# Depois, na VM:
# 1. Editar deployment.yaml (linha 21: sua imagem Docker)
kubectl apply -f ../task1/configmap-pyfile.yaml
kubectl apply -f ../task1/configmap-outputkey.yaml
kubectl apply -f configmap-runtime.yaml
kubectl apply -f deployment.yaml

# Verificar
kubectl logs -f <runtime-pod>
```

**✅ Sucesso se**: Runtime processa dados e salva no Redis

---

## 📖 Documentos Importantes

| Arquivo | Para que serve |
|---------|---------------|
| **RESUMO_PERSONALIZADO.md** | ⭐ Resumo completo com seu ID e comandos prontos |
| **docs/INICIO_RAPIDO.md** | Guia rápido passo a passo |
| **docs/PLANO_DE_EXECUCAO.md** | Plano detalhado com todas as etapas |
| **task3/README.md** | Documentação completa da Task 3 |

---

## 🔧 O que Você Precisa Fazer

### Antes de começar:
- [ ] Ter acesso SSH à VM
- [ ] Ter Docker instalado (para Tasks 2 e 3)
- [ ] Ter conta no Docker Hub
- [ ] Saber sua porta do DevOps (para calcular porta do dashboard)

### Task 1:
- [x] Código implementado ✅
- [x] ConfigMaps com seu ID ✅
- [ ] Fazer deploy
- [ ] Testar no Redis
- [ ] Criar PDF explicando média móvel

### Task 2:
- [x] Dashboard implementado ✅
- [x] Dockerfile pronto ✅
- [x] Seu ID configurado ✅
- [ ] Build da imagem Docker
- [ ] Calcular sua porta
- [ ] Fazer deploy
- [ ] Tirar screenshots
- [ ] Criar PDF com screenshots e explicações

### Task 3:
- [x] Runtime implementado ✅ (300+ linhas!)
- [x] Dockerfile pronto ✅
- [x] Funcionalidades adicionais ✅
  - [x] Chave Redis configurável
  - [x] Período de monitoramento configurável
  - [x] Suporte a ZIP
  - [x] Handler configurável
- [ ] Build da imagem Docker
- [ ] Fazer deploy
- [ ] Testar compatibilidade
- [ ] Criar PDF com documentação técnica

---

## 💡 Dicas Importantes

1. **Comece pela Task 1** - É a base de tudo (30 min)
2. **Seu ID já está configurado** - Não precisa editar manualmente
3. **Use os scripts** `build-and-push.sh` - Eles facilitam muito!
4. **Teste localmente** antes de fazer deploy (quando possível)
5. **Consulte os logs** sempre: `kubectl logs -f <pod-name>`

---

## 🎨 Calcular Porta do Dashboard

```
Porta Dashboard = Porta DevOps + 100
```

**Exemplo:**
- Porta DevOps: 30500
- Porta Dashboard: 30600

Editar em `task2/dashboard-service.yaml`:
```yaml
nodePort: 30600  # Sua porta aqui
```

---

## 🆘 Comandos Úteis

```bash
# Ver pods
kubectl get pods

# Ver logs
kubectl logs -f <pod-name>

# Ver serviços
kubectl get services

# Deletar pod
kubectl delete pod <pod-name>

# Testar Redis
redis-cli -h 192.168.121.48 -p 6379 get 2025720437-proj3-output

# Listar chaves Redis
redis-cli -h 192.168.121.48 -p 6379 keys "*"
```

---

## 📊 Status Atual

```
✅ Task 1: Código completo + ID configurado
✅ Task 2: Dashboard completo + ID configurado
✅ Task 3: Runtime completo (300+ linhas de código!)
✅ Documentação completa em português
✅ Scripts de automação prontos
✅ Seu ID (2025720437) em todos os lugares
```

**Você está 100% pronto para começar! 🎉**

---

## 🚀 Comece Agora!

```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
cd TP3_Cloud_Computing_UFMG/task1
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
kubectl apply -f serverless-deployment-course.yaml
kubectl get pods
```

---

## 📞 Precisa de Ajuda?

Consulte:
1. **RESUMO_PERSONALIZADO.md** - Comandos específicos para seu ID
2. **docs/INICIO_RAPIDO.md** - Guia passo a passo
3. **docs/PLANO_DE_EXECUCAO.md** - Plano detalhado completo

**Boa sorte no seu projeto! 🍀🚀**

