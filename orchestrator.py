"""
LangGraph Multi-Agent Orchestrator
Defines the agent workflow as a directed state graph.

Graph flow:
  ingest → customer_feedback → market_research → competitor_analysis
         → swot_analysis → feature_prioritization → executive_report → END
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agents.customer_feedback_agent import run_customer_feedback_agent
from agents.market_research_agent import run_market_research_agent
from agents.competitor_analysis_agent import run_competitor_analysis_agent
from agents.swot_agent import run_swot_agent
from agents.feature_prioritization_agent import run_feature_prioritization_agent
from agents.executive_report_agent import run_executive_report_agent


# ── State schema ────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    # User-provided
    user_context: Optional[str]

    # Agent outputs
    customer_feedback: Optional[str]
    market_research: Optional[str]
    competitor_analysis: Optional[str]
    swot_analysis: Optional[str]
    feature_prioritization: Optional[str]
    executive_summary: Optional[str]
    strategy_recommendations: Optional[str]

    # Pipeline status
    current_step: Optional[str]
    error: Optional[str]


# ── Node functions ───────────────────────────────────────────────────────────

def node_customer_feedback(state: AgentState) -> AgentState:
    try:
        result = run_customer_feedback_agent(context=state.get("user_context", ""))
        return {**state, "customer_feedback": result, "current_step": "customer_feedback"}
    except Exception as e:
        return {**state, "error": f"Customer feedback agent error: {e}", "current_step": "customer_feedback"}


def node_market_research(state: AgentState) -> AgentState:
    try:
        result = run_market_research_agent(context=state.get("user_context", ""))
        return {**state, "market_research": result, "current_step": "market_research"}
    except Exception as e:
        return {**state, "error": f"Market research agent error: {e}", "current_step": "market_research"}


def node_competitor_analysis(state: AgentState) -> AgentState:
    try:
        result = run_competitor_analysis_agent(
            context=state.get("user_context", ""),
            customer_insights=state.get("customer_feedback", ""),
        )
        return {**state, "competitor_analysis": result, "current_step": "competitor_analysis"}
    except Exception as e:
        return {**state, "error": f"Competitor analysis agent error: {e}", "current_step": "competitor_analysis"}


def node_swot_analysis(state: AgentState) -> AgentState:
    try:
        result = run_swot_agent(
            customer_insights=state.get("customer_feedback", ""),
            market_insights=state.get("market_research", ""),
            competitor_insights=state.get("competitor_analysis", ""),
        )
        return {**state, "swot_analysis": result, "current_step": "swot_analysis"}
    except Exception as e:
        return {**state, "error": f"SWOT agent error: {e}", "current_step": "swot_analysis"}


def node_feature_prioritization(state: AgentState) -> AgentState:
    try:
        result = run_feature_prioritization_agent(
            customer_insights=state.get("customer_feedback", ""),
            swot_insights=state.get("swot_analysis", ""),
            market_insights=state.get("market_research", ""),
        )
        return {**state, "feature_prioritization": result, "current_step": "feature_prioritization"}
    except Exception as e:
        return {**state, "error": f"Feature prioritization agent error: {e}", "current_step": "feature_prioritization"}


def node_executive_report(state: AgentState) -> AgentState:
    try:
        result = run_executive_report_agent(
            customer_insights=state.get("customer_feedback", ""),
            market_insights=state.get("market_research", ""),
            competitor_insights=state.get("competitor_analysis", ""),
            swot_insights=state.get("swot_analysis", ""),
            feature_insights=state.get("feature_prioritization", ""),
        )
        return {
            **state,
            "executive_summary": result.get("executive_summary", ""),
            "strategy_recommendations": result.get("strategy_recommendations", ""),
            "current_step": "executive_report",
        }
    except Exception as e:
        return {**state, "error": f"Executive report agent error: {e}", "current_step": "executive_report"}


# ── Build graph ──────────────────────────────────────────────────────────────

def build_agent_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("step_customer_feedback", node_customer_feedback)
    graph.add_node("step_market_research", node_market_research)
    graph.add_node("step_competitor_analysis", node_competitor_analysis)
    graph.add_node("step_swot_analysis", node_swot_analysis)
    graph.add_node("step_feature_prioritization", node_feature_prioritization)
    graph.add_node("step_executive_report", node_executive_report)

    # Linear pipeline
    graph.set_entry_point("step_customer_feedback")
    graph.add_edge("step_customer_feedback", "step_market_research")
    graph.add_edge("step_market_research", "step_competitor_analysis")
    graph.add_edge("step_competitor_analysis", "step_swot_analysis")
    graph.add_edge("step_swot_analysis", "step_feature_prioritization")
    graph.add_edge("step_feature_prioritization", "step_executive_report")
    graph.add_edge("step_executive_report", END)

    return graph.compile()


def run_full_pipeline(user_context: str = "") -> AgentState:
    """
    Run the full multi-agent pipeline.
    Returns the final AgentState with all agent outputs.
    """
    app = build_agent_graph()
    initial_state: AgentState = {
        "user_context": user_context,
        "customer_feedback": None,
        "market_research": None,
        "competitor_analysis": None,
        "swot_analysis": None,
        "feature_prioritization": None,
        "executive_summary": None,
        "strategy_recommendations": None,
        "current_step": "start",
        "error": None,
    }
    final_state = app.invoke(initial_state)
    return final_state
