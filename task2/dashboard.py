"""
Dashboard de Monitoramento para TP3
Visualiza métricas de CPU, memória e rede processadas pela função serverless.
"""

import streamlit as st
import redis
import json
import time
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="TP3 - Monitor de Recursos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações Redis (podem ser sobrescritas por variáveis de ambiente)
import os
REDIS_HOST = os.getenv('REDIS_HOST', '192.168.121.171')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_OUTPUT_KEY = os.getenv('REDIS_OUTPUT_KEY', '2025720437-proj3-output')
REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', 5))  # segundos


@st.cache_resource
def get_redis_connection():
    """Cria e retorna conexão com Redis."""
    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=5
        )
        r.ping()
        return r
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Redis: {e}")
        return None


def fetch_metrics(redis_conn):
    """Busca métricas do Redis."""
    try:
        data = redis_conn.get(REDIS_OUTPUT_KEY)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        st.error(f"❌ Erro ao buscar métricas: {e}")
        return None


def fetch_raw_metrics(redis_conn):
    """Busca métricas brutas (input) do Redis."""
    try:
        data = redis_conn.get('metrics')
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        return None


def create_cpu_gauge(cpu_id, value):
    """Cria gauge para uma CPU."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': f"CPU {cpu_id}"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def create_percentage_chart(title, value, color):
    """Cria gráfico de barra para porcentagens."""
    fig = go.Figure(go.Bar(
        x=[value],
        y=[title],
        orientation='h',
        marker=dict(color=color),
        text=[f"{value:.2f}%"],
        textposition='inside',
        textfont=dict(size=16, color='white')
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 100], title="Porcentagem (%)"),
        height=150,
        margin=dict(l=20, r=20, t=40, b=40),
        title=title,
        showlegend=False
    )
    return fig


def create_cpu_history_chart(cpu_histories):
    """Cria gráfico de linha com histórico de todas as CPUs."""
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, (cpu_id, history) in enumerate(cpu_histories.items()):
        if history:
            x = list(range(len(history)))
            fig.add_trace(go.Scatter(
                x=x,
                y=history,
                mode='lines+markers',
                name=f'CPU {cpu_id}',
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Histórico de Utilização de CPU (últimos 60 segundos)",
        xaxis_title="Medições (5s cada)",
        yaxis_title="Utilização (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        margin=dict(l=60, r=20, t=60, b=60),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def main():
    """Função principal do dashboard."""
    
    # Header
    st.title("📊 TP3 - Dashboard de Monitoramento de Recursos")
    st.markdown("---")
    
    # Sidebar com configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        st.info(f"""
        **Redis Server:**
        - Host: `{REDIS_HOST}`
        - Port: `{REDIS_PORT}`
        - Key: `{REDIS_OUTPUT_KEY}`
        """)
        
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        if auto_refresh:
            st.info(f"Atualizando a cada {REFRESH_INTERVAL}s")
        
        st.markdown("---")
        st.markdown("### 📖 Sobre")
        st.markdown("""
        Este dashboard visualiza métricas de recursos processadas pela função serverless:
        - **CPU:** Média móvel (60s)
        - **Memória:** % em cache
        - **Rede:** % tráfego de saída
        """)
    
    # Conectar ao Redis
    redis_conn = get_redis_connection()
    if not redis_conn:
        st.error("⚠️ Não foi possível conectar ao Redis. Verifique a configuração.")
        return
    
    # Placeholder para auto-refresh
    placeholder = st.empty()
    
    # Loop principal
    while True:
        with placeholder.container():
            # Buscar métricas
            metrics = fetch_metrics(redis_conn)
            raw_metrics = fetch_raw_metrics(redis_conn)
            
            if not metrics:
                st.warning("⚠️ Nenhuma métrica disponível ainda. Aguardando dados...")
                st.info("Certifique-se de que a função serverless está rodando e processando métricas.")
            else:
                # Status e timestamp
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.metric("📅 Timestamp", metrics.get('timestamp', 'N/A'))
                with col2:
                    st.metric("💻 CPUs Monitoradas", metrics.get('num_cpus_monitored', 0))
                with col3:
                    if raw_metrics:
                        mem_percent = raw_metrics.get('virtual_memory-percent', 0)
                        st.metric("💾 Memória Usada", f"{mem_percent:.1f}%")
                    else:
                        st.metric("💾 Memória Usada", "N/A")
                
                st.markdown("---")
                
                # Seção 1: Métricas Gerais
                st.header("📈 Métricas Gerais")
                col1, col2 = st.columns(2)
                
                with col1:
                    network_egress = metrics.get('percent-network-egress', 0)
                    fig = create_percentage_chart(
                        "🌐 Tráfego de Saída de Rede",
                        network_egress,
                        'steelblue'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    memory_cache = metrics.get('percent-memory-cache', 0)
                    fig = create_percentage_chart(
                        "💾 Memória em Cache",
                        memory_cache,
                        'mediumseagreen'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Seção 2: CPUs - Médias Móveis
                st.header("💻 Utilização de CPU (Média Móvel 60s)")
                
                # Extrair métricas de CPU
                cpu_metrics = {
                    key.replace('avg-util-cpu', '').replace('-60sec', ''): value
                    for key, value in metrics.items()
                    if key.startswith('avg-util-cpu')
                }
                
                if cpu_metrics:
                    # Criar gauges para cada CPU
                    num_cpus = len(cpu_metrics)
                    cols_per_row = 4
                    rows = (num_cpus + cols_per_row - 1) // cols_per_row
                    
                    for row in range(rows):
                        cols = st.columns(cols_per_row)
                        for col_idx in range(cols_per_row):
                            cpu_idx = row * cols_per_row + col_idx
                            if cpu_idx < num_cpus:
                                cpu_id = sorted(cpu_metrics.keys())[cpu_idx]
                                with cols[col_idx]:
                                    fig = create_cpu_gauge(cpu_id, cpu_metrics[cpu_id])
                                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Seção 3: Dados Brutos (Raw Metrics)
                if raw_metrics:
                    with st.expander("🔍 Ver Métricas Brutas (Dados de Entrada)", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("💻 CPU")
                            cpu_data = {
                                key: value for key, value in raw_metrics.items()
                                if key.startswith('cpu_percent-')
                            }
                            if cpu_data:
                                df = pd.DataFrame([
                                    {'CPU': key.replace('cpu_percent-', ''), 'Utilização (%)': value}
                                    for key, value in cpu_data.items()
                                ])
                                st.dataframe(df, hide_index=True)
                            
                            st.subheader("🌐 Rede")
                            bytes_sent = raw_metrics.get('net_io_counters_eth0-bytes_sent1', 0)
                            bytes_recv = raw_metrics.get('net_io_counters_eth0-bytes_recv1', 0)
                            st.metric("Bytes Enviados", f"{bytes_sent / (1024**2):.2f} MB")
                            st.metric("Bytes Recebidos", f"{bytes_recv / (1024**2):.2f} MB")
                        
                        with col2:
                            st.subheader("💾 Memória")
                            mem_total = raw_metrics.get('virtual_memory-total', 0)
                            mem_used = raw_metrics.get('virtual_memory-used', 0)
                            mem_cached = raw_metrics.get('virtual_memory-cached', 0)
                            mem_buffers = raw_metrics.get('virtual_memory-buffers', 0)
                            
                            st.metric("Total", f"{mem_total / (1024**3):.2f} GB")
                            st.metric("Usada", f"{mem_used / (1024**3):.2f} GB")
                            st.metric("Cache", f"{mem_cached / (1024**3):.2f} GB")
                            st.metric("Buffers", f"{mem_buffers / (1024**3):.2f} GB")
                
                # Seção 4: JSON completo
                with st.expander("📄 Ver JSON Completo (Métricas Processadas)", expanded=False):
                    st.json(metrics)
            
            # Status da conexão
            st.markdown("---")
            st.caption(f"⚡ Última atualização: {datetime.now().strftime('%H:%M:%S')} | "
                      f"Status: {'🟢 Conectado' if metrics else '🔴 Sem dados'}")
        
        # Auto-refresh
        if not auto_refresh:
            break
        
        time.sleep(REFRESH_INTERVAL)


if __name__ == "__main__":
    main()

