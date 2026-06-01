"""
Agent 1: Customer Feedback Agent
Analyzes customer reviews, survey responses, and feedback data.
"""

from utils.llm_client import chat_completion
from utils.vector_store import query_documents

SYSTEM_PROMPT = """You are a senior Customer Insights Analyst specializing in product strategy.
Your role is to analyze customer feedback, reviews, and survey data to extract:
- Key pain points and frustrations
- Most requested features
- Sentiment trends (positive/negative/neutral)
- Customer satisfaction drivers
- Churn risks and loyalty signals

Be concise, structured, and data-driven. Use bullet points where appropriate.
Limit your response to the most impactful insights."""


def run_customer_feedback_agent(context: str = "") -> str:
    """
    Analyze customer feedback from ingested documents.
    Returns structured insights string.
    """
    # Retrieve relevant chunks from vector store
    retrieved = query_documents(
        "customer feedback reviews complaints satisfaction feature requests",
        n_results=6,
    )

    combined_context = ""
    if context:
        combined_context += f"Additional context:\n{context}\n\n"
    if retrieved and "[ChromaDB Error]" not in retrieved and "No documents" not in retrieved:
        combined_context += f"Relevant document excerpts:\n{retrieved}"

    if not combined_context.strip():
        combined_context = "No specific data uploaded. Provide general framework for customer analysis."

    messages = [
        {
            "role": "user",
            "content": (
                f"Analyze the following customer data and provide structured insights:\n\n"
                f"{combined_context}\n\n"
                "Produce:\n"
                "1. Top 3 Pain Points\n"
                "2. Top Feature Requests\n"
                "3. Overall Sentiment Summary\n"
                "4. Key Customer Segments\n"
                "5. Actionable Recommendations"
            ),
        }
    ]

    return chat_completion(messages, system_prompt=SYSTEM_PROMPT, temperature=0.3)
