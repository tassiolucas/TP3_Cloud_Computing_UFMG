# 🚀 Guia Rápido - Task 1

## ✅ O que foi implementado?

Implementação completa da **Task 1** do TP3, incluindo:

- ✅ Função `handler()` que processa métricas de sistema
- ✅ Cálculo de porcentagem de tráfego de saída de rede
- ✅ Cálculo de porcentagem de memória em cache
- ✅ Média móvel de utilização de CPU (últimos 60 segundos)
- ✅ Persistência de estado usando `context.env`
- ✅ ConfigMaps Kubernetes prontos para deploy
- ✅ Documentação completa
- ✅ Scripts de teste e deploy

## 📁 Arquivos Criados

```
TP3/
├── handler_module.py              # ⭐ Função serverless principal
├── configmap-pyfile.yaml          # ConfigMap com o código Python
├── configmap-outputkey.yaml       # ConfigMap com chave Redis
├── TASK1_DOCUMENTACAO.md          # 📄 Documentação técnica detalhada
├── README.md                      # Visão geral do projeto
├── GUIA_RAPIDO.md                 # Este arquivo
├── deploy-task1.sh                # 🔧 Script de deploy automático
└── test_redis_connection.py       # 🧪 Script de teste Redis
```

## 🎯 Deploy em 4 Passos

### Passo 0: Conectar à VM

```bash
# Configurar SSH (primeira vez)
./setup-ssh.sh seu-usuario

# Conectar
ssh cloud2

# Transferir arquivos para a VM
scp *.yaml cloud2:~/TP3/
```

### Método 1: Script Automático (Recomendado)

```bash
# 1. Tornar o script executável (já feito)
chmod +x deploy-task1.sh

# 2. Executar o script com seu ID
./deploy-task1.sh seu-id-estudante

# Exemplo:
./deploy-task1.sh ifs4
```

### Método 2: Manual

```bash
# 1. Editar configmap-outputkey.yaml
# Substituir 'seu-id' pelo seu ID de estudante

# 2. Aplicar ConfigMaps
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml

# 3. Aplicar deployment (fornecido pelos instrutores)
kubectl apply -f deployment.yaml
```

## 🧪 Testar a Implementação

### Teste Local (Sem Kubernetes)

```bash
# Testar a função handler localmente
python handler_module.py
```

### Teste de Conexão Redis

```bash
# Verificar conexão e visualizar dados
python test_redis_connection.py
```

### Teste no Kubernetes

```bash
# 1. Verificar pods
kubectl get pods

# 2. Ver logs do pod
kubectl logs -f <nome-do-pod>

# 3. Verificar dados no Redis
redis-cli -h 67.159.94.11 -p 6379 get seu-id-proj3-output
```

## 📊 Exemplo de Saída

Sua função retornará algo como:

```json
{
  "percent-network-egress": 20.0,
  "percent-memory-cache": 15.62,
  "avg-util-cpu0-60sec": 45.5,
  "avg-util-cpu1-60sec": 32.1,
  "avg-util-cpu2-60sec": 67.8,
  "avg-util-cpu3-60sec": 21.4,
  "timestamp": "2025-11-23T10:30:00",
  "num_cpus_monitored": 4
}
```

## ❓ Troubleshooting

### Problema: Pod não inicia

```bash
# Verificar eventos
kubectl describe pod <nome-do-pod>

# Verificar se ConfigMaps existem
kubectl get configmaps
```

### Problema: Função não retorna dados

```bash
# Ver logs detalhados
kubectl logs <nome-do-pod> --previous

# Verificar se métricas estão chegando no Redis
redis-cli -h 67.159.94.11 -p 6379 get metrics
```

### Problema: Erro de conexão Redis

```bash
# Criar SSH tunnel se necessário
ssh -L 6379:localhost:6379 usuario@vm
```

## 📝 Checklist de Entrega

Para entregar a Task 1, você precisa:

- [ ] `handler_module.py` - Código fonte do módulo
- [ ] `configmap-pyfile.yaml` - ConfigMap com código
- [ ] `configmap-outputkey.yaml` - ConfigMap com output key
- [ ] `TASK1_DOCUMENTACAO.md` - Documentação em PDF/Markdown
  - Explicação da abordagem de média móvel
  - Como o estado é mantido
  - Estrutura de dados utilizada

## 🎓 Conceitos Implementados

### 1. Computação Serverless
- Função stateless que processa eventos
- Recebe input, processa, retorna output
- Runtime gerencia ciclo de vida

### 2. Média Móvel (Sliding Window)
- Janela deslizante de 12 valores (60 segundos)
- Estado persistido em `context.env`
- Algoritmo O(1) para inserção

### 3. Kubernetes ConfigMaps
- Injeção de código via volume mount
- Variáveis de ambiente para configuração
- Separação de código e configuração

## 📚 Próximos Passos

Após completar a Task 1:

1. **Task 2**: Implementar dashboard de monitoramento
   - Escolher framework (Plotly Dash, Streamlit, etc)
   - Ler dados do Redis
   - Criar visualizações
   - Deploy no Kubernetes

2. **Task 3**: Criar runtime serverless customizado
   - Substituir `lucasmsp/serverless:redis`
   - Adicionar funcionalidades extras
   - Suporte a funções multi-arquivo (ZIP)

## 💡 Dicas Importantes

1. **Sempre teste localmente primeiro** antes de fazer deploy
2. **Verifique os logs** se algo não funcionar
3. **Use o script de teste Redis** para debug
4. **Mantenha o output key único** para evitar conflitos
5. **Leia a documentação técnica** para entender os detalhes

## 🆘 Precisa de Ajuda?

- 📖 Leia `TASK1_DOCUMENTACAO.md` para detalhes técnicos
- 🧪 Use `test_redis_connection.py` para debug
- 📝 Consulte o `README.md` para visão geral

---

**Boa sorte com o projeto! 🎉**

