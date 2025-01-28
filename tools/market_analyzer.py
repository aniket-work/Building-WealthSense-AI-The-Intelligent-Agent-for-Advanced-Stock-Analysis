"""Market Analyzer Module

This module provides comprehensive competitor analysis functionality for financial markets.
It leverages the yfinance library to fetch and analyze competitor data within the same
industry sector.

Features:
    - Industry-based competitor identification
    - Comparative financial metrics analysis
    - Market positioning evaluation
    - Performance benchmarking

Dependencies:
    - yfinance: For fetching stock market data
    - crewai.tools: For tool decoration and integration

Example:
    ```python
    result = competitor_analysis("AAPL", num_competitors=5)
    print(result['competitors'])
    ```

Author: Aniket Hingane
Version: 2.0.0
Last Updated: 2024-01-27
"""

import yfinance as yf
from crewai.tools import tool
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np


@tool
def competitor_analysis(
        ticker: str,
        num_competitors: int = 3,
        metrics: Optional[List[str]] = None
) -> Dict[str, Union[str, List[Dict[str, Optional[float]]]]]:
    """
    Performs detailed competitor analysis for a given stock by analyzing companies
    within the same industry sector.

    Args:
        ticker (str): The stock ticker symbol to analyze (e.g., "AAPL", "GOOGL").
        num_competitors (int, optional): Number of top competitors to analyze. Defaults to 3.
        metrics (List[str], optional): List of specific metrics to analyze. If None,
            analyzes all available metrics.

    Returns:
        Dict[str, Union[str, List[Dict[str, Optional[float]]]]]: A dictionary containing:
            - main_stock: The analyzed stock ticker
            - industry: The industry classification
            - competitors: List of competitor data dictionaries containing:
                - ticker: Competitor stock symbol
                - name: Company name
                - market_cap: Market capitalization
                - pe_ratio: Price-to-Earnings ratio
                - revenue_growth: Year-over-year revenue growth
                - profit_margins: Profit margins
                - relative_strength: Market performance vs industry average

    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
        TypeError: If num_competitors is not a positive integer

    Note:
        Market cap values are returned in millions of dollars.
        Performance metrics are calculated using trailing twelve months (TTM) data.
    """
    if not isinstance(num_competitors, int) or num_competitors <= 0:
        raise TypeError("num_competitors must be a positive integer")

    stock = yf.Ticker(ticker)
    info = stock.info

    if not info:
        raise ValueError(f"Could not fetch data for ticker {ticker}")

    sector = info.get('sector')
    industry = info.get('industry')

    # Get industry index for the sector
    industry_stocks = yf.Ticker(f"^{sector}").info.get('components', [])
    competitors = [comp for comp in industry_stocks if comp != ticker][:num_competitors]

    # Calculate industry averages for benchmarking
    industry_metrics = calculate_industry_metrics(competitors)

    competitor_data = []
    for comp in competitors:
        try:
            comp_stock = yf.Ticker(comp)
            comp_info = comp_stock.info

            # Calculate relative strength compared to industry average
            relative_strength = calculate_relative_strength(
                comp_info,
                industry_metrics
            )

            competitor_data.append({
                "ticker": comp,
                "name": comp_info.get('longName'),
                "market_cap": format_market_cap(comp_info.get('marketCap')),
                "pe_ratio": comp_info.get('trailingPE'),
                "revenue_growth": format_percentage(comp_info.get('revenueGrowth')),
                "profit_margins": format_percentage(comp_info.get('profitMargins')),
                "relative_strength": relative_strength
            })
        except Exception as e:
            print(f"Warning: Could not analyze competitor {comp}: {str(e)}")
            continue

    return {
        "main_stock": ticker,
        "industry": industry,
        "competitors": sorted(competitor_data, key=lambda x: x['market_cap'] or 0,
                              reverse=True)
    }


def calculate_industry_metrics(tickers: List[str]) -> Dict[str, float]:
    """
    Calculates average industry metrics for benchmarking.

    Args:
        tickers (List[str]): List of stock tickers in the industry

    Returns:
        Dict[str, float]: Dictionary of average industry metrics
    """
    metrics = {
        'pe_ratio': [],
        'revenue_growth': [],
        'profit_margins': []
    }

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            if info.get('trailingPE'):
                metrics['pe_ratio'].append(info['trailingPE'])
            if info.get('revenueGrowth'):
                metrics['revenue_growth'].append(info['revenueGrowth'])
            if info.get('profitMargins'):
                metrics['profit_margins'].append(info['profitMargins'])
        except:
            continue

    return {
        key: np.mean(values) if values else None
        for key, values in metrics.items()
    }


def calculate_relative_strength(
        stock_info: Dict[str, Union[float, str, None]],
        industry_metrics: Dict[str, float]
) -> float:
    """
    Calculates the relative strength of a stock compared to industry averages.

    Args:
        stock_info (Dict[str, Union[float, str, None]]): Stock information
        industry_metrics (Dict[str, float]): Industry average metrics

    Returns:
        float: Relative strength score (>1 indicates above average)
    """
    metrics_weight = {
        'pe_ratio': 0.3,
        'revenue_growth': 0.4,
        'profit_margins': 0.3
    }

    score = 0
    total_weight = 0

    for metric, weight in metrics_weight.items():
        stock_value = stock_info.get(metric)
        industry_value = industry_metrics.get(metric)

        if stock_value and industry_value:
            # For PE ratio, lower is better
            if metric == 'pe_ratio':
                score += weight * (industry_value / stock_value)
            else:
                score += weight * (stock_value / industry_value)
            total_weight += weight

    return score / total_weight if total_weight > 0 else None


def format_market_cap(value: Optional[float]) -> Optional[float]:
    """Formats market cap value to millions."""
    return round(value / 1_000_000, 2) if value else None


def format_percentage(value: Optional[float]) -> Optional[float]:
    """Formats decimal to percentage with 2 decimal places."""
    return round(value * 100, 2) if value is not None else None