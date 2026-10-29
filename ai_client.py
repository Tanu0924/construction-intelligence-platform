"""Gemini multimodal client with JSON data contracts and a demo-mode fallback."""
import io
import json
import re
from typing import Any, Dict, List, Optional

from PIL import Image

DEFAULT_MODEL = "gemini-2.0-flash"
MODEL_CHOICES = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

# ----------------------------------------------------------------- JSON contracts
PPE_CONTRACT = {
    "safety_score": "integer 0-100",
    "overall_status": "one of: Compliant | Partially Compliant | Non-Compliant",
    "workers_detected": "integer",
    "ppe_detection": {
        "helmet": {"detected": "boolean", "note": "string"},
        "high_vis_vest": {"detected": "boolean", "note": "string"},
        "steel_toe_boots": {"detected": "boolean", "note": "string"},
        "safety_harness": {"detected": "boolean", "note": "string"},
    },
    "hazards": [
        {"hazard": "string", "severity": "Low | Medium | High | Critical",
         "remedy": "string", "standard_reference": "string"}
    ],
    "summary": "string",
}

CRACK_CONTRACT = {
    "defect_type": "Hairline | Settlement | Structural Shear | Thermal Expansion | Spalling",
    "severity_score": "integer 0-100 (100 = most severe)",
    "estimated_width_mm": "number",
    "urgency": "Low | Medium | High | Critical",
    "root_causes": ["string"],
    "recommended_repairs": [{"method": "string", "detail": "string"}],
    "monitoring_advice": "string",
    "summary": "string",
}

PPE_PROMPT = f"""You are a certified construction safety officer auditing a site photograph.
Audit worker PPE compliance (helmets, high-visibility vests, steel-toe boots, safety harnesses)
and identify site hazards, referencing OSHA 1926 and Indian standards (IS 456 / IS 3764 / BOCW Act) where relevant.
If no workers are visible, set workers_detected to 0 and judge site-level hazards only.
Respond with ONLY valid JSON matching this contract (no markdown fences):
{json.dumps(PPE_CONTRACT, indent=2)}"""

CRACK_PROMPT = f"""You are a senior structural engineer diagnosing a concrete or masonry surface from a photograph.
Classify the defect type, estimate crack width in mm using visible scale cues, give root causes,
recommend engineering repairs (e.g. epoxy injection, structural re-grouting, polymer-modified mortar, crack stitching, jacketing),
and state urgency. Reference IS 456 and IS 13935 where relevant.
Respond with ONLY valid JSON matching this contract (no markdown fences):
{json.dumps(CRACK_CONTRACT, indent=2)}"""

CHAT_SYSTEM = (
    "You are SiteMate, an expert construction engineering assistant for Indian projects. "
    "Answer concisely and practically, cite IS codes (IS 456, IS 800, IS 1893, IS 875, NBC 2016) and OSHA when relevant, "
    "use INR for costs, and flag safety-critical items clearly. If a question needs a licensed structural engineer, say so."
)


# ----------------------------------------------------------------- demo fallbacks
def demo_ppe() -> Dict[str, Any]:
    return {
        "safety_score": 62,
        "overall_status": "Partially Compliant",
        "workers_detected": 3,
        "ppe_detection": {
            "helmet": {"detected": True, "note": "All 3 workers wearing helmets."},
            "high_vis_vest": {"detected": True, "note": "2 of 3 workers in high-vis vests."},
            "steel_toe_boots": {"detected": False, "note": "Footwear appears to be sandals / sneakers."},
            "safety_harness": {"detected": False, "note": "Worker at open edge has no harness."},
        },
        "hazards": [
            {"hazard": "Unprotected edge work without fall arrest", "severity": "Critical",
             "remedy": "Stop work; install guardrails and mandate full-body harness anchored to a rated point.",
             "standard_reference": "OSHA 1926.501 / BOCW Rules"},
            {"hazard": "Non-compliant footwear", "severity": "High",
             "remedy": "Issue steel-toe safety boots and enforce at the gate.", "standard_reference": "IS 15298"},
            {"hazard": "Loose material near edge", "severity": "Medium",
             "remedy": "Provide toe boards and designated stacking areas.", "standard_reference": "OSHA 1926.502"},
        ],
        "summary": "DEMO MODE sample output. Add a Gemini API key in the sidebar for real analysis.",
    }


def demo_crack() -> Dict[str, Any]:
    return {
        "defect_type": "Structural Shear",
        "severity_score": 78,
        "estimated_width_mm": 2.5,
        "urgency": "High",
        "root_causes": ["Diagonal tension from overloading or inadequate shear reinforcement",
                        "Differential settlement of supporting column or footing",
                        "Insufficient stirrup spacing near support"],
        "recommended_repairs": [
            {"method": "Epoxy injection", "detail": "Low-viscosity epoxy pressure-injected after cleaning the crack."},
            {"method": "Structural re-grouting", "detail": "Non-shrink grout around damaged zones; consider jacketing."},
        ],
        "monitoring_advice": "Install tell-tale gauges and re-measure weekly; commission a structural audit.",
        "summary": "DEMO MODE sample output. Add a Gemini API key in the sidebar for real analysis.",
    }


def demo_chat(question: str) -> str:
    q = question.lower()
    rules = [
        (("curing", "cure"), "Per IS 456, cure OPC concrete for at least 7 days (10 days for mineral admixtures or hot/dry weather). Keep surfaces continuously wet using hessian, ponding or curing compound."),
        (("cement", "mix", "grade", "m25", "m20"), "For M25 nominal mix by IS 456 use roughly 1:1:2 (cement:sand:aggregate); design mixes are preferred for M25 and above. Typical w/c ratio is 0.45 to 0.50."),
        (("crack",), "Classify first: hairline (<0.3 mm) is usually cosmetic; widths above ~1 mm or diagonal/stepped cracks need structural assessment. Try the Crack Diagnostics tab."),
        (("steel", "rebar", "fe500", "fe 500"), "Fe 500/500D TMT is standard. Typical consumption is about 3.5 to 4.5 kg per sq ft for residential RCC. Maintain cover as per IS 456 exposure class."),
        (("safety", "ppe", "helmet", "harness"), "Mandatory PPE: helmet (IS 2925), high-vis vest, safety boots (IS 15298), harness above 1.8 m (OSHA) and gloves/eye protection per task."),
        (("rain", "monsoon"), "In heavy rain: isolate temporary electrics, stop pouring concrete, cover fresh work, and inspect excavation shoring before re-entry."),
        (("cost", "budget", "rate"), "Indicative RCC construction costs in India range about ₹1,600 to ₹3,000 per sq ft depending on type and city tier. Use the Planning tab for an estimate."),
    ]
    for keys, ans in rules:
        if any(k in q for k in keys):
            return ans + "\n\n*(Demo mode: add a Gemini API key for full AI answers.)*"
    return ("I'm running in demo mode with a limited knowledge base (curing, mixes, cracks, steel, PPE, rain, costs). "
            "Add a Gemini API key in the sidebar for open-ended engineering answers.")


# ----------------------------------------------------------------- helpers
def parse_json(text: str) -> Dict[str, Any]:
    """Robustly parse JSON from a model response."""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Model response was not valid JSON.")


def prepare_image(uploaded_file, max_side: int = 1600) -> Image.Image:
    """Open an uploaded image, normalise colour mode and downscale."""
    img = Image.open(io.BytesIO(uploaded_file.getvalue()))
    img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    return img


class GeminiClient:
    """Thin wrapper. If api_key is empty the client operates in demo mode."""

    def __init__(self, api_key: Optional[str], model_name: str = DEFAULT_MODEL):
        self.api_key = (api_key or "").strip()
        self.model_name = model_name
        self._model = None

    @property
    def demo_mode(self) -> bool:
        return not self.api_key

    def _get_model(self, system: Optional[str] = None):
        import google.generativeai as genai  # lazy import
        genai.configure(api_key=self.api_key)
        kwargs = {"system_instruction": system} if system else {}
        return genai.GenerativeModel(self.model_name, **kwargs)

    def _analyze(self, prompt: str, image: Image.Image, demo_fn) -> Dict[str, Any]:
        if self.demo_mode:
            return demo_fn()
        model = self._get_model()
        resp = model.generate_content(
            [prompt, image],
            generation_config={"temperature": 0.2, "response_mime_type": "application/json"},
        )
        return parse_json(resp.text)

    def analyze_ppe(self, image: Image.Image) -> Dict[str, Any]:
        return self._analyze(PPE_PROMPT, image, demo_ppe)

    def analyze_crack(self, image: Image.Image) -> Dict[str, Any]:
        return self._analyze(CRACK_PROMPT, image, demo_crack)

    def chat(self, history: List[Dict[str, str]], question: str) -> str:
        """Multi-turn chat. history is a list of {role, content} (user/assistant)."""
        if self.demo_mode:
            return demo_chat(question)
        model = self._get_model(CHAT_SYSTEM)
        contents = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in history
        ]
        contents.append({"role": "user", "parts": [question]})
        resp = model.generate_content(contents, generation_config={"temperature": 0.4})
        return resp.text
