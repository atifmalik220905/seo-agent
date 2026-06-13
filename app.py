import streamlit as st
import os
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from index import read_urls, read_urls_from_text, audit_single, run_batch, INPUT_CSV
from state import load_state, reset_state
from reporter import get_report_data, REPORT_JSON

st.set_page_config(
    page_title="SEO Audit Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    .main-header h1 {
        color: #ffffff;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    .main-header p {
        color: #a8a4ce;
        font-size: 1.1rem;
        font-weight: 300;
    }

    .metric-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 500;
    }

    .pass-color { color: #64ffda; }
    .fail-color { color: #ff6b6b; }
    .skip-color { color: #ffd93d; }
    .total-color { color: #74b9ff; }

    .status-pass {
        background: rgba(100, 255, 218, 0.15);
        color: #64ffda;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-fail {
        background: rgba(255, 107, 107, 0.15);
        color: #ff6b6b;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-error {
        background: rgba(255, 217, 61, 0.15);
        color: #ffd93d;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .url-card {
        background: linear-gradient(145deg, #1e1e30, #252540);
        padding: 1.25rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        transition: transform 0.15s ease;
    }

    .url-card:hover {
        transform: translateX(4px);
    }

    .url-card-pass { border-left-color: #64ffda; }
    .url-card-fail { border-left-color: #ff6b6b; }

    .sidebar-section {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .detail-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.75rem;
        margin-top: 1rem;
    }

    .detail-item {
        background: rgba(255, 255, 255, 0.03);
        padding: 0.75rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .detail-label {
        font-size: 0.75rem;
        color: #8892b0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.25rem;
    }

    .detail-value {
        font-size: 0.95rem;
        color: #ccd6f6;
        word-break: break-all;
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1a, #141428);
        min-width: 500px;
        max-width: 500px;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transform: translateY(-1px);
    }

    .flags-container {
        margin-top: 0.75rem;
    }

    .flag-item {
        background: rgba(255, 107, 107, 0.08);
        border: 1px solid rgba(255, 107, 107, 0.2);
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        color: #ff9999;
    }

    .broken-link {
        background: rgba(255, 217, 61, 0.08);
        border: 1px solid rgba(255, 217, 61, 0.2);
        padding: 0.4rem 0.75rem;
        border-radius: 6px;
        margin-bottom: 0.3rem;
        font-size: 0.8rem;
        color: #ffd93d;
        word-break: break-all;
    }

    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #8892b0;
    }

    .empty-state h3 {
        color: #ccd6f6;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🔍 SEO Audit Agent</h1>
    <p>Automated SEO analysis powered by Groq AI</p>
</div>
""", unsafe_allow_html=True)

api_key = os.environ.get("GROQ_API_KEY", "")

with st.sidebar:
    if api_key:
        st.success("✅ Groq API key loaded from .env")
    else:
        st.error("❌ GROQ_API_KEY not found in .env file")

    st.markdown("---")
    st.markdown("### 📥 Input URLs")

    input_method = st.radio(
        "Choose input method",
        ["Paste URLs", "Upload CSV"],
        label_visibility="collapsed",
    )

    urls_to_audit = []

    if input_method == "Paste URLs":
        url_text = st.text_area(
            "Enter URLs (one per line)",
            height=200,
            placeholder="https://example.com\nhttps://another-site.com",
        )
        if url_text.strip():
            urls_to_audit = read_urls_from_text(url_text)

    else:
        uploaded = st.file_uploader("Upload CSV with 'url' column", type=["csv"])
        if uploaded is not None:
            import io
            content = uploaded.read().decode("utf-8")
            with open(INPUT_CSV, "w", encoding="utf-8") as f:
                f.write(content)
            urls_to_audit = read_urls(INPUT_CSV)

    if urls_to_audit:
        st.markdown(f"**{len(urls_to_audit)} URLs** ready to audit")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        start_audit = st.button("🚀 Start Audit", disabled=(not urls_to_audit or not api_key))
    with col2:
        clear_data = st.button("🗑️ Clear Data")

    if clear_data:
        reset_state()
        if os.path.exists(REPORT_JSON):
            os.remove(REPORT_JSON)
        report_txt = REPORT_JSON.replace(".json", "-summary.txt")
        if os.path.exists(report_txt):
            os.remove(report_txt)
        st.rerun()

report_data = get_report_data()

if start_audit and urls_to_audit and api_key:
    progress_bar = st.progress(0, text="Initializing audit...")
    status_container = st.empty()
    results = []

    for i, url in enumerate(urls_to_audit):
        progress = (i) / len(urls_to_audit)
        progress_bar.progress(progress, text=f"Auditing {i+1}/{len(urls_to_audit)}: {url}")

        with status_container.container():
            st.info(f"🔄 Currently analyzing: **{url}**")

        result = audit_single(url)
        results.append(result)

    progress_bar.progress(1.0, text="Audit complete!")
    status_container.empty()
    st.balloons()
    report_data = get_report_data()
    st.rerun()

if report_data:
    total = len(report_data)
    passed = sum(1 for r in report_data if all(
        r.get(f, {}).get("status") == "PASS"
        for f in ["title", "description", "h1", "canonical"]
    ) and r.get("broken_links", {}).get("status") != "FAIL")
    failed = total - passed

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value total-color">{total}</div>
            <div class="metric-label">Total Audited</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value pass-color">{passed}</div>
            <div class="metric-label">Passed</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value fail-color">{failed}</div>
            <div class="metric-label">Failed</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        pass_rate = (passed / total * 100) if total > 0 else 0
        rate_color = "pass-color" if pass_rate >= 70 else "fail-color"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {rate_color}">{pass_rate:.0f}%</div>
            <div class="metric-label">Pass Rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Results Overview", "📊 Detailed Analysis", "📥 Export"])

    with tab1:
        for entry in report_data:
            url = entry.get("url", "unknown")
            is_pass = all(
                entry.get(f, {}).get("status") == "PASS"
                for f in ["title", "description", "h1", "canonical"]
            ) and entry.get("broken_links", {}).get("status") != "FAIL"

            status_class = "url-card-pass" if is_pass else "url-card-fail"
            status_badge = '<span class="status-pass">PASS</span>' if is_pass else '<span class="status-fail">FAIL</span>'

            flags = entry.get("flags", [])
            flags_html = ""
            if flags:
                flags_html = '<div class="flags-container">'
                for flag in flags:
                    flags_html += f'<div class="flag-item">⚠ {flag}</div>'
                flags_html += '</div>'

            broken = entry.get("broken_links", {}).get("broken", [])
            broken_html = ""
            if broken:
                broken_html = '<div class="flags-container">'
                for bl in broken[:5]:
                    broken_html += f'<div class="broken-link">🔗 {bl}</div>'
                if len(broken) > 5:
                    broken_html += f'<div class="broken-link">... and {len(broken)-5} more</div>'
                broken_html += '</div>'

            fields_html = ""
            for field in ["title", "description", "h1", "canonical"]:
                field_data = entry.get(field, {})
                field_status = field_data.get("status", "N/A")
                if field_status == "PASS":
                    badge = '<span class="status-pass">PASS</span>'
                elif field_status == "FAIL":
                    badge = '<span class="status-fail">FAIL</span>'
                else:
                    badge = '<span class="status-error">ERROR</span>'
                fields_html += f' {badge} {field.capitalize()} &nbsp;'

            st.markdown(f"""
            <div class="url-card {status_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="color: #ccd6f6; font-weight: 500; font-size: 0.95rem; word-break: break-all;">{url}</div>
                    <div>{status_badge}</div>
                </div>
                <div style="margin-bottom: 0.5rem;">{fields_html}</div>
                {flags_html}
                {broken_html}
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        for entry in report_data:
            url = entry.get("url", "unknown")
            with st.expander(f"🔍 {url}", expanded=False):
                dcol1, dcol2 = st.columns(2)

                with dcol1:
                    st.markdown("**Title**")
                    title_data = entry.get("title", {})
                    st.code(title_data.get("value", "N/A"))
                    tcol1, tcol2 = st.columns(2)
                    with tcol1:
                        st.metric("Length", title_data.get("length", 0))
                    with tcol2:
                        st.metric("Status", title_data.get("status", "N/A"))

                    st.markdown("**H1 Tag**")
                    h1_data = entry.get("h1", {})
                    st.code(h1_data.get("value", "N/A"))
                    hcol1, hcol2 = st.columns(2)
                    with hcol1:
                        st.metric("Count", h1_data.get("count", 0))
                    with hcol2:
                        st.metric("Status", h1_data.get("status", "N/A"))

                with dcol2:
                    st.markdown("**Meta Description**")
                    desc_data = entry.get("description", {})
                    st.code(desc_data.get("value", "N/A"))
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric("Length", desc_data.get("length", 0))
                    with mcol2:
                        st.metric("Status", desc_data.get("status", "N/A"))

                    st.markdown("**Canonical**")
                    canon_data = entry.get("canonical", {})
                    st.code(canon_data.get("value", "N/A"))
                    st.metric("Status", canon_data.get("status", "N/A"))

                broken_data = entry.get("broken_links", {})
                if broken_data.get("broken"):
                    st.markdown("**Broken Links**")
                    for bl in broken_data["broken"]:
                        st.warning(bl)

    with tab3:
        st.markdown("### Download Results")

        col1, col2 = st.columns(2)

        with col1:
            json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
            st.download_button(
                "📄 Download JSON Report",
                data=json_str,
                file_name="seo_audit_report.json",
                mime="application/json",
            )

        with col2:
            if report_data:
                rows = []
                for entry in report_data:
                    rows.append({
                        "URL": entry.get("url", ""),
                        "Status Code": entry.get("status_code", ""),
                        "Title": entry.get("title", {}).get("value", ""),
                        "Title Length": entry.get("title", {}).get("length", ""),
                        "Title Status": entry.get("title", {}).get("status", ""),
                        "Description": entry.get("description", {}).get("value", ""),
                        "Description Length": entry.get("description", {}).get("length", ""),
                        "Description Status": entry.get("description", {}).get("status", ""),
                        "H1": entry.get("h1", {}).get("value", ""),
                        "H1 Count": entry.get("h1", {}).get("count", ""),
                        "H1 Status": entry.get("h1", {}).get("status", ""),
                        "Canonical": entry.get("canonical", {}).get("value", ""),
                        "Canonical Status": entry.get("canonical", {}).get("status", ""),
                        "Broken Links": len(entry.get("broken_links", {}).get("broken", [])),
                        "Flags": "; ".join(entry.get("flags", [])),
                    })
                df = pd.DataFrame(rows)
                csv_data = df.to_csv(index=False)
                st.download_button(
                    "📊 Download CSV Report",
                    data=csv_data,
                    file_name="seo_audit_report.csv",
                    mime="text/csv",
                )

else:
    st.markdown("""
    <div class="empty-state">
        <h3>No audit results yet</h3>
        <p>Add URLs in the sidebar and click Start Audit to begin analyzing your pages.</p>
        <br>
        <p style="font-size: 0.85rem;">Supports individual URL input or CSV upload with a 'url' column.</p>
    </div>
    """, unsafe_allow_html=True)
