import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Configuração inicial do Streamlit
st.set_page_config(page_title="Gráfico de Candlestick", layout="wide")
st.title("📊 Gráfico de Candlestick Interativo com Indicadores")

# Definição dos temas
THEMES = {
    "Escuro": {
        "background": "#0e1117",
        "text": "#fafafa",
        "plot_template": "plotly_dark"
    },
    "Claro": {
        "background": "#ffffff",
        "text": "#000000",
        "plot_template": "plotly_white"
    }
}

# Seleção de tema
theme = st.sidebar.selectbox("Escolha o Tema", list(THEMES.keys()))
selected_theme = THEMES[theme]

# Aplicando estilo customizado ao corpo da página
st.markdown(f"""
<style>
    body {{
        background-color: {selected_theme['background']};
        color: {selected_theme['text']};
    }}
    .sidebar .sidebar-content {{
        background-color: {selected_theme['background']};
    }}
</style>
""", unsafe_allow_html=True)

# Configurações do usuário
st.sidebar.header("Configurações")
ticker = st.sidebar.text_input("Ticker do Ativo", value="AAPL")

interval_options = {
    "1 minuto": "1m",
    "5 minutos": "5m",
    "15 minutos": "15m",
    "30 minutos": "30m",
    "1 hora": "60m",
    "1 dia": "1d"
}
interval_display = st.sidebar.selectbox("Intervalo", options=list(interval_options.keys()))
interval = interval_options[interval_display]

period_days = st.sidebar.slider("Período (dias)", min_value=1, max_value=60, value=7)

# Indicadores técnicos
add_sma = st.sidebar.checkbox("Adicionar Média Móvel Simples (SMA)")
sma_period = st.sidebar.number_input("Período da SMA", min_value=2, max_value=100, value=9, disabled=not add_sma)

add_ema = st.sidebar.checkbox("Adicionar Média Móvel Exponencial (EMA)")
ema_period = st.sidebar.number_input("Período da EMA", min_value=2, max_value=100, value=21, disabled=not add_ema)

# Função para carregar dados
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_data(ticker_, interval_, period_days_):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days_)
    data = yf.download(
        tickers=ticker_,
        start=start_date,
        end=end_date,
        interval=interval_
    )
    return data

# Carregando os dados
try:
    df = get_data(ticker, interval, period_days)

    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado. Verifique o ticker ou período.")
    else:
        # Adicionando indicadores
        if add_sma:
            df[f"SMA_{sma_period}"] = df["Close"].rolling(window=sma_period).mean()

        if add_ema:
            df[f"EMA_{ema_period}"] = df["Close"].ewm(span=ema_period, adjust=False).mean()

        # Criando o gráfico de candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Candlesticks'
        )])

        # Adicionando indicadores
        if add_sma:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[f"SMA_{sma_period}"],
                mode='lines',
                name=f"SMA {sma_period}",
                line=dict(color="blue")
            ))

        if add_ema:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[f"EMA_{ema_period}"],
                mode='lines',
                name=f"EMA {ema_period}",
                line=dict(color="orange")
            ))

        # Layout do gráfico
        fig.update_layout(
            title=f"{ticker} - Gráfico de Candlestick ({interval_display})",
            xaxis_title="Data",
            yaxis_title="Preço",
            xaxis_rangeslider_visible=False,
            template=selected_theme["plot_template"],
            height=800
        )

        # Mostrar gráfico
        st.plotly_chart(fig, use_container_width=True)

        # Mostrar dados brutos (opcional)
        if st.checkbox("Mostrar dados brutos"):
            st.dataframe(df.tail(100))

except Exception as e:
    st.error(f"❌ Ocorreu um erro ao carregar os dados: {e}")
