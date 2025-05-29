import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuração inicial do Streamlit
st.set_page_config(page_title="Gráfico de Candlestick", layout="wide")
st.title("📊 Gráfico de Candlestick Interativo + Análise Técnica")

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
symbol = st.sidebar.text_input("Ticker do Ativo", value="AAPL")

interval_options = {
    "1 minuto": "1m",
    "5 minutos": "5m",
    "15 minutos": "15m",
    "30 minutos": "30m",
    "1 hora": "60m",
    "1 dia": "1d"
}

# Definir intervalo padrão como "1 dia"
interval_display = st.sidebar.selectbox(
    "Intervalo", 
    options=list(interval_options.keys()),
    index=list(interval_options.keys()).index("1 dia")  # Padrão: 1 dia
)

interval = interval_options[interval_display]

# Definir período padrão como 60 dias
period_days = st.sidebar.slider(
    "Período (dias)", 
    min_value=1, 
    max_value=60, 
    value=60  # Padrão: 60 dias
)

# Indicadores técnicos no Sidebar
st.sidebar.subheader("📈 Indicadores Técnicos")
add_sma = st.sidebar.checkbox("Média Móvel Simples (SMA)")
add_ema = st.sidebar.checkbox("Média Móvel Exponencial (EMA)")
add_rsi = st.sidebar.checkbox("RSI (Relative Strength Index)")
add_macd = st.sidebar.checkbox("MACD")

# Botão para forçar atualização
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# Tabs principais
#tab1, tab2 = st.tabs(["📈 Gráfico de Preço", "📉 Análise Técnica"])

# Função para carregar dados
#@st.cache_data(ttl=300)
def get_data(ticker_, interval_, period_days_):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days_)
    data = yf.download("AAPL", start="2022-01-01", end="2022-12-31")
    #data = yf.download(
    #    tickers=ticker_,
    #    start=start_date,
    #    end=end_date,
    #    interval=interval_
    #)
    if not data.empty:
        data.dropna(inplace=True)  # Remove linhas vazias

        # Garantir que o índice seja DatetimeIndex
        #if not isinstance(data.index, pd.DatetimeIndex):
        #    data.index = pd.to_datetime(data.index)

    return data

# Carregando os dados
try:
    #ticker = yf.Ticker(symbol)
    #data = ticker.history(period="3mo")

    end_date = datetime.now()
    #start_date = end_date - timedelta(days=period_days)
    #data = yf.download("AAPL", start="2025-01-01", end="2025-01-28", interval="1d")
    data = yf.download("AAPL", start="2020-01-01", end=end_date)
    data.reset_index(inplace=True)  # Make it no longer an Index
    data['Date'] = pandas.to_datetime(data['Date'], format="%Y/%m/%d")  
    
    #data = data.stack().reset_index().rename(index=str, columns={"level_1": "Symbol"}).sort_values(['Date'])
    #data = get_data(symbol, interval, period_days)
    
    if data.empty:
        st.warning("⚠️ Nenhum dado encontrado. Verifique o ticker ou período.")
    else:
        st.subheader("Gráfico de Candlestick")

        if len(data) < 2:
            st.warning("⚠️ Poucos dados para exibir o gráfico.")
        else:
            required_columns = ['Open', 'High', 'Low', 'Close']
            missing_cols = [col for col in required_columns if col not in data.columns]

            if missing_cols:
                st.error(f"❌ Faltando colunas no dataset: {missing_cols}")
            else:
                st.success("✅ Dados carregados. Gerando gráfico...")

                # Copiar dados para evitar alterações no original
                df_plot = data.copy()

                # Garantir índice como datetime
                if not isinstance(df_plot.index, pd.DatetimeIndex):
                    df_plot.index = pd.to_datetime(df_plot.index)

                # Calcular indicadores
                if add_sma:
                    sma_period = st.slider("Período da SMA", min_value=2, max_value=100, value=9)
                    df_plot[f"SMA_{sma_period}"] = df_plot["Close"].rolling(window=sma_period).mean()

                if add_ema:
                    ema_period = st.slider("Período da EMA", min_value=2, max_value=100, value=21)
                    df_plot[f"EMA_{ema_period}"] = df_plot["Close"].ewm(span=ema_period, adjust=False).mean()


                # Criar gráfico de candlestick
                fig = go.Figure(data=[go.Candlestick(x=data.index,
                                    open=data['Open'],
                                    high=data['High'],
                                    low=data['Low'],
                                    close=data['Close'])])

                # Adicionar indicadores (se ativados)
                if add_sma:
                    fig.add_trace(go.Scatter(
                        x=df_plot.index,
                        y=df_plot[f"SMA_{sma_period}"],
                        mode='lines',
                        name=f"SMA {sma_period}",
                        line=dict(color="blue")
                    ))

                if add_ema:
                    fig.add_trace(go.Scatter(
                        x=df_plot.index,
                        y=df_plot[f"EMA_{ema_period}"],
                        mode='lines',
                        name=f"EMA {ema_period}",
                        line=dict(color="orange")
                    ))

                # Set the chart title and labels
                fig.update_layout(
                    title=f'Candlestick Chart of {symbol}',
                    xaxis_title='Date',
                    yaxis_title='Price',
                    xaxis_rangeslider_visible=False,
                    template=selected_theme["plot_template"],
                    height=800
                )

                # Display the chart
                fig.show()

                st.plotly_chart(fig, use_container_width=True)

                # Cálculo e exibição do RSI
                if add_rsi:
                    st.markdown("### RSI (Relative Strength Index)")
                    rsi_period = st.slider("Período do RSI", min_value=2, max_value=30, value=14)
                    delta = df_plot['Close'].diff()
                    gain = delta.where(delta > 0, 0)
                    loss = -delta.where(delta < 0, 0)
                    avg_gain = gain.rolling(rsi_period).mean()
                    avg_loss = loss.rolling(rsi_period).mean()
                    rs = avg_gain / avg_loss
                    df_plot['RSI'] = 100 - (100 / (1 + rs))

                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(x=df_plot.index, y=df_plot['RSI'], mode='lines', name='RSI'))
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                    fig_rsi.update_layout(title="RSI", template=selected_theme["plot_template"])
                    st.plotly_chart(fig_rsi, use_container_width=True)

                # Cálculo e exibição do MACD
                if add_macd:
                    st.markdown("### MACD (Moving Average Convergence Divergence)")
                    df_plot['EMA12'] = df_plot['Close'].ewm(span=12, adjust=False).mean()
                    df_plot['EMA26'] = df_plot['Close'].ewm(span=26, adjust=False).mean()
                    df_plot['MACD'] = df_plot['EMA12'] - df_plot['EMA26']
                    df_plot['Signal_Line'] = df_plot['MACD'].ewm(span=9, adjust=False).mean()

                    fig_macd = go.Figure()
                    fig_macd.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'], mode='lines', name='MACD'))
                    fig_macd.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Signal_Line'], mode='lines', name='Linha de Sinal'))
                    fig_macd.add_trace(go.Bar(x=df_plot.index, y=df_plot['MACD'] - df_plot['Signal_Line'], name='Histograma'))
                    fig_macd.update_layout(title="MACD", template=selected_theme["plot_template"])
                    st.plotly_chart(fig_macd, use_container_width=True)

                # Mostrar dados brutos (opcional)
                if st.checkbox("Mostrar dados brutos"):
                    st.dataframe(data.tail(100))
        

except Exception as e:
    st.error(f"❌ Ocorreu um erro ao carregar os dados: {e}")
