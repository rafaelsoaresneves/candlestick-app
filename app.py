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

# Retrieve AAPL historical data
symbol = "AAPL"
ticker = yf.Ticker(symbol)
data = ticker.history(period="2mo")

# Create candlestick chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                                     open=data['Open'],
                                     high=data['High'],
                                     low=data['Low'],
                                     close=data['Close'])])

# Set the chart title and labels
fig.update_layout(title=f'Candlestick Chart of {ticker}',
                  xaxis_title='Date',
                  yaxis_title='Price')

# Display the chart
fig.show()

st.plotly_chart(fig, use_container_width=True)
