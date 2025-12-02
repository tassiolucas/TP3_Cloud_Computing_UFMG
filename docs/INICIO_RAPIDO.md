# 🚀 Guia de Início Rápido - TP3

Este guia vai te ajudar a começar rapidamente com o projeto.

---

## 📋 Pré-requisitos

Antes de começar, você precisa:

- [ ] Acesso SSH à VM (pugna.snes.dcc.ufmg.br:51927)
- [ ] kubectl configurado
- [ ] Docker instalado (para Task 2 e 3)
- [ ] Seu ID de estudante (ex: `ifs4`)
- [ ] Sua porta do DevOps (para calcular porta do dashboard)

---

## 🎯 PARTE 1: Task 1 (30 minutos)

### Passo 1: Configure seu ID
```bash
cd task1
```

Edite `configmap-outputkey.yaml`:
```yaml
data:
  REDIS_OUTPUT_KEY: "SEU-ID-proj3-output"  # Ex: ifs4-proj3-output
```

### Passo 2: Conecte na VM
```bash
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

### Passo 3: Aplique os ConfigMaps
```bash
# Dentro da VM
cd TP3_Cloud_Computing_UFMG/task1

kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
kubectl apply -f serverless-deployment-course.yaml
```

### Passo 4: Verifique
```bash
# Ver pods
kubectl get pods

# Ver logs (substitua <POD-NAME>)
kubectl logs -f <POD-NAME>

# Testar Redis
redis-cli -h 192.168.121.48 -p 6379 get SEU-ID-proj3-output
```

**✅ Sucesso**: Você deve ver JSON com métricas!

---

## 📊 PARTE 2: Task 2 (1-2 horas)

### Passo 1: Configure variáveis

Edite `task2/dashboard.py` linha 27:
```python
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', 'SEU-ID-proj3-output')
```

### Passo 2: Calcule sua porta
```
Porta Dashboard = Porta DevOps + 100
```

Exemplo: Se sua porta DevOps era `30500`, use `30600`

### Passo 3: Edite o Service

Edite `task2/dashboard-service.yaml`:
```yaml
spec:
  type: NodePort
  ports:
    - port: 8501
      targetPort: 8501
      nodePort: SUA_PORTA  # Ex: 30600
```

### Passo 4: Build da imagem

**Importante**: Substitua `seu-usuario` pelo seu usuário do Docker Hub!

```bash
cd task2

# Login no Docker Hub
docker login

# Build
docker build -t seu-usuario/tp3-dashboard:v1 .

# Testar localmente (opcional)
docker run -p 8501:8501 -e REDIS_HOST=192.168.121.48 -e REDIS_OUTPUT_KEY=SEU-ID-proj3-output seu-usuario/tp3-dashboard:v1

# Push
docker push seu-usuario/tp3-dashboard:v1
```

### Passo 5: Edite o Deployment

Edite `task2/dashboard-deployment.yaml`:
```yaml
spec:
  template:
    spec:
      containers:
      - name: dashboard
        image: seu-usuario/tp3-dashboard:v1  # ATUALIZAR AQUI
        env:
        - name: REDIS_HOST
          value: "192.168.121.48"
        - name: REDIS_PORT
          value: "6379"
        - name: REDIS_OUTPUT_KEY
          value: "SEU-ID-proj3-output"  # ATUALIZAR AQUI
```

### Passo 6: Deploy no Kubernetes

```bash
# Conectar na VM
ssh -i ~/.ssh/tassioUFMG tassioalmeida@pugna.snes.2advanced.dev -p 51927

cd TP3_Cloud_Computing_UFMG/task2

# Aplicar
kubectl apply -f dashboard-deployment.yaml
kubectl apply -f dashboard-service.yaml

# Verificar
kubectl get pods
kubectl get services
```

### Passo 7: Acesse o Dashboard

**Na sua máquina local**:
```bash
ssh -i ~/.ssh/tassioUFMG -L 8501:localhost:SUA_PORTA tassioalmeida@pugna.snes.2advanced.dev -p 51927
```

Abra no navegador: http://localhost:8501

**✅ Sucesso**: Você deve ver o dashboard com gráficos!

---

## ⚙️ PARTE 3: Task 3 (4-6 horas)

### Resumo do que fazer:

A Task 3 requer criar um runtime customizado do zero. Aqui está a estrutura:

```
task3/
├── runtime.py           # ⭐ Código principal
├── Dockerfile           # Container
├── requirements.txt     # Dependências
├── deployment.yaml      # Kubernetes
└── configmaps/          # Configurações
```

### Abordagem sugerida:

#### Fase 1: Runtime Básico (2-3 horas)
1. Criar `runtime.py` que:
   - Conecta ao Redis
   - Lê dados periodicamente
   - Carrega módulo Python do usuário
   - Chama `handler(input, context)`
   - Salva resultado no Redis

#### Fase 2: Adicionar Funcionalidades (2-3 horas)
2. Implementar features adicionais:
   - Chave Redis configurável
   - Período de monitoramento configurável
   - Suporte a ZIP
   - Handler configurável

#### Fase 3: Deploy e Teste (1 hora)
3. Build, push, deploy e testar

### Template do runtime.py

```python
#!/usr/bin/env python3
"""
Runtime Serverless Customizado - TP3
Substitui lucasmsp/serverless:redis com funcionalidades adicionais
"""

import redis
import json
import time
import os
import importlib.util
from datetime import datetime

# Ler configurações
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', 'metrics')
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', 'output')
MONITORING_PERIOD = int(os.getenv('MONITORING_PERIOD', 5))
HANDLER_FUNCTION = os.getenv('HANDLER_FUNCTION', 'handler_module.handler')

class Context:
    """Contexto passado para a função handler"""
    def __init__(self):
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.input_key = REDIS_INPUT_KEY
        self.output_key = REDIS_OUTPUT_KEY
        self.function_getmtime = None
        self.last_execution = None
        self.env = {}  # Estado persistente

def load_user_module():
    """Carrega o módulo Python do usuário"""
    # TODO: Implementar lógica de carregamento
    # 1. Tentar carregar de pyfile
    # 2. Se ZIP_URL existe, baixar e descompactar
    pass

def main():
    """Loop principal do runtime"""
    
    # Conectar ao Redis
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    
    # Carregar módulo do usuário
    handler = load_user_module()
    
    # Criar contexto
    context = Context()
    
    # Loop infinito
    while True:
        try:
            # Ler dados do Redis
            data = r.get(REDIS_INPUT_KEY)
            
            if data:
                # Parse JSON
                input_data = json.loads(data)
                
                # Chamar handler
                result = handler(input_data, context)
                
                # Salvar resultado
                r.set(REDIS_OUTPUT_KEY, json.dumps(result))
                
                # Atualizar last_execution
                context.last_execution = datetime.now().isoformat()
                
                print(f"✅ Executado em {context.last_execution}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Aguardar próxima execução
        time.sleep(MONITORING_PERIOD)

if __name__ == '__main__':
    main()
```

**Dica**: Use este template como base e vá implementando cada parte!

---

## 📝 Checklist Final

### Task 1
- [ ] ConfigMaps aplicados
- [ ] Pod rodando
- [ ] Dados no Redis
- [ ] PDF com explicação da média móvel

### Task 2
- [ ] Imagem Docker criada e pushed
- [ ] Deployment aplicado
- [ ] Service exposto na porta correta
- [ ] Dashboard acessível
- [ ] PDF com screenshots

### Task 3
- [ ] Runtime implementado
- [ ] Dockerfile criado
- [ ] Funcionalidades adicionais implementadas
- [ ] Compatível com Task 1
- [ ] PDF com documentação técnica

---

## 🆘 Problemas Comuns

### "Connection refused" no Redis
**Solução**: Use IP `192.168.121.48` dentro dos pods, não `localhost`

### Pod em CrashLoopBackOff
```bash
kubectl logs <pod-name>
kubectl describe pod <pod-name>
```

### Imagem não puxa
```bash
# Verificar se fez push
docker images

# Tentar push novamente
docker push seu-usuario/tp3-dashboard:v1
```

### Dashboard não mostra dados
1. Verificar se Task 1 está rodando
2. Verificar REDIS_OUTPUT_KEY está correto
3. Ver logs: `kubectl logs <dashboard-pod>`

---

## 📞 Onde Pedir Ajuda

1. **Documentação completa**: Veja `docs/PLANO_DE_EXECUCAO.md`
2. **Task 1 detalhada**: Veja `docs/TASK1_DOCUMENTACAO.md`
3. **Redis**: Veja `scripts/test_redis_connection.py`

---

## 🎯 Ordem Recomendada

1. ✅ **Task 1** → Mais simples, base para as outras
2. ✅ **Task 2** → Médio, requer Docker
3. ⏳ **Task 3** → Mais complexa, precisa entender runtime

**Boa sorte! 🚀**

