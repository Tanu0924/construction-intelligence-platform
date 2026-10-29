"""Multimodal Construction Intelligence Platform (Skill Wallet Capstone Project 1).

Run:  streamlit run app.py
"""
import json
import os

import streamlit as st

from modules import estimator, styles, weather
from modules.ai_client import DEFAULT_MODEL, MODEL_CHOICES, GeminiClient, prepare_image

st.set_page_config(page_title="Construction Intelligence Platform", page_icon="🏗️", layout="wide")
st.markdown(styles.CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ sidebar
def render_sidebar() -> GeminiClient:
    with st.sidebar:
        st.markdown("## 🏗️ Construction AI")
        default_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
        try:
            default_key = default_key or os.environ.get("GEMINI_API_KEY", "")
        except Exception:
            pass
        api_key = st.text_input("Google Gemini API Key", type="password", value=default_key,
                                help="Get a free key at aistudio.google.com. Stored only in this session.")
        model_name = st.selectbox("Model", MODEL_CHOICES, index=MODEL_CHOICES.index(DEFAULT_MODEL))
        client = GeminiClient(api_key, model_name)
        if client.demo_mode:
            st.markdown('<div class="demo-banner">🧪 <b>Demo mode</b>: sample outputs shown. '
                        'Enter a Gemini API key for live analysis.</div>', unsafe_allow_html=True)
        else:
            st.success("Live Gemini mode enabled")

        st.markdown("---")
        st.markdown("### Navigation")
        st.markdown("1. 🦺 Site Safety & PPE Audit\n2. 🧱 Crack Diagnostics\n"
                    "3. 💰 Planning & Valuation\n4. 🌦️ Daily Site Assistant")
        st.markdown("---")
        with st.expander("Architecture overview"):
            st.markdown(
                "- **UI:** Streamlit (single-file entry `app.py`)\n"
                "- **Vision/LLM:** Gemini multimodal via `modules/ai_client.py`\n"
                "- **Contracts:** strict JSON schemas for PPE and crack outputs\n"
                "- **Engines:** `estimator.py` (INR costing), `weather.py` (protocols)\n"
                "- **Rendering:** Pollinations AI (Flux), no key needed\n"
                "- **State:** session only, no database"
            )
        st.caption("Indicative figures only. Verify with a licensed engineer.")
    return client


# ------------------------------------------------------------------ shared renderers
def score_color(score: int) -> str:
    return "pill-green" if score >= 80 else "pill-yellow" if score >= 60 else "pill-orange" if score >= 40 else "pill-red"


def download_json(label: str, data: dict, filename: str):
    st.download_button(label, json.dumps(data, indent=2, ensure_ascii=False), file_name=filename,
                       mime="application/json")


def run_analysis(client, uploaded, analyze_fn, spinner_text):
    """Run analysis with robust error handling. Returns dict or None."""
    try:
        image = prepare_image(uploaded)
    except Exception as exc:
        st.error(f"Could not read the image: {exc}")
        return None
    try:
        with st.spinner(spinner_text):
            return analyze_fn(image)
    except Exception as exc:
        st.error(f"Analysis failed: {exc}")
        st.info("Check your API key, model choice or quota, or clear the key to use demo mode.")
        return None


# ------------------------------------------------------------------ tab 1
def tab_ppe(client: GeminiClient):
    st.subheader("Site Safety & PPE Audit")
    st.caption("Upload a site photo. Audits helmets, high-vis vests, steel-toe boots and harnesses (OSHA / IS standards).")
    up = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="ppe_up")
    if up:
        c1, c2 = st.columns([1, 1])
        c1.image(up, caption="Uploaded photo", use_container_width=True)
        if c2.button("🔍 Run PPE audit", type="primary", key="ppe_btn"):
            res = run_analysis(client, up, client.analyze_ppe, "Auditing site safety...")
            if res:
                st.session_state["ppe_result"] = res
    res = st.session_state.get("ppe_result")
    if not res:
        return
    score = int(res.get("safety_score", 0))
    status = res.get("overall_status", "Unknown")
    status_cls = {"Compliant": "pill-green", "Partially Compliant": "pill-yellow",
                  "Non-Compliant": "pill-red"}.get(status, "pill-gray")
    hazards = res.get("hazards", [])
    crit = sum(1 for h in hazards if str(h.get("severity", "")).lower() in ("critical", "high"))

    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(styles.metric_card("Safety score", f"{score}/100", styles.pill("Rating", score_color(score))),
                unsafe_allow_html=True)
    m2.markdown(styles.metric_card("Overall status", styles.pill(status, status_cls), "OSHA / IS aligned"),
                unsafe_allow_html=True)
    m3.markdown(styles.metric_card("Workers detected", str(res.get("workers_detected", "n/a"))),
                unsafe_allow_html=True)
    m4.markdown(styles.metric_card("High/Critical hazards", str(crit)), unsafe_allow_html=True)
    st.progress(max(0, min(100, score)) / 100)

    st.markdown("#### PPE checklist")
    labels = {"helmet": "⛑️ Helmet", "high_vis_vest": "🦺 High-vis vest",
              "steel_toe_boots": "🥾 Steel-toe boots", "safety_harness": "🧗 Safety harness"}
    cols = st.columns(4)
    for col, (key, label) in zip(cols, labels.items()):
        item = res.get("ppe_detection", {}).get(key, {})
        ok = bool(item.get("detected"))
        col.markdown(
            f'<div class="alert-box {"alert-green" if ok else "alert-red"}"><b>{label}</b><br>'
            f'{styles.pill("Detected" if ok else "Missing", "pill-green" if ok else "pill-red")}<br>'
            f'<small>{item.get("note", "")}</small></div>', unsafe_allow_html=True)

    st.markdown("#### Identified hazards")
    if not hazards:
        st.success("No hazards identified.")
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    for h in sorted(hazards, key=lambda x: order.get(str(x.get("severity", "")).lower(), 9)):
        st.markdown(
            f'<div class="hazard">{styles.severity_pill(h.get("severity", "n/a"))} <b>{h.get("hazard", "")}</b><br>'
            f'<small><b>Remedy:</b> {h.get("remedy", "")}<br>'
            f'<b>Reference:</b> {h.get("standard_reference", "n/a")}</small></div>', unsafe_allow_html=True)
    if res.get("summary"):
        st.info(res["summary"])
    download_json("⬇️ Download JSON report", res, "ppe_safety_report.json")


# ------------------------------------------------------------------ tab 2
def tab_crack(client: GeminiClient):
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.caption("Upload a concrete or wall surface photo to classify the defect and get repair guidance.")
    up = st.file_uploader("Concrete / wall surface photo", type=["jpg", "jpeg", "png"], key="crack_up")
    if up:
        c1, c2 = st.columns([1, 1])
        c1.image(up, caption="Uploaded surface", use_container_width=True)
        if c2.button("🔬 Diagnose defect", type="primary", key="crack_btn"):
            res = run_analysis(client, up, client.analyze_crack, "Diagnosing structure...")
            if res:
                st.session_state["crack_result"] = res
    res = st.session_state.get("crack_result")
    if not res:
        return
    sev = int(res.get("severity_score", 0))
    urgency = res.get("urgency", "n/a")
    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(styles.metric_card("Defect type", res.get("defect_type", "n/a")), unsafe_allow_html=True)
    m2.markdown(styles.metric_card("Severity score", f"{sev}/100", "higher = worse"), unsafe_allow_html=True)
    m3.markdown(styles.metric_card("Est. crack width", f'{res.get("estimated_width_mm", "n/a")} mm'),
                unsafe_allow_html=True)
    m4.markdown(styles.metric_card("Urgency", styles.severity_pill(urgency)), unsafe_allow_html=True)
    st.progress(max(0, min(100, sev)) / 100)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Probable root causes")
        for c in res.get("root_causes", []):
            st.markdown(f"- {c}")
    with right:
        st.markdown("#### Recommended engineering repairs")
        for r in res.get("recommended_repairs", []):
            st.markdown(f"**{r.get('method', '')}**: {r.get('detail', '')}")
    if res.get("monitoring_advice"):
        st.warning(f"**Monitoring:** {res['monitoring_advice']}")
    if res.get("summary"):
        st.info(res["summary"])
    download_json("⬇️ Download JSON report", res, "crack_diagnostic_report.json")


# ------------------------------------------------------------------ tab 3
def tab_planning():
    st.subheader("Project Planning & Real Estate Valuation (INR)")
    c1, c2 = st.columns(2)
    structure = c1.selectbox("Structure type", list(estimator.STRUCTURE_TYPES))
    tier = c2.selectbox("Location tier", list(estimator.TIER_FACTORS), index=1)
    sqft = c1.number_input("Built-up area (sq ft)", min_value=100, max_value=1_000_000, value=2000, step=100)
    completion = c2.slider("Completion %", 0, 100, 40)
    try:
        est = estimator.calculate(structure, sqft, tier, completion)
    except Exception as exc:
        st.error(f"Calculation error: {exc}")
        return
    fmt = estimator.format_inr
    st.markdown("---")
    a, b, c, d = st.columns(4)
    a.markdown(styles.metric_card("Total project budget", fmt(est.total_budget), "full completion"), unsafe_allow_html=True)
    b.markdown(styles.metric_card("Capex incurred", fmt(est.capex_incurred), f"{fmt(est.remaining_budget)} remaining"),
               unsafe_allow_html=True)
    c.markdown(styles.metric_card("Current asset valuation", fmt(est.current_asset_value),
                                  f"Completed value {fmt(est.full_market_value)}"), unsafe_allow_html=True)
    d.markdown(styles.metric_card("Value uplift", fmt(est.full_market_value - est.total_budget),
                                  "market value less cost (indicative)"), unsafe_allow_html=True)
    e, f, g, h = st.columns(4)
    e.markdown(styles.metric_card("Steel required", f"{est.steel_total_tonnes:,.1f} t",
                                  f"{est.steel_used_tonnes:,.1f} t used"), unsafe_allow_html=True)
    f.markdown(styles.metric_card("Cement required", f"{est.cement_total_bags:,.0f} bags",
                                  f"{est.cement_used_bags:,.0f} used (50 kg)"), unsafe_allow_html=True)
    g.markdown(styles.metric_card("Current milestone", est.current_milestone), unsafe_allow_html=True)
    h.markdown(styles.metric_card("Cost / sq ft", f"₹{est.total_budget / sqft:,.0f}"), unsafe_allow_html=True)

    st.markdown("#### Milestone progress")
    st.progress(completion / 100, text=f"{completion}% complete: {est.current_milestone}")
    cols = st.columns(len(estimator.MILESTONES))
    for col, (name, lo, hi) in zip(cols, estimator.MILESTONES):
        done = completion >= hi
        active = lo <= completion < hi
        icon = "✅" if done else "🔨" if active else "⏳"
        col.markdown(f"{icon} **{name}**  \n<small>{lo}-{hi}%</small>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Conceptual 3D architectural rendering (Pollinations AI)")
    style = st.selectbox("Design style", ["Modern minimalist", "Contemporary Indian", "Traditional Indian",
                                          "Industrial", "Eco-friendly green building"])
    prompt = st.text_area("Rendering prompt (editable)",
                          estimator.render_prompt(structure, tier, sqft, completion, style), height=90)
    if st.button("🎨 Generate rendering", type="primary"):
        st.session_state["render_url"] = estimator.pollinations_url(prompt)
    if st.session_state.get("render_url"):
        st.image(st.session_state["render_url"], caption="AI concept rendering (illustrative only)",
                 use_container_width=True)
        st.caption("Images are generated by Pollinations; loading may take a few seconds.")


# ------------------------------------------------------------------ tab 4
def tab_assistant(client: GeminiClient):
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    cond = st.radio("Today's weather condition", weather.conditions(), horizontal=True)
    proto = weather.get_protocol(cond)
    items = "".join(f"<li>{a}</li>" for a in proto["alerts"])
    st.markdown(f'<div class="alert-box alert-{proto["level"]}"><b>{proto["headline"]}</b><ul>{items}</ul></div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💬 Construction engineering assistant")
    if "chat" not in st.session_state:
        st.session_state["chat"] = [{"role": "assistant",
                                    "content": "Hi, I'm SiteMate. Ask me about mixes, curing, rebar, safety, scheduling or costs."}]
    for m in st.session_state["chat"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    if q := st.chat_input("Ask a construction engineering question..."):
        history = list(st.session_state["chat"])
        st.session_state["chat"].append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        ctx = f"[Site weather today: {cond}] {q}"
        try:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = client.chat(history, ctx)
                st.markdown(answer)
        except Exception as exc:
            answer = f"Sorry, the assistant hit an error: {exc}"
            st.error(answer)
        st.session_state["chat"].append({"role": "assistant", "content": answer})
    if st.button("Clear conversation"):
        st.session_state.pop("chat", None)
        st.rerun()


# ------------------------------------------------------------------ main
def main():
    client = render_sidebar()
    st.markdown('<div class="hero"><h1>🏗️ Multimodal Construction Intelligence Platform</h1>'
                '<p>Safety audits, crack diagnostics, INR costing &amp; valuation, and weather-aware site guidance.</p></div>',
                unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🦺 Site Safety & PPE", "🧱 Crack Diagnostics", "💰 Planning & Valuation",
                              "🌦️ Daily Site Assistant"])
    with t1:
        tab_ppe(client)
    with t2:
        tab_crack(client)
    with t3:
        tab_planning()
    with t4:
        tab_assistant(client)


if __name__ == "__main__":
    main()
