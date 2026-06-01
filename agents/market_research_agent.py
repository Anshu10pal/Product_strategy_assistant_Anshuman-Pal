"""
Agent 2: Market Research Agent
Analyzes market trends, industry data, and growth opportunities.
"""

from utils.llm_client import chat_completion
from utils.vector_store import query_documents

SYSTEM_PROMPT = """You are a Market Research Strategist with deep expertise in product markets.
Your role is to analyze market data, identify trends, and surface growth opportunities.
Focus on:
- Market size and growth trajectory
- Emerging trends and disruptions
- Target segment opportunities
- Demand signals and whitespace
- Macro factors affecting the product

Be analytical, forward-looking, and concise. Structure your output clearly."""


def run_market_research_agent(context: str = "") -> str:
    """
    Analyze market data and trends from ingested documents.
    Returns market research summary string.
    """
    retrieved = query_documents(
        "market trends growth industry analysis revenue sales data segments",
        n_results=6,
    )

    combined_context = ""
    if context:
        combined_context += f"Additional context:\n{context}\n\n"
    if retrieved and "[ChromaDB Error]" not in retrieved and "No documents" not in retrieved:
        combined_context += f"Relevant document excerpts:\n{retrieved}"

    if not combined_context.strip():
        combined_context = "No specific data uploaded. Provide a general market research framework."

    messages = [
        {
            "role": "user",
            "content": (
                f"Analyze the following market data:\n\n{combined_context}\n\n"
                "Provide:\n"
                "1. Market Overview & Size Estimate\n"
                "2. Top 3 Market Trends\n"
                "3. Target Segment Analysis\n"
                "4. Growth Opportunities\n"
                "5. Market Risks"
            ),
        }
    ]

    return chat_completion(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)
