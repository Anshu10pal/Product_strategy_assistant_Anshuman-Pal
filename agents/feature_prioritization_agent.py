"""
Agent 5: Feature Prioritization Agent
Prioritizes features using RICE scoring framework.
Considers customer demand, market opportunity, and strategic fit.
"""

from utils.llm_client import chat_completion
from utils.vector_store import query_documents

SYSTEM_PROMPT = """You are a Product Manager specializing in feature prioritization.
You use the RICE framework (Reach, Impact, Confidence, Effort) to prioritize features.
You also consider strategic alignment and competitive differentiation.

Output a prioritized feature list with reasoning.
Format each feature clearly with its priority score rationale.
Be concise, structured, and practical."""


def run_feature_prioritization_agent(
    customer_insights: str = "",
    swot_insights: str = "",
    market_insights: str = "",
) -> str:
    """
    Generate feature prioritization recommendations.
    Returns prioritized feature list string.
    """
    retrieved = query_documents(
        "feature requests product roadmap improvements enhancements user needs",
        n_results=6,
    )

    synthesis = ""
    if customer_insights:
        synthesis += f"CUSTOMER INSIGHTS (feature requests, pain points):\n{customer_insights}\n\n"
    if market_insights:
        synthesis += f"MARKET INSIGHTS (opportunities):\n{market_insights}\n\n"
    if swot_insights:
        synthesis += f"SWOT ANALYSIS:\n{swot_insights}\n\n"
    if retrieved and "[ChromaDB Error]" not in retrieved and "No documents" not in retrieved:
        synthesis += f"DOCUMENT CONTEXT:\n{retrieved}\n\n"

    if not synthesis.strip():
        synthesis = "No specific feature data available. Provide a general prioritization framework."

    messages = [
        {
            "role": "user",
            "content": (
                f"Using the following inputs:\n\n{synthesis}\n\n"
                "Produce a Feature Prioritization Report:\n\n"
                "1. HIGH PRIORITY features (must-have, high impact)\n"
                "   - Feature name, reason, estimated impact\n\n"
                "2. MEDIUM PRIORITY features (should-have)\n"
                "   - Feature name, reason, estimated impact\n\n"
                "3. LOW PRIORITY / BACKLOG features\n"
                "   - Feature name, reason\n\n"
                "4. Suggested 3-month roadmap focus\n\n"
                "Use RICE scoring rationale where applicable."
            ),
        }
    ]

    return chat_completion(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)
