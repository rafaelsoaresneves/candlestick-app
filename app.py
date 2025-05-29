import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

st.title("Interactive Moving Average Envelope Visualization")

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
