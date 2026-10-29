"""Cost estimation, real estate valuation and material requirement engine (INR).

All rates are indicative planning figures, not quotations.
"""
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import quote

STRUCTURE_TYPES: Dict[str, Dict[str, float]] = {
    # cost = construction INR/sqft (Tier 2 baseline), market = resale INR/sqft (Tier 2 baseline)
    # steel = kg/sqft, cement = 50kg bags/sqft
    "Residential Apartment": {"cost": 1900, "market": 5500, "steel": 3.8, "cement": 0.40},
    "Independent House / Villa": {"cost": 2300, "market": 6200, "steel": 4.2, "cement": 0.45},
    "Commercial Office": {"cost": 2700, "market": 8000, "steel": 4.8, "cement": 0.45},
    "Retail / Mall Space": {"cost": 3000, "market": 9500, "steel": 5.0, "cement": 0.48},
    "Industrial Warehouse": {"cost": 1600, "market": 3800, "steel": 6.0, "cement": 0.35},
}

TIER_FACTORS: Dict[str, Dict[str, float]] = {
    "Tier 1 (Mumbai, Delhi NCR, Bengaluru)": {"cost": 1.25, "market": 2.00},
    "Tier 2 (Pune, Indore, Jaipur, Lucknow)": {"cost": 1.00, "market": 1.00},
    "Tier 3 (Small cities & towns)": {"cost": 0.85, "market": 0.55},
}

MILESTONES: List[tuple] = [
    ("Site prep & Foundation", 0, 15),
    ("Plinth & Substructure", 15, 30),
    ("Superstructure (RCC frame)", 30, 60),
    ("Masonry, MEP & Services", 60, 80),
    ("Finishing & Handover", 80, 100),
]

LAND_SHARE = 0.30  # share of market value attributed to land (exists regardless of progress)


def format_inr(amount: float) -> str:
    """Format a rupee amount in Lakhs / Crores."""
    if amount >= 1e7:
        return f"₹{amount / 1e7:,.2f} Cr"
    if amount >= 1e5:
        return f"₹{amount / 1e5:,.2f} L"
    return f"₹{amount:,.0f}"


@dataclass
class Estimate:
    total_budget: float
    capex_incurred: float
    remaining_budget: float
    full_market_value: float
    current_asset_value: float
    steel_total_tonnes: float
    cement_total_bags: float
    steel_used_tonnes: float
    cement_used_bags: float
    current_milestone: str


def current_milestone(completion: float) -> str:
    for name, lo, hi in MILESTONES:
        if lo <= completion < hi:
            return name
    return MILESTONES[-1][0]


def calculate(structure: str, sqft: float, tier: str, completion: float) -> Estimate:
    """Compute budget, capex, valuation and material metrics.

    completion is 0-100.
    """
    if sqft <= 0:
        raise ValueError("Built-up area must be greater than zero.")
    completion = max(0.0, min(100.0, float(completion)))
    s, t = STRUCTURE_TYPES[structure], TIER_FACTORS[tier]
    total_budget = sqft * s["cost"] * t["cost"]
    capex = total_budget * completion / 100
    full_market = sqft * s["market"] * t["market"]
    structure_share = 1 - LAND_SHARE
    current_value = full_market * (LAND_SHARE + structure_share * completion / 100)
    steel_total = sqft * s["steel"] / 1000
    cement_total = sqft * s["cement"]
    return Estimate(
        total_budget=total_budget,
        capex_incurred=capex,
        remaining_budget=total_budget - capex,
        full_market_value=full_market,
        current_asset_value=current_value,
        steel_total_tonnes=steel_total,
        cement_total_bags=cement_total,
        steel_used_tonnes=steel_total * completion / 100,
        cement_used_bags=cement_total * completion / 100,
        current_milestone=current_milestone(completion),
    )


def render_prompt(structure: str, tier: str, sqft: float, completion: float, style: str) -> str:
    """Build a descriptive architectural-rendering prompt."""
    city = tier.split("(")[0].strip()
    stage = "fully completed" if completion >= 100 else f"under construction, {int(completion)}% complete"
    return (
        f"Conceptual 3D architectural rendering of a {structure.lower()}, about {int(sqft)} sq ft, "
        f"{style} design, Indian urban context ({city}), {stage}, golden hour lighting, "
        "photorealistic, highly detailed, wide angle, landscaped surroundings"
    )


def pollinations_url(prompt: str, width: int = 1024, height: int = 640, seed: int = 7) -> str:
    """Pollinations AI image URL (free, no key, no database)."""
    return (
        f"https://image.pollinations.ai/prompt/{quote(prompt)}"
        f"?width={width}&height={height}&seed={seed}&nologo=true&model=flux"
    )
