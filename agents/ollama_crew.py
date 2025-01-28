import json
from crewai import Agent, Task, Crew, Process
from tools.tech_stats_analyzer import yf_tech_analysis
from tools.tech_indicator_analyzer import yf_fundamental_analysis
from tools.risk_analyzer import risk_assessment
from tools.market_analyzer import competitor_analysis
from tools.market_view_analyzer import sentiment_analysis

class OllamaAgent:
    def __init__(self, model_name="tinyllama"):
        self.model = model_name

    async def agenerate(self, messages):
        prompt = self._format_messages(messages)
        try:
            response = ollama.chat(model=self.model, messages=[
                {"role": "user", "content": prompt}
            ])
            return response['message']['content']
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def _format_messages(self, messages):
        formatted_prompt = ""
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            formatted_prompt += f"{role}: {content}\n"
        return formatted_prompt

def run_analysis(ticker: str) -> str:  # Returns a string that can be parsed as JSON
    try:
        # Collect all the raw analysis data
        tech_data = yf_tech_analysis(ticker)
        fundamental_data = yf_fundamental_analysis(ticker)
        risk_data = risk_assessment(ticker)
        competitor_data = competitor_analysis(ticker)
        sentiment_data = sentiment_analysis(ticker)

        # Format the data to match the expected structure
        analysis_result = {
            "technical_analysis": {
                "current_price": tech_data["current_price"],
                "sma_50": tech_data["sma_50"],
                "sma_200": tech_data["sma_200"],
                "rsi": tech_data["rsi"],
                "macd": tech_data["macd"]
            },
            "chart_patterns": tech_data["identified_patterns"],
            "fundamental_analysis": {
                "pe_ratio": fundamental_data["pe_ratio"],
                "market_cap": fundamental_data["market_cap"],
                "dividend_yield": fundamental_data["dividend_yield"],
                "revenue_growth": fundamental_data["revenue_growth"]
            },
            "sentiment_analysis": {
                "news_sentiment": sentiment_data["news_sentiment"],
                "social_sentiment": sentiment_data["social_sentiment"],
                "overall_sentiment": sentiment_data["overall_sentiment"]
            },
            "risk_assessment": {
                "beta": risk_data["beta"],
                "sharpe_ratio": risk_data["sharpe_ratio"],
                "value_at_risk_95": risk_data["value_at_risk_95"],
                "max_drawdown": risk_data["max_drawdown"]
            },
            "competitor_analysis": competitor_data["competitors"],
            "investment_strategy": generate_investment_strategy(tech_data, fundamental_data, risk_data, sentiment_data)
        }

        return json.dumps(analysis_result)

    except Exception as e:
        error_result = {
            "error": f"Analysis failed: {str(e)}",
            "technical_analysis": "Analysis failed",
            "chart_patterns": [],
            "fundamental_analysis": "Analysis failed",
            "sentiment_analysis": "Analysis failed",
            "risk_assessment": "Analysis failed",
            "competitor_analysis": "Analysis failed",
            "investment_strategy": "Unable to generate strategy due to analysis failure"
        }
        return json.dumps(error_result)

def generate_investment_strategy(tech_data, fundamental_data, risk_data, sentiment_data):
    # This would ideally use Ollama for generating the strategy
    # For now, we'll return a placeholder
    return "Investment strategy generation not yet implemented with Ollama"