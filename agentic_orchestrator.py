from crewai import Agent, Task, Crew, Process
from custom_llm import OllamaLLM
import json
from typing import Dict, Any

# Import all necessary tools
from tools.tech_stats_analyzer import yf_tech_analysis
from tools.tech_indicator_analyzer import yf_fundamental_analysis
from tools.market_view_analyzer import sentiment_analysis
from tools.market_analyzer import competitor_analysis
from tools.risk_analyzer import risk_assessment


def create_crew(stock_symbol: str) -> Crew:
    """
    Create a crew of AI agents for comprehensive stock analysis.

    Args:
        stock_symbol (str): The stock ticker symbol to analyze

    Returns:
        Crew: A configured CrewAI crew ready for analysis
    """
    # Initialize the Ollama LLM with the specified model
    llm = OllamaLLM(model_name="llama3.2:3b")

    # Define the Stock Market Researcher Agent
    researcher = Agent(
        role='Stock Market Researcher',
        goal='Conduct thorough technical and fundamental analysis of the stock',
        backstory="""You're an experienced stock market researcher with a talent for 
        uncovering market patterns and analyzing company fundamentals. You always 
        provide analysis in clear, structured JSON format.""",
        tools=[yf_tech_analysis, yf_fundamental_analysis, competitor_analysis],
        llm=llm,
        verbose=True
    )

    # Define the Financial Analyst Agent
    analyst = Agent(
        role='Financial Analyst',
        goal='Analyze data and assess investment risks comprehensively',
        backstory="""You're a seasoned financial analyst known for accurate predictions 
        and risk assessment. You provide detailed analysis in JSON format with clear 
        metrics and insights.""",
        tools=[yf_tech_analysis, yf_fundamental_analysis, risk_assessment],
        llm=llm,
        verbose=True
    )

    # Define the Sentiment Analyst Agent
    sentiment_analyst = Agent(
        role='Sentiment Analyst',
        goal='Analyze market sentiment and media perception',
        backstory="""You're an expert in behavioral finance and sentiment analysis, 
        skilled at gauging market emotions and their impact on stock performance. 
        You format all outputs as structured JSON.""",
        tools=[sentiment_analysis],
        llm=llm,
        verbose=True
    )

    # Define the Investment Strategist Agent
    strategist = Agent(
        role='Investment Strategist',
        goal='Develop actionable investment strategies',
        backstory="""You're a renowned investment strategist who creates data-driven 
        investment plans. You always present recommendations in clear JSON format 
        with specific actions and risk considerations.""",
        tools=[],  # No specific tools needed for strategy formulation
        llm=llm,
        verbose=True
    )

    # Define Tasks with specific JSON output requirements
    research_task = Task(
        description=f"""Research {stock_symbol} using technical and fundamental analysis tools.
        Return your findings in JSON format with the following structure:
        {{
            "technical_analysis": {{
                "indicators": {{...}},
                "patterns": {{...}},
                "trends": {{...}}
            }},
            "fundamental_analysis": {{
                "metrics": {{...}},
                "growth": {{...}},
                "valuation": {{...}}
            }}
        }}""",
        agent=researcher
    )

    sentiment_task = Task(
        description=f"""Analyze market sentiment for {stock_symbol}.
        Return your analysis in JSON format with the following structure:
        {{
            "sentiment_analysis": {{
                "news_sentiment": {{...}},
                "social_media_sentiment": {{...}},
                "overall_sentiment": {{...}}
            }}
        }}""",
        agent=sentiment_analyst
    )

    analysis_task = Task(
        description=f"""Analyze all data for {stock_symbol} and assess risks.
        Return your analysis in JSON format with the following structure:
        {{
            "risk_assessment": {{
                "market_risks": {{...}},
                "company_risks": {{...}},
                "financial_risks": {{...}}
            }}
        }}""",
        agent=analyst
    )

    strategy_task = Task(
        description=f"""Create investment strategy for {stock_symbol} based on all analyses.
        Return your strategy in JSON format with the following structure:
        {{
            "investment_strategy": {{
                "recommendation": {{...}},
                "entry_points": {{...}},
                "exit_points": {{...}},
                "risk_management": {{...}}
            }}
        }}""",
        agent=strategist
    )

    # Create and return the configured Crew
    crew = Crew(
        agents=[researcher, sentiment_analyst, analyst, strategist],
        tasks=[research_task, sentiment_task, analysis_task, strategy_task],
        process=Process.sequential,
        verbose=2  # Enable verbose output for debugging
    )

    return crew


from crewai import Agent, Task, Crew, Process
from custom_llm import OllamaLLM
import json
import yfinance as yf


def run_analysis(ticker: str) -> str:
    try:
        # Get stock data
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="1y")
        info = stock.info

        # Vision analysis
        chart_prompt = f"""Given the {ticker} stock chart:
        - Price movement from March 2024 to Jan 2025
        - Currently around $220-230 range
        - Below 50-day MA (short-term bearish)
        - Above 200-day MA (long-term uptrend)
        - Notable volume spikes in Jul/Sep/Dec"""

        # Stock data prompt
        data_prompt = f"""With these metrics:
        Market Cap: ${info.get('marketCap'):,.0f}
        P/E: {info.get('trailingPE')}
        52W High: ${info.get('fiftyTwoWeekHigh')}
        52W Low: ${info.get('fiftyTwoWeekLow')}
        Beta: {info.get('beta')}"""

        llm = OllamaLLM(model_name="llama3.2-vision")
        response = llm.create_chat_completion(f"{chart_prompt}\n{data_prompt}\nProvide analysis in JSON format")

        try:
            parsed = json.loads(response)
            return json.dumps(parsed, indent=2)
        except:
            # Fallback with real stock data
            ma50 = stock_data['Close'].rolling(window=50).mean()[-1]
            ma200 = stock_data['Close'].rolling(window=200).mean()[-1]
            current_price = stock_data['Close'][-1]

            return json.dumps({
                "technical_analysis": {
                    "price_trend": "BEARISH" if current_price < ma50 else "BULLISH",
                    "key_levels": {
                        "support": float(stock_data['Low'].min()),
                        "resistance": float(stock_data['High'].max())
                    },
                    "moving_averages": {
                        "50_day": "BELOW" if current_price < ma50 else "ABOVE",
                        "200_day": "ABOVE" if current_price > ma200 else "BELOW"
                    }
                },
                "fundamental_analysis": {
                    "valuation": "PREMIUM",
                    "key_metrics": {
                        "pe_ratio_analysis": str(info.get('trailingPE')),
                        "market_cap_assessment": f"${info.get('marketCap'):,.0f}"
                    }
                }
            })
    except Exception as e:
        print(f"Analysis error: {e}")
        return json.dumps({"error": str(e)})