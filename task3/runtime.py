#!/usr/bin/env python3
"""
Runtime Serverless Customizado - TP3 Cloud Computing UFMG

Este runtime substitui lucasmsp/serverless:redis com funcionalidades adicionais:
1. Chave Redis de entrada configurável
2. Período de monitoramento configurável
3. Suporte a funções complexas (ZIP)
4. Handler configurável

Autor: [SEU NOME]
ID: [SEU ID]
"""

import redis
import json
import time
import os
import sys
import importlib.util
import zipfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import requests


# ============================================================================
# CONFIGURAÇÕES DO RUNTIME (via variáveis de ambiente)
# ============================================================================

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_INPUT_KEY = os.getenv('REDIS_INPUT_KEY', 'metrics')
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', 'output')
MONITORING_PERIOD = int(os.getenv('MONITORING_PERIOD', 5))
HANDLER_FUNCTION = os.getenv('HANDLER_FUNCTION', 'handler_module.handler')
ZIP_URL = os.getenv('ZIP_URL', None)
PYFILE_PATH = os.getenv('PYFILE_PATH', '/app/pyfile/pyfile')


# ============================================================================
# CLASSE DE CONTEXTO
# ============================================================================

class Context:
    """
    Contexto passado para a função handler do usuário.
    Contém metadados sobre o runtime e estado persistente.
    """
    
    def __init__(self):
        self.host = REDIS_HOST
        self.port = REDIS_PORT
        self.input_key = REDIS_INPUT_KEY
        self.output_key = REDIS_OUTPUT_KEY
        self.function_getmtime = None
        self.last_execution = None
        self.env = {}  # Estado persistente entre execuções
    
    def __repr__(self):
        return f"Context(host={self.host}, port={self.port}, input_key={self.input_key}, output_key={self.output_key})"


# ============================================================================
# CARREGAMENTO DE MÓDULOS
# ============================================================================

def download_and_extract_zip(url: str, extract_to: str) -> str:
    """
    Baixa e extrai um arquivo ZIP de uma URL.
    
    Args:
        url: URL do arquivo ZIP
        extract_to: Diretório onde extrair
    
    Returns:
        Caminho do diretório extraído
    """
    print(f"📦 Baixando ZIP de: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Salvar ZIP temporariamente
        zip_path = os.path.join(extract_to, 'function.zip')
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ ZIP baixado: {len(response.content)} bytes")
        
        # Extrair
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        print(f"✅ ZIP extraído em: {extract_to}")
        
        # Remover ZIP
        os.remove(zip_path)
        
        return extract_to
        
    except Exception as e:
        print(f"❌ Erro ao baixar/extrair ZIP: {e}")
        raise


def load_module_from_path(module_path: str, module_name: str = 'user_module'):
    """
    Carrega um módulo Python de um caminho específico.
    
    Args:
        module_path: Caminho para o arquivo .py
        module_name: Nome do módulo
    
    Returns:
        Módulo carregado
    """
    print(f"📥 Carregando módulo de: {module_path}")
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar módulo de {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    print(f"✅ Módulo carregado: {module_name}")
    
    return module


def load_user_function():
    """
    Carrega a função handler do usuário.
    
    Estratégia:
    1. Se ZIP_URL está definido, baixar e extrair ZIP
    2. Caso contrário, usar pyfile montado via ConfigMap
    3. Importar módulo e extrair função handler
    
    Returns:
        Função handler do usuário
    """
    
    # Diretório temporário para extração
    temp_dir = tempfile.mkdtemp(prefix='serverless_')
    
    try:
        # Caso 1: ZIP fornecido
        if ZIP_URL:
            print(f"🔧 Modo ZIP: {ZIP_URL}")
            extract_dir = download_and_extract_zip(ZIP_URL, temp_dir)
            
            # Adicionar ao sys.path para permitir imports
            sys.path.insert(0, extract_dir)
            
            # Parsear HANDLER_FUNCTION (formato: module.function)
            module_name, function_name = HANDLER_FUNCTION.rsplit('.', 1)
            
            # Encontrar arquivo .py principal
            module_file = None
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == f"{module_name}.py":
                        module_file = os.path.join(root, file)
                        break
                if module_file:
                    break
            
            if not module_file:
                raise FileNotFoundError(f"Módulo {module_name}.py não encontrado no ZIP")
            
            # Carregar módulo
            module = load_module_from_path(module_file, module_name)
            
        # Caso 2: pyfile montado
        else:
            print(f"🔧 Modo PYFILE: {PYFILE_PATH}")
            
            if not os.path.exists(PYFILE_PATH):
                raise FileNotFoundError(f"pyfile não encontrado em {PYFILE_PATH}")
            
            # Parsear HANDLER_FUNCTION
            module_name, function_name = HANDLER_FUNCTION.rsplit('.', 1)
            
            # Carregar módulo
            module = load_module_from_path(PYFILE_PATH, module_name)
        
        # Extrair função handler
        if not hasattr(module, function_name):
            raise AttributeError(f"Função '{function_name}' não encontrada no módulo")
        
        handler_func = getattr(module, function_name)
        
        print(f"✅ Função handler carregada: {HANDLER_FUNCTION}")
        
        return handler_func
        
    except Exception as e:
        print(f"❌ Erro ao carregar função: {e}")
        raise
    
    # Note: Não removemos temp_dir aqui pois o módulo precisa estar acessível


# ============================================================================
# RUNTIME PRINCIPAL
# ============================================================================

def check_data_changed(redis_client, last_data: dict, current_data: dict) -> bool:
    """
    Verifica se os dados mudaram desde a última execução.
    
    Args:
        redis_client: Cliente Redis
        last_data: Dados da última execução
        current_data: Dados atuais
    
    Returns:
        True se dados mudaram, False caso contrário
    """
    
    if last_data is None:
        return True
    
    # Comparar timestamps
    last_ts = last_data.get('timestamp', '')
    current_ts = current_data.get('timestamp', '')
    
    return last_ts != current_ts


def main():
    """
    Loop principal do runtime serverless.
    
    Fluxo:
    1. Conectar ao Redis
    2. Carregar função do usuário
    3. Loop infinito:
       a. Ler dados do Redis
       b. Verificar se mudaram
       c. Chamar handler
       d. Persistir context.env
       e. Salvar resultado no Redis
       f. Sleep(MONITORING_PERIOD)
    """
    
    print("=" * 80)
    print("🚀 Runtime Serverless Customizado - TP3")
    print("=" * 80)
    print(f"📍 Redis: {REDIS_HOST}:{REDIS_PORT}")
    print(f"📥 Input Key: {REDIS_INPUT_KEY}")
    print(f"📤 Output Key: {REDIS_OUTPUT_KEY}")
    print(f"⏱️  Monitoring Period: {MONITORING_PERIOD}s")
    print(f"🔧 Handler Function: {HANDLER_FUNCTION}")
    if ZIP_URL:
        print(f"📦 ZIP URL: {ZIP_URL}")
    print("=" * 80)
    
    # Conectar ao Redis
    print("\n🔌 Conectando ao Redis...")
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=10
        )
        redis_client.ping()
        print("✅ Conectado ao Redis com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar ao Redis: {e}")
        sys.exit(1)
    
    # Carregar função do usuário
    print("\n📚 Carregando função do usuário...")
    try:
        handler_function = load_user_function()
    except Exception as e:
        print(f"❌ Erro ao carregar função: {e}")
        sys.exit(1)
    
    # Criar contexto
    context = Context()
    
    # Estado
    last_data = None
    execution_count = 0
    
    print("\n✨ Runtime iniciado! Aguardando dados...\n")
    
    # Loop principal
    while True:
        try:
            # Ler dados do Redis
            raw_data = redis_client.get(REDIS_INPUT_KEY)
            
            if not raw_data:
                print(f"⏳ [{datetime.now().strftime('%H:%M:%S')}] Aguardando dados em '{REDIS_INPUT_KEY}'...")
                time.sleep(MONITORING_PERIOD)
                continue
            
            # Parse JSON
            try:
                current_data = json.loads(raw_data)
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao parsear JSON: {e}")
                time.sleep(MONITORING_PERIOD)
                continue
            
            # Verificar se dados mudaram
            if not check_data_changed(redis_client, last_data, current_data):
                # Dados não mudaram, skip
                time.sleep(MONITORING_PERIOD)
                continue
            
            # Dados mudaram, executar handler
            execution_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"▶️  [{timestamp}] Execução #{execution_count}: Chamando handler...")
            
            # Atualizar metadados do contexto
            context.last_execution = datetime.now().isoformat()
            
            # Chamar handler do usuário
            start_time = time.time()
            result = handler_function(current_data, context)
            elapsed_time = time.time() - start_time
            
            # Validar resultado
            if not isinstance(result, dict):
                print(f"⚠️  Aviso: Handler retornou {type(result)}, esperado dict")
                result = {'error': 'Handler deve retornar dict', 'result': str(result)}
            
            # Salvar resultado no Redis
            result_json = json.dumps(result)
            redis_client.set(REDIS_OUTPUT_KEY, result_json)
            
            print(f"✅ [{timestamp}] Execução concluída em {elapsed_time:.3f}s")
            print(f"   📊 Resultado: {len(result)} chaves | {len(result_json)} bytes")
            
            # Atualizar last_data
            last_data = current_data
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Runtime interrompido pelo usuário")
            break
            
        except Exception as e:
            print(f"❌ Erro durante execução: {e}")
            import traceback
            traceback.print_exc()
        
        # Aguardar próxima execução
        time.sleep(MONITORING_PERIOD)
    
    print("\n👋 Runtime encerrado")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    main()

