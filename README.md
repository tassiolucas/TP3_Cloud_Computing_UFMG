# TP3 - Serverless Computing e Dashboard de Monitoramento

**Aluno:** Tássio Almeida  
**ID:** 2025720437  
**Disciplina:** Cloud Computing - Mestrado UFMG

---

## 📂 Estrutura do Projeto

```
TP3_Cloud_Computing_UFMG/
├── task1/              # Função Serverless
├── task2/              # Dashboard de Monitoramento  
├── task3/              # Runtime Customizado
└── RELATORIO_TP3.md    # 📄 Relatório completo (Tasks 1 e 2)
```

---

## 🚀 Quick Start

### 🔐 Conectar na VM

```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

### ✅ Task 1: Deploy da Função Serverless

```bash
cd TP3_Cloud_Computing_UFMG/task1
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
kubectl apply -f serverless-deployment-course.yaml

# Verificar
kubectl get pods
kubectl logs -f <pod-name>
```

### 📊 Task 2: Acessar Dashboard

```bash
# Criar túnel SSH (na sua máquina local)
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:30600 tassioalmeida@pugna.snes.2advanced.dev -p 51927

# Abrir no navegador
open http://localhost:8501
```

---

## 📝 Informações do Sistema

### Redis
- **IP (containers):** `192.168.121.171:6379`
- **Chave Input:** `metrics`
- **Chave Output:** `2025720437-proj3-output`

### Kubernetes
- **Dashboard NodePort:** `30600`
- **Porta cálculo:** DevOps (30500) + 100 = 30600

### Docker Hub
- **Dashboard:** `tassiolucas/tp3-dashboard:v1`

---

## 📋 Status das Tasks

- ✅ **Task 1:** Implementada e deployada
- ✅ **Task 2:** Implementada e deployada
- ⏳ **Task 3:** Implementada (pendente teste)

---

## 🆘 Comandos Úteis

```bash
# Ver pods
kubectl get pods

# Ver logs
kubectl logs -f <pod-name>

# Ver services
kubectl get services

# Restart pod
kubectl delete pod <pod-name>
```

---

## 📄 Documentação Completa

Para relatório técnico detalhado, veja: **[RELATORIO_TP3.md](RELATORIO_TP3.md)**

Contém:
- ✅ Explicação da média móvel com `context.env`
- ✅ Implementação do dashboard
- ✅ Desafios e soluções
- ✅ Screenshots (marcados para inserir)
- ✅ Referências

---

## 🎯 Próximos Passos

1. Inserir prints no `RELATORIO_TP3.md`
2. Converter para PDF
3. Entregar!

**Dúvidas?** Veja o [RELATORIO_TP3.md](RELATORIO_TP3.md) completo.
