# Task 1 - Documentação da Implementação

## Aluno
**Nome:** [SEU NOME AQUI]  
**ID:** [SEU ID AQUI]

---

## Sumário Executivo

Este documento descreve a implementação da função serverless para processamento de métricas de recursos do sistema, conforme especificado na Task 1 do Projeto 3. A solução implementa o cálculo de três métricas principais:

1. **Porcentagem de tráfego de saída de rede**
2. **Porcentagem de memória em cache**
3. **Média móvel de utilização de CPU** nos últimos 60 segundos

---

## Abordagem para Manutenção de Estado - Média Móvel de CPU

### Problema

A função serverless deve calcular a média móvel da utilização de cada CPU nos últimos 60 segundos. Como as medições chegam a cada 5 segundos, é necessário manter um histórico dos últimos 12 valores (60 segundos ÷ 5 segundos/medição = 12 medições) para cada CPU.

O desafio é que funções serverless são, por definição, **stateless** (sem estado). Cada invocação é independente e não mantém dados em memória entre execuções.

### Solução Implementada

Para resolver este problema, utilizamos o objeto `context.env` fornecido pelo runtime serverless. Este objeto é especialmente projetado para persistir pequenas quantidades de dados entre múltiplas invocações da função.

#### Estrutura de Dados

Implementamos a seguinte estrutura de dados em `context.env`:

```python
context.env = {
    'cpu_history': {
        '0': [45.5, 46.3, 47.1, ...],  # Histórico CPU 0
        '1': [32.1, 32.8, 33.2, ...],  # Histórico CPU 1
        '2': [67.8, 66.9, 65.4, ...],  # Histórico CPU 2
        ...
    }
}
```

Cada chave em `cpu_history` representa uma CPU (identificada por seu número), e o valor é uma **lista** contendo os últimos valores de utilização.

#### Algoritmo de Janela Deslizante (Sliding Window)

A implementação utiliza um algoritmo de **janela deslizante de tamanho fixo**:

1. **Inicialização**: Na primeira execução, verificamos se `cpu_history` existe em `context.env`. Se não existir, criamos a estrutura.

2. **Adição de novo valor**: A cada nova medição, adicionamos o valor atual ao final da lista correspondente à CPU:
   ```python
   context.env['cpu_history'][cpu_id].append(cpu_value)
   ```

3. **Manutenção do tamanho da janela**: Mantemos apenas os últimos 12 valores. Se a lista ultrapassar esse limite, removemos os valores mais antigos:
   ```python
   if len(context.env['cpu_history'][cpu_id]) > WINDOW_SIZE:
       context.env['cpu_history'][cpu_id] = context.env['cpu_history'][cpu_id][-WINDOW_SIZE:]
   ```

4. **Cálculo da média**: Calculamos a média aritmética simples dos valores na janela:
   ```python
   avg_cpu_util = sum(cpu_history) / len(cpu_history)
   ```

#### Comportamento Durante o Warm-up

Durante as primeiras execuções (período de "aquecimento"), a janela ainda não está completa:

- **Execução 1**: Janela tem 1 valor → média de 1 valor
- **Execução 2**: Janela tem 2 valores → média de 2 valores
- ...
- **Execução 12**: Janela tem 12 valores → média de 12 valores (janela completa)
- **Execução 13+**: Janela sempre tem 12 valores → média móvel estabilizada

Esta abordagem garante que a função sempre retorna um resultado válido, mesmo antes da janela estar completamente preenchida.

### Vantagens da Abordagem

1. **Eficiência de Memória**: Mantemos apenas os dados necessários (12 valores por CPU)
2. **Simplicidade**: Implementação direta e fácil de entender
3. **Escalabilidade**: Funciona com qualquer número de CPUs (detecção dinâmica)
4. **Sem Dependências Externas**: Não requer acesso a banco de dados ou Redis para manter o estado
5. **Tempo Constante**: Operações de adição e cálculo têm complexidade O(1) e O(n) respectivamente, onde n=12 (constante)

### Alternativas Consideradas

Outras abordagens foram consideradas mas não implementadas:

1. **Armazenamento em Redis**: Funcionaria, mas adicionaria latência de rede a cada invocação
2. **Média Móvel Exponencial (EMA)**: Mais eficiente em memória (guarda apenas um valor), mas menos intuitiva e pode ser menos precisa
3. **Buffer Circular**: Mesma complexidade, mas implementação mais complexa sem benefícios significativos

---

## Métricas Calculadas

### 1. Porcentagem de Tráfego de Saída de Rede

**Fórmula:**
```
percent_egress = (bytes_sent / (bytes_sent + bytes_recv)) × 100
```

**Chave de saída:** `percent-network-egress`

### 2. Porcentagem de Memória em Cache

**Fórmula:**
```
percent_cache = ((cached + buffers) / total_memory) × 100
```

**Chave de saída:** `percent-memory-cache`

### 3. Média Móvel de CPU

**Fórmula:**
```
avg_cpu = Σ(últimos_12_valores) / 12
```

**Chaves de saída:** `avg-util-cpu0-60sec`, `avg-util-cpu1-60sec`, etc.

---

## Estrutura de Saída

A função retorna um dicionário JSON com a seguinte estrutura:

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

---

## Instruções de Deploy

### Passo 1: Editar o ConfigMap de Output Key

Edite o arquivo `configmap-outputkey.yaml` e substitua `seu-id` pelo seu ID de estudante:

```yaml
REDIS_OUTPUT_KEY: "seu-id-proj3-output"
```

### Passo 2: Aplicar os ConfigMaps

```bash
kubectl apply -f configmap-pyfile.yaml
kubectl apply -f configmap-outputkey.yaml
```

### Passo 3: Aplicar o Deployment

```bash
kubectl apply -f deployment.yaml
```

### Passo 4: Verificar o Status

```bash
# Verificar pods
kubectl get pods

# Verificar logs
kubectl logs -f <nome-do-pod>

# Verificar no Redis (da VM)
redis-cli -h 67.159.94.11 -p 6379 get seu-id-proj3-output
```

---

## Testes Realizados

A função inclui uma função de teste `_test_handler()` que pode ser executada localmente:

```bash
python handler_module.py
```

Esta função simula 15 execuções consecutivas com valores variados de CPU para validar o comportamento da média móvel.

---

## Conclusão

A implementação apresentada atende a todos os requisitos da Task 1:

✅ Calcula porcentagem de tráfego de saída de rede  
✅ Calcula porcentagem de memória em cache  
✅ Calcula média móvel de CPU nos últimos 60 segundos  
✅ Mantém estado entre invocações usando `context.env`  
✅ Retorna dicionário JSON-encodable  
✅ Funciona com qualquer número de CPUs (dinâmico)  
✅ Código documentado e testável  

A solução é robusta, eficiente e pronta para deploy em ambiente de produção.

---

**Data:** 23 de Novembro de 2025  
**Versão:** 1.0

