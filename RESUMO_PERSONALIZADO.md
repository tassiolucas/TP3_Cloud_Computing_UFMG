# 🎯 Resumo Personalizado - TP3 Cloud Computing

## 👤 Informações do Estudante

**ID do Estudante:** `2025720437`  
**Chave Redis:** `2025720437-proj3-output`

---

## ✅ O que foi preparado para você

### 📦 Task 1: Função Serverless
- ✅ Código Python implementado (`handler_module.py`)
- ✅ ConfigMaps configurados com seu ID
- ✅ Pronto para deploy

**Chave Redis configurada:** `2025720437-proj3-output`

### 📊 Task 2: Dashboard de Monitoramento
- ✅ Dashboard Streamlit implementado
- ✅ Dockerfile preparado
- ✅ Deployment e Service configurados com seu ID
- ✅ Script de build automatizado

**Sua chave Redis já está configurada no código!**

### ⚙️ Task 3: Runtime Serverless
- ✅ Runtime completo implementado
- ✅ Dockerfile preparado
- ✅ ConfigMaps de exemplo criados
- ✅ Deployment modificado pronto
- ✅ Script de build automatizado

---

## 🚀 Comandos Prontos para Uso

### Task 1 - Deploy da Função Serverless

```bash
# Conectar na VM
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927

# Navegar até o diretório
cd TP3_Cloud_Computing_UFMG/task1

# Aplicar ConfigMaps (já configurados com seu ID!)
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml

# Fazer deploy
kubectl apply -f serverless-deployment-course.yaml

# Verificar
kubectl get pods
kubectl logs -f <pod-name>

# Testar no Redis
redis-cli -h 192.168.121.48 -p 6379 get 2025720437-proj3-output
```

### Task 2 - Deploy do Dashboard

```bash
# Na sua máquina local
cd task2

# Build e push (script interativo)
./build-and-push.sh

# Ou manualmente:
docker build -t seu-usuario/tp3-dashboard:v1 .
docker push seu-usuario/tp3-dashboard:v1

# Editar dashboard-deployment.yaml (mudar a imagem)
# Depois, na VM:
kubectl apply -f dashboard-deployment.yaml
kubectl apply -f dashboard-service.yaml

# Acessar dashboard (tunelSSH)
# Calcule sua porta: Porta DevOps + 100
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:SUA_PORTA tassioalmeida@pugna.snes.2advanced.dev -p 51927
# Acesse: http://localhost:8501
```

### Task 3 - Deploy do Runtime Customizado

```bash
# Na sua máquina local
cd task3

# Build e push (script interativo)
./build-and-push.sh

# Ou manualmente:
docker build -t seu-usuario/tp3-runtime:v1 .
docker push seu-usuario/tp3-runtime:v1

# Na VM:
kubectl apply -f ../task1/configmap-pyfile.yaml
kubectl apply -f ../task1/configmap-outputkey.yaml
kubectl apply -f configmap-runtime.yaml
kubectl apply -f deployment.yaml

# Verificar
kubectl get pods
kubectl logs -f <runtime-pod>
```

---

## 🔍 Verificação Rápida

### Verificar se Task 1 está funcionando:
```bash
redis-cli -h 192.168.121.48 -p 6379 get 2025720437-proj3-output
```

**Resultado esperado:** JSON com métricas de CPU, memória e rede

### Verificar pods:
```bash
kubectl get pods
kubectl get services
```

### Ver logs:
```bash
kubectl logs -f <pod-name>
```

---

## 📋 Checklist de Conclusão

### Task 1
- [ ] Configurado com ID: `2025720437` ✅ (já feito!)
- [ ] ConfigMaps aplicados
- [ ] Pod rodando
- [ ] Dados visíveis no Redis
- [ ] PDF com explicação da média móvel

### Task 2
- [ ] Imagem Docker buildada
- [ ] Push para Docker Hub
- [ ] Deployment editado com sua imagem
- [ ] Aplicado no Kubernetes
- [ ] Dashboard acessível
- [ ] PDF com screenshots

### Task 3
- [ ] Runtime implementado ✅ (código pronto!)
- [ ] Imagem Docker buildada
- [ ] Push para Docker Hub
- [ ] Deployment editado com sua imagem
- [ ] Testado e funcionando
- [ ] PDF com documentação técnica

---

## 🎨 Sua Porta do Dashboard

**Cálculo:** Porta DevOps + 100

Se você não sabe sua porta do DevOps, consulte o projeto anterior ou escolha uma porta entre `30000-32767` que não esteja em uso.

**Exemplo:**
- Porta DevOps: `30500`
- Porta Dashboard: `30600`

Edite em `task2/dashboard-service.yaml`:
```yaml
spec:
  type: NodePort
  ports:
    - port: 8501
      targetPort: 8501
      nodePort: 30600  # <-- Sua porta aqui
```

---

## 📚 Documentação Disponível

- 📘 **PLANO_DE_EXECUCAO.md** - Plano completo e detalhado
- 🚀 **INICIO_RAPIDO.md** - Guia rápido passo a passo
- 📖 **task1/**: Código e ConfigMaps prontos
- 📊 **task2/**: Dashboard completo
- ⚙️ **task3/**: Runtime implementado

---

## 🆘 Troubleshooting Rápido

### Redis não conecta:
```bash
redis-cli -h 192.168.121.48 -p 6379 ping
```

### ConfigMap não aplica:
```bash
kubectl delete configmap <nome>
kubectl apply -f <arquivo.yaml>
```

### Pod não inicia:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Dashboard não mostra dados:
1. Verificar Task 1 está rodando
2. Verificar chave Redis: `2025720437-proj3-output`
3. Ver logs: `kubectl logs <dashboard-pod>`

---

## 🎯 Ordem Recomendada de Execução

1. **Task 1** (30 min - 1h)
   - Aplicar ConfigMaps
   - Fazer deploy
   - Verificar funcionamento
   - ✅ Mais simples, já está tudo configurado!

2. **Task 2** (2-3h)
   - Build da imagem Docker
   - Deploy no Kubernetes
   - Acessar dashboard
   - Tirar screenshots

3. **Task 3** (4-6h)
   - Entender o código do runtime
   - Build da imagem Docker
   - Deploy e teste
   - Verificar compatibilidade

---

## 📦 Arquivos Importantes já Configurados

Estes arquivos **JÁ ESTÃO** configurados com seu ID:

- ✅ `task1/configmap-outputkey.yaml` → `2025720437-proj3-output`
- ✅ `task2/dashboard.py` → `2025720437-proj3-output`
- ✅ `task2/dashboard-deployment.yaml` → `2025720437-proj3-output`

Você só precisa:
1. Substituir `seu-usuario` pela sua conta do Docker Hub
2. Calcular sua porta do dashboard
3. Fazer deploy!

---

## 🎓 Dicas Finais

1. **Comece pela Task 1** - É a base de tudo e já está pronta
2. **Teste localmente** antes de fazer deploy (quando possível)
3. **Use os scripts** `build-and-push.sh` - eles automatizam o processo
4. **Verifique os logs** sempre que algo não funcionar
5. **Consulte a documentação** em `docs/` quando tiver dúvidas

---

## ✨ Status do Projeto

```
✅ Task 1: Código implementado + ConfigMaps prontos
✅ Task 2: Dashboard implementado + Dockerfile pronto
✅ Task 3: Runtime implementado + Dockerfile pronto
✅ Documentação completa criada
✅ Scripts de automação preparados
✅ Seu ID já configurado em todos os lugares
```

**Você está pronto para começar! 🚀**

---

## 📞 Próximo Passo

Execute este comando para começar:

```bash
# Conectar na VM
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927

# Clonar/copiar o repositório se necessário
# Depois:
cd TP3_Cloud_Computing_UFMG/task1
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
kubectl apply -f serverless-deployment-course.yaml
```

**Boa sorte! 🍀**

