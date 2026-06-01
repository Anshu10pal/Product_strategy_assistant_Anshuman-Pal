"""
Streamlit Frontend: AI-Powered Product Strategy Assistant
"""

import os
import time
import requests
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────────

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Product Strategy Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 1rem; }

    .agent-card {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .agent-card h4 { margin: 0 0 0.4rem; color: #1e3a8a; font-size: 1rem; }
    .agent-card p  { margin: 0; font-size: 0.88rem; color: #374151; }

    .metric-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
    }
    .metric-box .val { font-size: 1.8rem; font-weight: 700; color: #1e3a8a; }
    .metric-box .lbl { font-size: 0.8rem; color: #6b7280; }

    .status-ok   { color: #16a34a; font-weight: 600; }
    .status-warn { color: #d97706; font-weight: 600; }

    div[data-testid="stChatMessage"] { border-radius: 10px; margin-bottom: 0.5rem; }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────

for key, default in {
    "chat_history": [],
    "analysis_results": {},
    "doc_count": 0,
    "analysis_done": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helper functions ──────────────────────────────────────────────────────────

def api_status():
    try:
        r = requests.get(f"{API_BASE}/status", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def upload_files(files):
    try:
        file_tuples = [("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in files]
        r = requests.post(f"{API_BASE}/upload", files=file_tuples, timeout=60)
        return r.json() if r.status_code == 200 else {"success": False, "error": r.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_analysis(context: str = ""):
    try:
        r = requests.post(f"{API_BASE}/analyze", json={"context": context}, timeout=300)
        return r.json() if r.status_code == 200 else {"success": False, "error": r.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_chat(message: str, history: list):
    try:
        r = requests.post(
            f"{API_BASE}/chat",
            json={"message": message, "chat_history": history[-10:]},  # last 10 turns
            timeout=60,
        )
        return r.json().get("response", "No response") if r.status_code == 200 else f"Error: {r.text}"
    except Exception as e:
        return f"Error: {str(e)}"


def download_pdf():
    try:
        r = requests.post(f"{API_BASE}/report/pdf", timeout=120)
        if r.status_code == 200:
            return r.content
        return None
    except Exception:
        return None


def clear_docs():
    try:
        r = requests.delete(f"{API_BASE}/documents", timeout=30)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


# ── Header ─────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🧠 Product Strategy Assistant</h1>
    <p>AI-powered multi-agent analysis for data-driven product decisions</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ System Status")

    status = api_status()
    if status:
        st.markdown('<span class="status-ok">● API Connected</span>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="val">{status.get("documents_ingested", 0)}</div><div class="lbl">Doc Chunks</div></div>', unsafe_allow_html=True)
        with col2:
            analysis_icon = "✅" if status.get("analysis_ready") else "⏳"
            st.markdown(f'<div class="metric-box"><div class="val">{analysis_icon}</div><div class="lbl">Analysis</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-warn">● API Offline — start backend</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🤖 Agent Pipeline")
    agents = [
        ("👥", "Customer Feedback", "Pain points, sentiment, requests"),
        ("📊", "Market Research", "Trends, segments, opportunities"),
        ("⚔️", "Competitor Analysis", "Gaps, threats, differentiation"),
        ("🔷", "SWOT Analysis", "Strengths, weaknesses, threats"),
        ("🎯", "Feature Prioritization", "RICE scoring, roadmap"),
        ("📋", "Executive Report", "Summary, strategy, KPIs"),
    ]
    for icon, name, desc in agents:
        st.markdown(f"""
        <div class="agent-card">
            <h4>{icon} {name}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    if st.button("🗑️ Clear All Documents", use_container_width=True, type="secondary"):
        if clear_docs():
            st.session_state.analysis_results = {}
            st.session_state.analysis_done = False
            st.session_state.doc_count = 0
            st.success("Documents cleared.")
            time.sleep(1)
            st.rerun()


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📂 Upload & Analyze", "📊 Analysis Results", "📈 Dashboard", "💬 Chat", "ℹ️ About"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Upload & Analyze
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("📂 Upload Data Sources")
        st.caption("Supported: CSV, TXT, JSON, PDF")

        uploaded_files = st.file_uploader(
            "Drop files here",
            accept_multiple_files=True,
            type=["csv", "txt", "json", "pdf", "md"],
            label_visibility="collapsed",
        )

        if uploaded_files:
            if st.button("⬆️ Ingest Documents", type="primary", use_container_width=True):
                with st.spinner("Parsing and ingesting into ChromaDB..."):
                    result = upload_files(uploaded_files)

                if result.get("success"):
                    st.success(f"✅ Ingested {result['files_processed']} file(s) → {result['chunks_added']} chunks added")
                    st.session_state.doc_count = result.get("total_chunks_in_store", 0)
                    for f in result.get("files", []):
                        st.markdown(f"- `{f['filename']}` ({f['doc_type']}, {f['size_bytes']:,} bytes)")
                else:
                    st.error(f"Upload failed: {result.get('error', 'Unknown error')}")

        # Sample data note
        st.info("💡 **Tip:** Place your `sample_sales.csv` in the `data/` folder and upload it here, or use the pre-loaded path below.")

        sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_sales.csv")
        if os.path.exists(sample_path):
            st.success(f"✅ Sample dataset found at `data/sample_sales.csv`")
            if st.button("📥 Auto-Load Sample Sales Data", use_container_width=True):
                with open(sample_path, "rb") as f:
                    csv_bytes = f.read()
                with st.spinner("Loading sample data..."):
                    from utils.document_parser import parse_file
                    from utils.vector_store import ingest_documents
                    content, doc_type = parse_file(csv_bytes, "sample_sales.csv")
                    ingest_documents([{"content": content, "source": "sample_sales.csv", "doc_type": doc_type}])
                st.success("Sample sales data loaded into vector store!")

    with col_right:
        st.subheader("🚀 Run Analysis")

        context_input = st.text_area(
            "Optional: Add context or focus area",
            placeholder="e.g. 'Focus on B2B SaaS market' or 'Highlight churn risks'",
            height=100,
        )

        st.markdown("**What the pipeline will do:**")
        steps = [
            "1️⃣ Analyze customer feedback & sentiment",
            "2️⃣ Research market trends & opportunities",
            "3️⃣ Map competitive landscape",
            "4️⃣ Generate SWOT analysis",
            "5️⃣ Prioritize features with RICE scoring",
            "6️⃣ Produce executive summary & strategy",
        ]
        for step in steps:
            st.markdown(f"<small>{step}</small>", unsafe_allow_html=True)

        st.markdown("")
        if st.button("▶️ Run Full Analysis", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()

            agent_steps = [
                (15,  "🔍 Agent 1: Analyzing customer feedback..."),
                (30,  "📊 Agent 2: Researching market trends..."),
                (48,  "⚔️ Agent 3: Mapping competitive landscape..."),
                (63,  "🔷 Agent 4: Running SWOT analysis..."),
                (78,  "🎯 Agent 5: Prioritizing features..."),
                (92,  "📋 Agent 6: Generating executive report..."),
                (100, "✅ Analysis complete!"),
            ]

            def progress_callback():
                for pct, msg in agent_steps:
                    status_text.markdown(f"**{msg}**")
                    progress_bar.progress(pct)
                    time.sleep(0.3)

            import threading
            t = threading.Thread(target=progress_callback)
            t.start()

            result = run_analysis(context=context_input)
            t.join()

            if result.get("success"):
                st.session_state.analysis_results = result.get("analysis", {})
                st.session_state.analysis_done = True
                st.success("🎉 Analysis complete! View results in the **Analysis Results** tab.")
            else:
                st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
                progress_bar.empty()
                status_text.empty()

        if st.session_state.analysis_done:
            st.divider()
            st.markdown("### 📄 Download Report")
            if st.button("📥 Generate & Download PDF Report", use_container_width=True, type="secondary"):
                with st.spinner("Generating PDF..."):
                    pdf_bytes = download_pdf()
                if pdf_bytes:
                    st.download_button(
                        label="💾 Click to Save PDF",
                        data=pdf_bytes,
                        file_name="product_strategy_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.error("PDF generation failed. Check backend logs.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Analysis Results
# ══════════════════════════════════════════════════════════════════════════════

with tab2:
    if not st.session_state.analysis_done:
        st.info("No analysis available yet. Go to **Upload & Analyze** tab and run the pipeline.")
    else:
        results = st.session_state.analysis_results

        # Executive Summary at top
        exec_summary = results.get("executive_summary", "")
        if exec_summary:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#1e3a8a,#3b82f6);
                        color:white;padding:1.2rem 1.5rem;border-radius:10px;margin-bottom:1.5rem">
                <h3 style="margin:0 0 0.5rem">📋 Executive Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(exec_summary)
            st.divider()

        # Two-column grid for agent results
        col_a, col_b = st.columns(2, gap="medium")
        sections = [
            ("col_a", "👥 Customer Feedback Analysis",   "customer_feedback"),
            ("col_b", "📊 Market Research",              "market_research"),
            ("col_a", "⚔️ Competitor Analysis",          "competitor_analysis"),
            ("col_b", "🔷 SWOT Analysis",                "swot_analysis"),
            ("col_a", "🎯 Feature Prioritization",       "feature_prioritization"),
            ("col_b", "🗺️ Strategic Recommendations",    "strategy_recommendations"),
        ]

        for col_target, title, key in sections:
            content = results.get(key, "")
            if content:
                target_col = col_a if col_target == "col_a" else col_b
                with target_col:
                    with st.expander(title, expanded=True):
                        st.markdown(content)

        # PDF download button
        st.divider()
        col_dl, _ = st.columns([1, 2])
        with col_dl:
            if st.button("📄 Download Full PDF Report", type="primary", use_container_width=True):
                with st.spinner("Generating PDF report..."):
                    pdf_bytes = download_pdf()
                if pdf_bytes:
                    st.download_button(
                        label="💾 Save PDF Report",
                        data=pdf_bytes,
                        file_name="product_strategy_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.error("PDF generation failed.")


# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Dashboard
# ══════════════════════════════════════════════════════════════════════════════

with tab3:
    st.subheader("📈 Data Analytics Dashboard")

    import os as _os
    import pandas as _pd

    DATA_PATH = _os.path.join(_os.path.dirname(__file__), "data", "sample_sales.csv")

    @st.cache_data
    def load_data(path):
        return _pd.read_csv(path)

    if not _os.path.exists(DATA_PATH):
        st.warning("No CSV found at data/sample_sales.csv. Upload a CSV in the Upload tab first.")
    else:
        try:
            import plotly.express as px
            import plotly.graph_objects as go
        except ImportError:
            st.error("Run: pip install plotly")
            st.stop()

        df = load_data(DATA_PATH)

        # ── KPI row ──────────────────────────────────────────────────────────
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Total Revenue",    f"${df['revenue'].sum():,.0f}")
        k2.metric("Total Orders",     f"{len(df):,}")
        k3.metric("Avg Order Value",  f"${df['revenue'].mean():,.0f}")
        k4.metric("Avg Rating",       f"{df['rating'].mean():.2f} / 5")
        k5.metric("High Churn Risk",  f"{(df['churn_risk']=='High').sum()} orders")

        st.divider()

        # ── Row 1: Revenue by Category | Revenue by Region ───────────────────
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(
                df.groupby("category")["revenue"].sum().reset_index(),
                x="category", y="revenue", color="category",
                title="Revenue by Category",
                labels={"revenue": "Revenue ($)", "category": "Category"},
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig = px.pie(
                df.groupby("region")["revenue"].sum().reset_index(),
                names="region", values="revenue",
                title="Revenue by Region",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4,
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        # ── Row 2: Monthly Revenue Trend | Rating Distribution ────────────────
        c3, c4 = st.columns(2)
        with c3:
            df["month"] = _pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
            monthly = df.groupby("month")["revenue"].sum().reset_index()
            fig = px.line(
                monthly, x="month", y="revenue",
                title="Monthly Revenue Trend",
                labels={"revenue": "Revenue ($)", "month": "Month"},
                markers=True, line_shape="spline",
            )
            fig.update_traces(line_color="#3b82f6", fill="tozeroy", fillcolor="rgba(59,130,246,0.1)")
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with c4:
            fig = px.histogram(
                df, x="rating", nbins=5,
                title="Customer Rating Distribution",
                labels={"rating": "Rating", "count": "Count"},
                color_discrete_sequence=["#6366f1"],
            )
            fig.update_layout(height=350, bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

        # ── Row 3: Churn Risk | Top Products ─────────────────────────────────
        c5, c6 = st.columns(2)
        with c5:
            churn_counts = df["churn_risk"].value_counts().reset_index()
            churn_counts.columns = ["churn_risk", "count"]
            color_map = {"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"}
            fig = px.bar(
                churn_counts, x="churn_risk", y="count",
                title="Churn Risk Distribution",
                color="churn_risk", color_discrete_map=color_map,
                labels={"count": "Orders", "churn_risk": "Risk Level"},
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)

        with c6:
            top_products = df.groupby("product_name")["revenue"].sum().sort_values(ascending=True).reset_index()
            fig = px.bar(
                top_products, x="revenue", y="product_name",
                orientation="h", title="Revenue by Product",
                labels={"revenue": "Revenue ($)", "product_name": "Product"},
                color="revenue", color_continuous_scale="Blues",
            )
            fig.update_layout(height=350, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        # ── Row 4: Revenue by Customer Type | Top Feature Requests ───────────
        c7, c8 = st.columns(2)
        with c7:
            fig = px.pie(
                df.groupby("customer_type")["revenue"].sum().reset_index(),
                names="customer_type", values="revenue",
                title="Revenue by Customer Type",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.35,
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with c8:
            top_features = df["feature_request"].value_counts().head(8).reset_index()
            top_features.columns = ["feature", "count"]
            fig = px.bar(
                top_features, x="count", y="feature",
                orientation="h", title="Top Feature Requests",
                labels={"count": "Requests", "feature": "Feature"},
                color="count", color_continuous_scale="Teal",
            )
            fig.update_layout(height=350, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        # ── Row 5: Avg Rating by Product ──────────────────────────────────────
        avg_rating = df.groupby("product_name")["rating"].mean().reset_index()
        fig = px.bar(
            avg_rating, x="product_name", y="rating",
            title="Average Customer Rating by Product",
            color="rating", color_continuous_scale="RdYlGn",
            range_y=[0, 5],
            labels={"rating": "Avg Rating", "product_name": "Product"},
        )
        fig.add_hline(y=df["rating"].mean(), line_dash="dash",
                      line_color="gray", annotation_text="Overall Avg")
        fig.update_layout(height=380, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)



# TAB 3 — Chat
# ══════════════════════════════════════════════════════════════════════════════

with tab4:
    st.subheader("💬 Chat with Your Product Data")
    st.caption("Ask questions about your uploaded documents and analysis results.")

    # Suggested prompts
    st.markdown("**Suggested prompts:**")
    suggestion_cols = st.columns(3)
    suggestions = [
        "What are the top customer pain points?",
        "Which features should we prioritize first?",
        "What is our biggest competitive threat?",
        "Summarize the market opportunities",
        "What does the SWOT analysis tell us?",
        "What are the recommended KPIs to track?",
    ]
    for i, sugg in enumerate(suggestions):
        with suggestion_cols[i % 3]:
            if st.button(sugg, key=f"sugg_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": sugg})
                with st.spinner("Thinking..."):
                    response = send_chat(sugg, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    st.divider()

    # Chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask about your product data, market, or strategy..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = send_chat(prompt, st.session_state.chat_history[:-1])
            st.markdown(response)

        st.session_state.chat_history.append({"role": "assistant", "content": response})

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — About
# ══════════════════════════════════════════════════════════════════════════════

with tab5:
    st.subheader("ℹ️ About This Application")
    st.markdown("""
    ### AI-Powered Product Strategy Assistant

    This application uses a **6-agent LangGraph pipeline** to transform raw business data
    into actionable product strategy insights.

    ---

    #### 🏗️ Architecture

    | Layer | Technology |
    |-------|-----------|
    | LLM | GPT-4o Mini (OpenAI-compatible endpoint) |
    | Agent Framework | LangGraph + LangChain |
    | Vector Database | ChromaDB (local persistent) |
    | Backend | FastAPI |
    | Frontend | Streamlit |
    | PDF Generation | fpdf2 |

    ---

    #### 🤖 Agent Pipeline

    ```
    Upload Docs → ChromaDB
                     ↓
    [Agent 1] Customer Feedback Analysis
                     ↓
    [Agent 2] Market Research
                     ↓
    [Agent 3] Competitor Analysis
                     ↓
    [Agent 4] SWOT Synthesis
                     ↓
    [Agent 5] Feature Prioritization (RICE)
                     ↓
    [Agent 6] Executive Report Generation
                     ↓
               PDF Download
    ```

    ---

    #### 📁 Data Input Location

    Place your sample sales CSV at:
    ```
    product_strategy_assistant/data/sample_sales.csv
    ```

    ---

    #### 🚀 How to Run

    ```bash
    # Install dependencies
    pip install -r requirements.txt

    # Set environment variables
    cp .env.example .env
    # Edit .env with your API key

    # Start backend
    uvicorn main:app --reload --port 8000

    # Start frontend (new terminal)
    streamlit run app.py
    ```
    """)
