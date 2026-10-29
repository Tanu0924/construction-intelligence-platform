# Multimodal Construction Intelligence Platform
Skill Wallet Capstone Project 1 · Platform ID: `6ac4c98d1dcde6d7857c1642`

A Streamlit decision-support app that analyses site photos for PPE compliance, classifies concrete cracks, estimates cost and valuation in INR, and gives weather-aware daily protocols plus a multi-turn engineering chatbot.

## Features
| Tab | What it does |
|---|---|
| Site Safety & PPE | Gemini vision audit, safety score, PPE checklist, hazards with severity and remedies, JSON download |
| Crack Diagnostics | Defect type, width (mm), severity score, root causes, repairs, urgency, JSON download |
| Planning & Valuation | Budget, capex, asset valuation (Lakhs/Crores), steel/cement, milestones, Pollinations 3D concept render |
| Daily Site Assistant | Weather protocols (High Wind, Heavy Rain, Extreme Heat, Normal) and chatbot |

No API key? The app runs in **demo mode** with sample outputs.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Paste your Gemini key (free at https://aistudio.google.com) in the sidebar, or set `GEMINI_API_KEY` as an environment variable.

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. At share.streamlit.io choose the repo, branch and `app.py`.
3. (Optional) Under *Advanced settings > Secrets* add: `GEMINI_API_KEY = "your-key"`.

## Structure
```
app.py                 Streamlit UI (sidebar + 4 tabs)
modules/ai_client.py   Gemini client, JSON contracts, demo fallbacks
modules/estimator.py   INR costing, valuation, materials, render prompt
modules/weather.py     Weather safety protocols
modules/styles.py      CSS and HTML helpers
PROMPT.md              Original master prompt
```

## Notes
- Cost and valuation rates are indicative planning figures; edit the tables in `modules/estimator.py`.
- AI output is advisory. Structural decisions need a licensed engineer.
- If a Gemini model name is retired, pick another in the sidebar or edit `MODEL_CHOICES`.
