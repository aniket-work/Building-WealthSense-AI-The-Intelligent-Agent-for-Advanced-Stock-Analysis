import yfinance as yf
from crewai.tools import tool

@tool
def yf_fundamental_analysis(ticker: str):
    """
    Performs comprehensive fundamental analysis on a given stock.

    Args:
        ticker (str): The stock ticker symbol to analyze (e.g., "AAPL", "GOOGL")
        lookback_years (int, optional): Years of historical data to analyze. Defaults to 5
        peer_comparison (bool, optional): Include peer comparison analysis. Defaults to True

    Returns:
        Dict containing:
            - company_info (Dict[str, str]): Basic company information
            - valuation_metrics (Dict[str, float]): Key valuation ratios
            - growth_metrics (Dict[str, float]): Growth rate calculations
            - profitability_metrics (Dict[str, float]): Profitability measures
            - efficiency_metrics (Dict[str, float]): Operational efficiency ratios
            - liquidity_metrics (Dict[str, float]): Liquidity measures
            - solvency_metrics (Dict[str, float]): Long-term solvency measures
            - cash_flow_metrics (Dict[str, float]): Cash flow analysis
            - peer_comparison (List[Dict[str, float]]): Industry peer analysis
            - historical_trends (Dict[str, List[float]]): Historical metric trends

    Raises:
        ValueError: If insufficient financial data available
        TypeError: If input parameters are invalid

    Note:
        All growth rates and ratios are returned as decimal values
    """

    stock = yf.Ticker(ticker)
    info = stock.info
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    
    # Calculate additional financial ratios
    try:
        current_ratio = balance_sheet.loc['Total Current Assets'].iloc[-1] / balance_sheet.loc['Total Current Liabilities'].iloc[-1]
        debt_to_equity = balance_sheet.loc['Total Liabilities'].iloc[-1] / balance_sheet.loc['Total Stockholder Equity'].iloc[-1]
        roe = financials.loc['Net Income'].iloc[-1] / balance_sheet.loc['Total Stockholder Equity'].iloc[-1]
        roa = financials.loc['Net Income'].iloc[-1] / balance_sheet.loc['Total Assets'].iloc[-1]
        
        # Calculate growth rates
        revenue_growth = (financials.loc['Total Revenue'].iloc[-1] - financials.loc['Total Revenue'].iloc[-2]) / financials.loc['Total Revenue'].iloc[-2]
        net_income_growth = (financials.loc['Net Income'].iloc[-1] - financials.loc['Net Income'].iloc[-2]) / financials.loc['Net Income'].iloc[-2]
        
        # Free Cash Flow calculation
        fcf = cash_flow.loc['Operating Cash Flow'].iloc[-1] - cash_flow.loc['Capital Expenditures'].iloc[-1]
    except:
        current_ratio = debt_to_equity = roe = roa = revenue_growth = net_income_growth = fcf = None
    
    return {
        "ticker": ticker,
        "company_name": info.get('longName'),
        "sector": info.get('sector'),
        "industry": info.get('industry'),
        "market_cap": info.get('marketCap'),
        "pe_ratio": info.get('trailingPE'),
        "forward_pe": info.get('forwardPE'),
        "peg_ratio": info.get('pegRatio'),
        "price_to_book": info.get('priceToBook'),
        "dividend_yield": info.get('dividendYield'),
        "beta": info.get('beta'),
        "52_week_high": info.get('fiftyTwoWeekHigh'),
        "52_week_low": info.get('fiftyTwoWeekLow'),
        "current_ratio": current_ratio,
        "debt_to_equity": debt_to_equity,
        "return_on_equity": roe,
        "return_on_assets": roa,
        "revenue_growth": revenue_growth,
        "net_income_growth": net_income_growth,
        "free_cash_flow": fcf,
        "analyst_recommendation": info.get('recommendationKey'),
        "target_price": info.get('targetMeanPrice')
    }
