"""
Agent 4: SWOT Analysis Agent
Synthesizes inputs from previous agents to produce a structured SWOT analysis.
"""

from utils.llm_client import chat_completion
from utils.vector_store import query_documents

SYSTEM_PROMPT = """You are a Strategic Business Analyst specializing in SWOT analysis.
You synthesize inputs from customer feedback, market research, and competitor analysis
to produce a clear, actionable SWOT matrix.

Each quadrant must have 3–5 specific, evidence-based points.
After the SWOT matrix, provide 2–3 strategic implications.
Be concise and structured."""


def run_swot_agent(
    customer_insights: str = "",
    market_insights: str = "",
    competitor_insights: str = "",
) -> str:
    """
    Synthesize previous agent outputs into a SWOT analysis.
    Returns SWOT analysis string.
    """
    retrieved = query_documents(
        "product strengths weaknesses opportunities threats strategy",
        n_results=4,
    )

    synthesis = ""
    if customer_insights:
        synthesis += f"CUSTOMER INSIGHTS:\n{customer_insights}\n\n"
    if market_insights:
        synthesis += f"MARKET INSIGHTS:\n{market_insights}\n\n"
    if competitor_insights:
        synthesis += f"COMPETITOR INSIGHTS:\n{competitor_insights}\n\n"
    if retrieved and "[ChromaDB Error]" not in retrieved and "No documents" not in retrieved:
        synthesis += f"ADDITIONAL CONTEXT FROM DOCUMENTS:\n{retrieved}\n\n"

    if not synthesis.strip():
        synthesis = "No specific data available. Generate a general SWOT framework."

    messages = [
        {
            "role": "user",
            "content": (
                f"Based on the following synthesized insights:\n\n{synthesis}\n\n"
                "Generate a detailed SWOT Analysis:\n\n"
                "STRENGTHS (internal positives)\n"
                "WEAKNESSES (internal negatives)\n"
                "OPPORTUNITIES (external positives)\n"
                "THREATS (external negatives)\n\n"
                "Then provide 2-3 Strategic Implications from the SWOT."
            ),
        }
    ]

    return chat_completion(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)
