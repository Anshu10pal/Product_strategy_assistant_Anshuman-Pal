"""
Agent 6: Executive Report Agent
Synthesizes all agent outputs into an executive summary and strategic action plan.
"""

from utils.llm_client import chat_completion

SYSTEM_PROMPT = """You are a Chief Product Officer preparing a board-level executive briefing.
Your role is to synthesize inputs from multiple analysts and produce:
- A crisp executive summary
- Top 3 strategic priorities
- A clear action plan with timelines
- Key risks and mitigations
- Success metrics (KPIs)

Write in clear, executive-level language. Be decisive and recommendation-driven.
Every paragraph must add value. No filler."""


def run_executive_report_agent(
    customer_insights: str = "",
    market_insights: str = "",
    competitor_insights: str = "",
    swot_insights: str = "",
    feature_insights: str = "",
) -> dict:
    """
    Generate executive summary and strategic recommendations.
    Returns dict with 'executive_summary' and 'strategy_recommendations'.
    """
    synthesis = ""
    if customer_insights:
        synthesis += f"CUSTOMER ANALYSIS:\n{customer_insights}\n\n"
    if market_insights:
        synthesis += f"MARKET RESEARCH:\n{market_insights}\n\n"
    if competitor_insights:
        synthesis += f"COMPETITOR ANALYSIS:\n{competitor_insights}\n\n"
    if swot_insights:
        synthesis += f"SWOT ANALYSIS:\n{swot_insights}\n\n"
    if feature_insights:
        synthesis += f"FEATURE PRIORITIES:\n{feature_insights}\n\n"

    if not synthesis.strip():
        synthesis = "No specific data available. Generate a general product strategy executive summary."

    # Executive Summary
    exec_messages = [
        {
            "role": "user",
            "content": (
                f"Based on all analysis below:\n\n{synthesis}\n\n"
                "Write a concise Executive Summary (200 words max) covering:\n"
                "- Current product situation\n"
                "- Key findings\n"
                "- Most critical opportunity\n"
                "- Recommended strategic direction"
            ),
        }
    ]
    executive_summary = chat_completion(exec_messages, system_prompt=SYSTEM_PROMPT, temperature=0.2)

    # Strategic Recommendations
    strategy_messages = [
        {
            "role": "user",
            "content": (
                f"Based on all analysis:\n\n{synthesis}\n\n"
                "Produce a Strategic Action Plan:\n"
                "1. Top 3 Strategic Priorities (with rationale)\n"
                "2. 90-day Action Plan (quick wins)\n"
                "3. 6-month Initiatives\n"
                "4. Key Risks & Mitigations\n"
                "5. Success KPIs to track"
            ),
        }
    ]
    strategy_recommendations = chat_completion(strategy_messages, system_prompt=SYSTEM_PROMPT, temperature=0.2)

    return {
        "executive_summary": executive_summary,
        "strategy_recommendations": strategy_recommendations,
    }
