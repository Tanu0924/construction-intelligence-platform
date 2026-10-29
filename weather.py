"""Weather-aware site safety protocols."""
from typing import Dict, List

WEATHER_PROTOCOLS: Dict[str, Dict] = {
    "Normal": {
        "level": "green",
        "headline": "Normal conditions: standard operations permitted",
        "alerts": [
            "Conduct the routine toolbox talk and PPE check before shift start.",
            "Maintain standard curing: keep fresh concrete moist for a minimum of 7 days (IS 456).",
            "Inspect scaffolding, lifting tackle and temporary electrics as per daily checklist.",
        ],
    },
    "High Wind": {
        "level": "red",
        "headline": "High wind: suspend crane and elevated work",
        "alerts": [
            "SUSPEND all crane and hoist operations when sustained wind exceeds ~38 km/h (follow manufacturer limit).",
            "Stop work on scaffolds, formwork platforms and roof edges; secure all loose sheets, shuttering and materials.",
            "Lower tower crane booms into weathervane mode and lock the slewing brake.",
            "Restrict workers from the fall zone beneath hoists and façade work; verify harness anchorages.",
            "Cover stacked cement and dusty materials; cordon off unfinished masonry walls at risk of toppling.",
        ],
    },
    "Heavy Rain": {
        "level": "orange",
        "headline": "Heavy rain: electrical, excavation and curing risks",
        "alerts": [
            "ELECTRICAL HAZARD: isolate temporary power, ensure ELCB/RCCB trip tests, keep cables off wet ground.",
            "Halt concrete pouring; protect fresh concrete with tarpaulin to prevent washout and surface scaling.",
            "Inspect excavation walls and shoring for slips; pump out standing water before re-entry.",
            "Anti-skid footwear mandatory; barricade slippery ramps, and re-check scaffold base plates.",
            "Move cement and admixtures to covered, raised storage; cover steel to limit surface rust.",
        ],
    },
    "Extreme Heat": {
        "level": "orange",
        "headline": "Extreme heat: heat-stress and curing protocol",
        "alerts": [
            "Shift heavy tasks to early morning; enforce rest breaks every hour in shade with drinking water and ORS.",
            "Monitor workers for heat exhaustion: dizziness, cramps, confusion; provide first-aid shade cover.",
            "CONCRETE CURING: pour in cool hours, use retarders if needed, and cure continuously with wet hessian for 10+ days.",
            "Keep concrete temperature below ~35 °C at placement; shade aggregates and chill mixing water.",
            "Avoid prolonged use of bare metal tools and check hot formwork surfaces before handling.",
        ],
    },
}


def get_protocol(condition: str) -> Dict:
    return WEATHER_PROTOCOLS.get(condition, WEATHER_PROTOCOLS["Normal"])


def conditions() -> List[str]:
    return list(WEATHER_PROTOCOLS.keys())
