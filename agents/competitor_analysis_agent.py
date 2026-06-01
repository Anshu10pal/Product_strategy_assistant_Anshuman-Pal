"""
Agent 3: Competitor Analysis Agent
Evaluates competitive landscape, positioning, and differentiation opportunities.
"""

from utils.llm_client import chat_completion
from utils.vector_store import query_documents

SYSTEM_PROMPT = """You are a Competitive Intelligence Analyst specializing in product strategy.
Your role is to analyze competitor information and identify:
- Key competitors and their positioning
- Competitive strengths and weaknesses
- Feature gaps and differentiation opportunities
- Pricing and go-to-market strategies
- Areas where our product can win

Provide sharp, actionable competitive intelligence. Be concise and structured."""


def run_competitor_analysis_agent(context: str = "", customer_insights: str = "") -> str:
    """
    Analyze competitor landscape from ingested documents.
    Optionally uses customer insights to frame competitive gaps.
    Returns competitor analysis string.
    """
    retrieved = query_documents(
        "competitor analysis market share pricing features comparison differentiation",
        n_results=6,
    )

    combined_context = ""
    if context:
        combined_context += f"Additional context:\n{context}\n\n"
    if retrieved and "[ChromaDB Error]" not in retrieved and "No documents" not in retrieved:
        combined_context += f"Relevant document excerpts:\n{retrieved}\n\n"
    if customer_insights:
        combined_context += f"Customer insights (from previous agent):\n{customer_insights}\n\n"

    if not combined_context.strip():
        combined_context = "No specific competitor data uploaded. Provide a general competitive analysis framework."

    messages = [
        {
            "role": "user",
            "content": (
                f"Perform a competitive analysis based on:\n\n{combined_context}\n\n"
                "Provide:\n"
                "1. Top Competitors Overview\n"
                "2. Competitive Strengths vs Our Product\n"
                "3. Competitor Weaknesses / Gaps\n"
                "4. Our Differentiation Opportunities\n"
                "5. Competitive Threats to Watch"
            ),
        }
    ]

    return chat_completion(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)
