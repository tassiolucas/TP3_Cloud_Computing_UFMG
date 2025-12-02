"""
Módulo serverless para processamento de métricas de recursos do sistema.

Este módulo implementa uma função handler que processa dados de monitoramento
de CPU, memória e rede, calculando:
- Porcentagem de tráfego de saída de rede
- Porcentagem de memória em cache
- Média móvel de utilização de CPU nos últimos 60 segundos
"""

from typing import Any, Dict, List
import json


def handler(input: dict, context: object) -> Dict[str, Any]:
    """
    Função handler para processar métricas de recursos do sistema.
    
    Args:
        input: Dicionário contendo métricas coletadas do sistema (CPU, memória, rede)
        context: Objeto de contexto contendo informações de ambiente e estado persistente
        
    Returns:
        Dicionário JSON-encodable com as métricas calculadas
    """
    
    # Inicializar dicionário de resultados
    results = {}
    
    # ========================================================================
    # 1. CALCULAR PORCENTAGEM DE TRÁFEGO DE SAÍDA DE REDE
    # ========================================================================
    bytes_sent = input.get('net_io_counters_eth0-bytes_sent1', 0)
    bytes_recv = input.get('net_io_counters_eth0-bytes_recv1', 0)
    
    total_bytes = bytes_sent + bytes_recv
    
    if total_bytes > 0:
        percent_egress = (bytes_sent / total_bytes) * 100.0
    else:
        percent_egress = 0.0
    
    results['percent-network-egress'] = round(percent_egress, 2)
    
    # ========================================================================
    # 2. CALCULAR PORCENTAGEM DE MEMÓRIA EM CACHE
    # ========================================================================
    memory_total = input.get('virtual_memory-total', 1)  # Evitar divisão por zero
    memory_cached = input.get('virtual_memory-cached', 0)
    memory_buffers = input.get('virtual_memory-buffers', 0)
    
    # Memória em cache = cached + buffers
    memory_cache_total = memory_cached + memory_buffers
    percent_memory_cache = (memory_cache_total / memory_total) * 100.0
    
    results['percent-memory-cache'] = round(percent_memory_cache, 2)
    
    # ========================================================================
    # 3. CALCULAR MÉDIA MÓVEL DE UTILIZAÇÃO DE CPU (últimos 60 segundos)
    # ========================================================================
    
    # Inicializar estado persistente se não existir
    if not hasattr(context, 'env'):
        context.env = {}
    
    if 'cpu_history' not in context.env:
        context.env['cpu_history'] = {}
    
    # Identificar todas as CPUs no input
    cpu_keys = [key for key in input.keys() if key.startswith('cpu_percent-')]
    
    # Coletor de métricas a cada 5 segundos
    # Para média móvel de 60 segundos, precisamos dos últimos 12 valores (60/5 = 12)
    WINDOW_SIZE = 12
    
    for cpu_key in cpu_keys:
        cpu_value = input.get(cpu_key, 0.0)
        
        # Extrair identificador da CPU (ex: 'cpu_percent-0' -> '0')
        cpu_id = cpu_key.replace('cpu_percent-', '')
        
        # Inicializar histórico para esta CPU se não existir
        if cpu_id not in context.env['cpu_history']:
            context.env['cpu_history'][cpu_id] = []
        
        # Adicionar valor atual ao histórico
        context.env['cpu_history'][cpu_id].append(cpu_value)
        
        # Manter apenas os últimos WINDOW_SIZE valores
        if len(context.env['cpu_history'][cpu_id]) > WINDOW_SIZE:
            context.env['cpu_history'][cpu_id] = context.env['cpu_history'][cpu_id][-WINDOW_SIZE:]
        
        # Calcular média móvel
        cpu_history = context.env['cpu_history'][cpu_id]
        avg_cpu_util = sum(cpu_history) / len(cpu_history)
        
        # Adicionar ao resultado
        results[f'avg-util-cpu{cpu_id}-60sec'] = round(avg_cpu_util, 2)
    
    # ========================================================================
    # INFORMAÇÕES ADICIONAIS (opcional, mas útil para debug)
    # ========================================================================
    results['timestamp'] = input.get('timestamp', 'unknown')
    results['num_cpus_monitored'] = len(cpu_keys)
    
    return results


# Função auxiliar para testar localmente (opcional)
def _test_handler():
    """
    Função de teste local para validar o handler sem precisar do runtime completo.
    """
    
    # Simular dados de input
    test_input = {
        'timestamp': '2025-11-23T10:30:00',
        'cpu_percent-0': 45.5,
        'cpu_percent-1': 32.1,
        'cpu_percent-2': 67.8,
        'cpu_percent-3': 21.4,
        'net_io_counters_eth0-bytes_sent1': 1024000,
        'net_io_counters_eth0-bytes_recv1': 4096000,
        'virtual_memory-total': 16000000000,
        'virtual_memory-cached': 2000000000,
        'virtual_memory-buffers': 500000000,
    }
    
    # Simular contexto
    class TestContext:
        def __init__(self):
            self.env = {}
            self.host = 'localhost'
            self.port = 6379
            self.input_key = 'metrics'
            self.output_key = 'test-output'
    
    context = TestContext()
    
    # Executar handler várias vezes para testar média móvel
    print("Testando handler com múltiplas execuções...")
    for i in range(15):
        # Variar os valores de CPU
        test_input['cpu_percent-0'] = 45.5 + i
        test_input['cpu_percent-1'] = 32.1 + i * 0.5
        test_input['cpu_percent-2'] = 67.8 - i * 0.3
        test_input['cpu_percent-3'] = 21.4 + i * 0.8
        
        result = handler(test_input, context)
        print(f"\n=== Execução {i+1} ===")
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    _test_handler()

