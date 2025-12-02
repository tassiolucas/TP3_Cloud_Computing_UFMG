#!/usr/bin/env python3
"""
Script de teste para verificar conexão com Redis e validar dados.

Este script permite testar a conexão com o Redis da VM e visualizar
os dados de entrada e saída da função serverless.
"""

import json
import sys

try:
    import redis
except ImportError:
    print("❌ Módulo 'redis' não encontrado!")
    print("   Instale com: pip install redis")
    sys.exit(1)


def test_redis_connection():
    """Testa conexão com o servidor Redis."""
    
    REDIS_HOST = '67.159.94.11'
    REDIS_PORT = 6379
    
    print("=" * 60)
    print("  Teste de Conexão Redis - TP3")
    print("=" * 60)
    print()
    print(f"🔌 Conectando ao Redis...")
    print(f"   Host: {REDIS_HOST}")
    print(f"   Port: {REDIS_PORT}")
    print()
    
    try:
        # Conectar ao Redis
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True  # Decodificar bytes para strings
        )
        
        # Testar conexão
        r.ping()
        print("✅ Conexão estabelecida com sucesso!")
        print()
        
        return r
        
    except redis.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        print()
        print("💡 Dicas:")
        print("   - Verifique se você tem acesso à VM")
        print("   - Verifique se o firewall permite conexões na porta 6379")
        print("   - Tente fazer SSH tunnel: ssh -L 6379:localhost:6379 user@vm")
        print()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        sys.exit(1)


def show_input_metrics(r):
    """Mostra as métricas de entrada (coletadas pelo sistema)."""
    
    print("-" * 60)
    print("📥 DADOS DE ENTRADA (metrics)")
    print("-" * 60)
    print()
    
    try:
        data = r.get('metrics')
        
        if data is None:
            print("⚠️  Nenhum dado encontrado na chave 'metrics'")
            print("   O coletor de métricas pode não estar rodando.")
            return
        
        metrics = json.loads(data)
        
        print(f"🕐 Timestamp: {metrics.get('timestamp', 'N/A')}")
        print()
        
        # CPUs
        cpu_keys = [k for k in metrics.keys() if k.startswith('cpu_percent-')]
        if cpu_keys:
            print("💻 CPUs:")
            for cpu_key in sorted(cpu_keys):
                cpu_id = cpu_key.replace('cpu_percent-', '')
                cpu_val = metrics[cpu_key]
                print(f"   CPU {cpu_id}: {cpu_val:.1f}%")
            print()
        
        # Memória
        mem_total = metrics.get('virtual_memory-total', 0)
        mem_used = metrics.get('virtual_memory-used', 0)
        mem_percent = metrics.get('virtual_memory-percent', 0)
        mem_cached = metrics.get('virtual_memory-cached', 0)
        mem_buffers = metrics.get('virtual_memory-buffers', 0)
        
        print("💾 Memória:")
        print(f"   Total: {mem_total / (1024**3):.2f} GB")
        print(f"   Usada: {mem_used / (1024**3):.2f} GB ({mem_percent:.1f}%)")
        print(f"   Cache: {mem_cached / (1024**3):.2f} GB")
        print(f"   Buffers: {mem_buffers / (1024**3):.2f} GB")
        print()
        
        # Rede
        bytes_sent = metrics.get('net_io_counters_eth0-bytes_sent1', 0)
        bytes_recv = metrics.get('net_io_counters_eth0-bytes_recv1', 0)
        
        print("🌐 Rede:")
        print(f"   Enviados: {bytes_sent / (1024**2):.2f} MB")
        print(f"   Recebidos: {bytes_recv / (1024**2):.2f} MB")
        print()
        
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON dos dados de entrada")
    except Exception as e:
        print(f"❌ Erro ao processar dados: {e}")


def show_output_metrics(r, output_key):
    """Mostra as métricas de saída (processadas pela função)."""
    
    print("-" * 60)
    print(f"📤 DADOS DE SAÍDA ({output_key})")
    print("-" * 60)
    print()
    
    try:
        data = r.get(output_key)
        
        if data is None:
            print(f"⚠️  Nenhum dado encontrado na chave '{output_key}'")
            print("   Sua função serverless pode não estar rodando ainda.")
            print()
            print("💡 Verifique:")
            print("   1. Os ConfigMaps foram aplicados?")
            print("   2. O deployment está rodando? (kubectl get pods)")
            print("   3. Há erros nos logs? (kubectl logs <pod-name>)")
            return
        
        results = json.loads(data)
        
        print(f"🕐 Timestamp: {results.get('timestamp', 'N/A')}")
        print()
        
        # Métricas calculadas
        print("📊 Métricas Calculadas:")
        print(f"   🌐 Tráfego de Saída: {results.get('percent-network-egress', 0):.2f}%")
        print(f"   💾 Memória em Cache: {results.get('percent-memory-cache', 0):.2f}%")
        print()
        
        # Médias móveis de CPU
        cpu_keys = [k for k in results.keys() if k.startswith('avg-util-cpu')]
        if cpu_keys:
            print("💻 Médias Móveis de CPU (60s):")
            for cpu_key in sorted(cpu_keys):
                cpu_val = results[cpu_key]
                print(f"   {cpu_key}: {cpu_val:.2f}%")
            print()
        
        # Info adicional
        num_cpus = results.get('num_cpus_monitored', 0)
        print(f"ℹ️  CPUs monitoradas: {num_cpus}")
        print()
        
    except json.JSONDecodeError:
        print("❌ Erro ao decodificar JSON dos dados de saída")
    except Exception as e:
        print(f"❌ Erro ao processar dados: {e}")


def list_all_keys(r):
    """Lista todas as chaves disponíveis no Redis."""
    
    print("-" * 60)
    print("🔑 CHAVES DISPONÍVEIS NO REDIS")
    print("-" * 60)
    print()
    
    try:
        # Buscar chaves relacionadas ao projeto
        proj_keys = r.keys('*proj3*')
        metric_keys = r.keys('metrics*')
        
        all_keys = set(proj_keys + metric_keys)
        
        if not all_keys:
            print("⚠️  Nenhuma chave relacionada ao projeto encontrada")
        else:
            for key in sorted(all_keys):
                memory = r.memory_usage(key)
                memory_str = f"{memory} bytes" if memory else "N/A"
                print(f"   📝 {key} ({memory_str})")
        print()
        
    except Exception as e:
        print(f"❌ Erro ao listar chaves: {e}")


def main():
    """Função principal."""
    
    # Conectar ao Redis
    r = test_redis_connection()
    
    # Mostrar métricas de entrada
    show_input_metrics(r)
    
    # Perguntar pelo output key do estudante
    print("=" * 60)
    output_key = input("Digite sua chave de saída (ex: ifs4-proj3-output): ").strip()
    print()
    
    if output_key:
        show_output_metrics(r, output_key)
    
    # Listar todas as chaves
    list_all_keys(r)
    
    print("=" * 60)
    print("✨ Teste concluído!")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(0)

