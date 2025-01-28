class OllamaConfig:
    # Default model settings
    DEFAULT_MODEL = "tinyllama"

    # Ollama API settings
    API_BASE = "http://localhost:11434"  # Default Ollama API endpoint

    # Model parameters
    PARAMETERS = {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 2048,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0
    }

    # Task-specific prompts
    PROMPTS = {
        "technical_analysis": """Analyze the technical indicators and chart patterns for the given stock.
        Focus on key technical signals and potential trade setups.""",

        "fundamental_analysis": """Evaluate the company's fundamental metrics and financial health.
        Consider valuation ratios, growth metrics, and financial statements.""",

        "risk_assessment": """Assess the investment risks associated with the stock.
        Consider market risks, company-specific risks, and broader economic factors.""",

        "market_research": """Research market sentiment and competitive landscape.
        Analyze news sentiment, social media trends, and competitor positioning."""
    }

    # Error messages
    ERROR_MESSAGES = {
        "model_unavailable": "The specified Ollama model is not available. Please check your installation.",
        "api_error": "Error connecting to Ollama API. Please ensure Ollama is running.",
        "analysis_error": "Error performing analysis. Please try again."
    }