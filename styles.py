"""Modern CSS styling and small HTML render helpers."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.hero {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    padding: 1.6rem 2rem; border-radius: 16px; color: #fff; margin-bottom: 1.2rem;
}
.hero h1 { margin: 0; font-size: 1.9rem; font-weight: 700; }
.hero p { margin: .3rem 0 0; opacity: .85; }
.metric-card {
    background: #ffffff; border: 1px solid #e6e9ef; border-radius: 14px;
    padding: 1rem 1.2rem; box-shadow: 0 2px 8px rgba(16,24,40,.06); height: 100%;
}
.metric-card .label { font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: #667085; }
.metric-card .value { font-size: 1.7rem; font-weight: 700; color: #101828; margin-top: .15rem; }
.metric-card .sub { font-size: .8rem; color: #667085; }
.pill {
    display: inline-block; padding: .2rem .75rem; border-radius: 999px;
    font-size: .78rem; font-weight: 600; margin-right: .35rem;
}
.pill-green { background: #d1fadf; color: #027a48; }
.pill-yellow { background: #fef0c7; color: #b54708; }
.pill-orange { background: #ffead5; color: #c4320a; }
.pill-red { background: #fee4e2; color: #b42318; }
.pill-blue { background: #d1e9ff; color: #175cd3; }
.pill-gray { background: #eaecf0; color: #344054; }
.alert-box { border-left: 6px solid; border-radius: 10px; padding: .9rem 1.1rem; margin: .6rem 0; background: #f9fafb; }
.alert-red { border-color: #d92d20; background: #fef3f2; }
.alert-orange { border-color: #f79009; background: #fffaeb; }
.alert-green { border-color: #12b76a; background: #f6fef9; }
.alert-blue { border-color: #2e90fa; background: #eff8ff; }
.hazard { border: 1px solid #e6e9ef; border-radius: 12px; padding: .8rem 1rem; margin-bottom: .6rem; background: #fff; }
.demo-banner { background: #fffaeb; border: 1px dashed #f79009; color: #93370d; padding: .5rem .9rem; border-radius: 10px; font-size: .85rem; }
</style>
"""

SEVERITY_PILL = {
    "low": "pill-green", "medium": "pill-yellow", "high": "pill-orange", "critical": "pill-red",
}


def pill(text: str, cls: str = "pill-gray") -> str:
    return f'<span class="pill {cls}">{text}</span>'


def severity_pill(severity: str) -> str:
    return pill(str(severity).title(), SEVERITY_PILL.get(str(severity).lower(), "pill-gray"))


def metric_card(label: str, value: str, sub: str = "") -> str:
    return (
        f'<div class="metric-card"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>'
    )
