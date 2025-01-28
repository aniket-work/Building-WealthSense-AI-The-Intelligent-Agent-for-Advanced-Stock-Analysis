import yfinance as yf
import pandas as pd
import numpy as np
from crewai.tools import tool
from ta import add_all_ta_features
from ta.utils import dropna
from scipy.signal import find_peaks

@tool
def yf_tech_analysis(ticker: str, period: str = "1y"):
    """
    Perform advanced technical analysis on a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol.
        period (str): The time period for analysis (e.g., "1y" for 1 year).
    
    Returns:
        dict: Advanced technical analysis results.
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    
    # Add all technical analysis features
    df = add_all_ta_features(
        history, open="Open", high="High", low="Low", close="Close", volume="Volume"
    )
    df = dropna(df)
    
    # Calculate additional custom indicators
    df['volatility'] = df['Close'].pct_change().rolling(window=20).std() * np.sqrt(252)
    df['momentum'] = df['Close'] - df['Close'].shift(20)
    
    # Identify potential support and resistance levels
    close_prices = df['Close'].values
    peaks, _ = find_peaks(close_prices, distance=20)
    troughs, _ = find_peaks(-close_prices, distance=20)
    support_levels = close_prices[troughs][-3:]
    resistance_levels = close_prices[peaks][-3:]
    
    # Identify chart patterns
    patterns = identify_chart_patterns(df)
    
    return {
        "ticker": ticker,
        "current_price": df['Close'].iloc[-1],
        "sma_50": df['trend_sma_50'].iloc[-1],
        "sma_200": df['trend_sma_200'].iloc[-1],
        "rsi": df['momentum_rsi'].iloc[-1],
        "macd": df['trend_macd_diff'].iloc[-1],
        "bollinger_hband": df['volatility_bbhi'].iloc[-1],
        "bollinger_lband": df['volatility_bbli'].iloc[-1],
        "atr": df['volatility_atr'].iloc[-1],
        "volatility": df['volatility'].iloc[-1],
        "momentum": df['momentum'].iloc[-1],
        "support_levels": support_levels.tolist(),
        "resistance_levels": resistance_levels.tolist(),
        "identified_patterns": patterns
    }

def identify_chart_patterns(df):
    patterns = []
    close = df['Close'].values
    
    # Head and Shoulders pattern
    if is_head_and_shoulders(close):
        patterns.append("Head and Shoulders")
    
    # Double Top pattern
    if is_double_top(close):
        patterns.append("Double Top")
    
    # Double Bottom pattern
    if is_double_bottom(close):
        patterns.append("Double Bottom")
    
    return patterns

def is_head_and_shoulders(close):
    # Simplified head and shoulders detection
    peaks, _ = find_peaks(close, distance=20)
    if len(peaks) >= 3:
        left_shoulder, head, right_shoulder = peaks[-3], peaks[-2], peaks[-1]
        if close[head] > close[left_shoulder] and close[head] > close[right_shoulder]:
            return True
    return False

def is_double_top(close):
    # Simplified double top detection
    peaks, _ = find_peaks(close, distance=20)
    if len(peaks) >= 2:
        if abs(close[peaks[-1]] - close[peaks[-2]]) / close[peaks[-2]] < 0.03:
            return True
    return False

def is_double_bottom(close):
    # Simplified double bottom detection
    troughs, _ = find_peaks(-close, distance=20)
    if len(troughs) >= 2:
        if abs(close[troughs[-1]] - close[troughs[-2]]) / close[troughs[-2]] < 0.03:
            return True
    return False
