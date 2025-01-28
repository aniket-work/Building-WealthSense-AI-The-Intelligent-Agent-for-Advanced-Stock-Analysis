import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from agentic_orchestrator import run_analysis
import json
import streamlit as st

def main():
    st.set_page_config(layout="wide", page_title="Stock Analysis")



    # Add at start of your code
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        }

        div[data-testid="stTextInput"] input {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            color: #ffffff;
            padding: 15px;
            font-size: 16px;
        }

        .stButton > button {
            background: linear-gradient(90deg, #1E3B8A 0%, #0047AB 100%);
            padding: 15px 30px;
            font-weight: 500;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }

        [data-testid="stMetricValue"] {
            background: #1E3B8A;
            padding: 10px;
            border-radius: 5px;
            font-size: 20px;
        }

        h1, h2, h3 {
            background: linear-gradient(90deg, #ffffff 0%, #cccccc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("WealthSense AI Agentic Advanced Stock Analysis")

    # Keep original functionality, just enhance the visual presentation
    stock_symbol = st.text_input("Enter Stock Symbol:", "AAPL", help="Example: AAPL, GOOGL, MSFT")

    if st.button("Analyze Stock"):
        # Your existing analysis code remains unchanged
        with st.spinner("Analyzing..."):
            result = run_analysis(stock_symbol)

        # Rest of your code stays exactly the same, just with better styling applied
        analysis = json.loads(result)

        st.header("Analysis Report")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Technical Analysis")
            st.write(analysis.get('technical_analysis', 'No technical analysis available'))

            st.subheader("Chart Patterns")
            st.write(analysis.get('chart_patterns', 'No chart patterns identified'))

        with col2:
            st.subheader("Fundamental Analysis")
            st.write(analysis.get('fundamental_analysis', 'No fundamental analysis available'))

            st.subheader("Sentiment Analysis")
            st.write(analysis.get('sentiment_analysis', 'No sentiment analysis available'))

        st.subheader("Risk Assessment")
        st.write(analysis.get('risk_assessment', 'No risk assessment available'))

        st.subheader("Competitor Analysis")
        st.write(analysis.get('competitor_analysis', 'No competitor analysis available'))

        st.subheader("Investment Strategy")
        st.write(analysis.get('investment_strategy', 'No investment strategy available'))

        stock = yf.Ticker(stock_symbol)
        hist = stock.history(period="1y")

        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index,
                                     open=hist['Open'],
                                     high=hist['High'],
                                     low=hist['Low'],
                                     close=hist['Close'],
                                     name='Price'))

        fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', yaxis='y2'))

        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=50).mean(), name='50-day MA'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(window=200).mean(), name='200-day MA'))

        fig.update_layout(
            title=f"{stock_symbol} Stock Analysis",
            yaxis_title='Price',
            yaxis2=dict(title='Volume', overlaying='y', side='right'),
            xaxis_rangeslider_visible=False,
            template='plotly_white',
            height=600,
            margin=dict(t=100, b=50)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Key Statistics")
        info = stock.info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
            st.metric("P/E Ratio", round(info.get('trailingPE', 0), 2))
        with col2:
            st.metric("52 Week High", f"${info.get('fiftyTwoWeekHigh', 0):,.2f}")
            st.metric("52 Week Low", f"${info.get('fiftyTwoWeekLow', 0):,.2f}")
        with col3:
            st.metric("Dividend Yield", f"{info.get('dividendYield', 0):.2%}")
            st.metric("Beta", round(info.get('beta', 0), 2))


if __name__ == "__main__":
    main()