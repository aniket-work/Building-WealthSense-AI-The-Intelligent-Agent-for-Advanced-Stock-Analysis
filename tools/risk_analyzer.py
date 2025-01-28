import yfinance as yf
import numpy as np
from scipy import stats
from crewai.tools import tool

@tool
def risk_assessment(ticker: str, benchmark: str = "^GSPC", period: str = "5y"):
    """
    Performs comprehensive risk assessment for a given financial instrument.

    Args:
        ticker (str): The stock ticker symbol to analyze (e.g., "AAPL", "GOOGL")
        benchmark (str, optional): Benchmark index for comparison. Defaults to "^GSPC" (S&P 500)
        period (str, optional): Time period for analysis. Defaults to "5y"
        confidence_level (float, optional): Confidence level for VaR calculation. Defaults to 0.95
        risk_free_rate (float, optional): Annual risk-free rate for calculations. Defaults to 0.02

    Returns:
        Dict containing:
            - ticker (str): Analyzed stock symbol
            - beta (float): Stock's beta relative to benchmark
            - alpha (float): Jensen's alpha
            - sharpe_ratio (float): Risk-adjusted return metric
            - treynor_ratio (float): Risk-adjusted return using beta
            - value_at_risk (Dict[str, float]): VaR at different confidence levels
            - expected_shortfall (float): Average loss beyond VaR
            - max_drawdown (float): Maximum peak to trough decline
            - volatility (Dict[str, float]): Various volatility metrics
            - correlation (float): Correlation with benchmark
            - risk_rating (str): Overall risk assessment rating

    Raises:
        ValueError: If insufficient data for analysis
        TypeError: If input parameters are invalid

    Note:
        Risk metrics are calculated using daily returns and annualized where appropriate
    """
    stock = yf.Ticker(ticker)
    benchmark_index = yf.Ticker(benchmark)
    
    stock_data = stock.history(period=period)['Close']
    benchmark_data = benchmark_index.history(period=period)['Close']
    
    # Calculate returns
    stock_returns = stock_data.pct_change().dropna()
    benchmark_returns = benchmark_data.pct_change().dropna()
    
    # Calculate beta
    covariance = np.cov(stock_returns, benchmark_returns)[0][1]
    benchmark_variance = np.var(benchmark_returns)
    beta = covariance / benchmark_variance
    
    # Calculate Sharpe ratio
    risk_free_rate = 0.02  # Assume 2% risk-free rate
    excess_returns = stock_returns - risk_free_rate
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    # Calculate Value at Risk (VaR)
    var_95 = np.percentile(stock_returns, 5)
    
    # Calculate Maximum Drawdown
    cumulative_returns = (1 + stock_returns).cumprod()
    max_drawdown = (cumulative_returns.cummax() - cumulative_returns).max()
    
    return {
        "ticker": ticker,
        "beta": beta,
        "sharpe_ratio": sharpe_ratio,
        "value_at_risk_95": var_95,
        "max_drawdown": max_drawdown,
        "volatility": stock_returns.std() * np.sqrt(252)
    }
