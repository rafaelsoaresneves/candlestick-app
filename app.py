import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuração inicial do Streamlit
st.set_page_config(page_title="Gráfico de Candlestick", layout="wide")
st.title("📊 Gráfico de Candlestick Interativo + Análise Técnica")

# Retrieve AAPL historical data
symbol = "AAPL"
ticker = yf.Ticker(symbol)
data = ticker.history(period="6mo")

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
