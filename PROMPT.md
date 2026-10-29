# Project 1: Multimodal Construction Intelligence Platform

**Category:** Generative AI | Real Estate Decision Support
**Platform ID:** 6ac4c98d1dcde6d7857c1642

## Objective & Scope
An intelligent decision-support system analyzing site photos to audit PPE safety compliance, classify concrete cracks with severity scores, estimate construction costs and real estate valuation in INR, and provide weather-aware daily protocols.

## Kanban Epics Coverage
Pre-requisites (Python 3.9+, FastAPI, React) | Epic 1 (Requirements & Env) | Epic 2 (PPE Safety Vision & Crack Diagnostics) | Epic 3 (Project Planning & Real Estate Valuation) | Epic 4 (Multimodal AI & JSON Contracts) | Epic 5 (Site Chatbot & Weather Advisory) | Epic 6 (Interface, Testing, Cloud Deployment)

## Recommended Tech Stack
Python 3.9+, Streamlit / FastAPI + React, Multimodal LLM (Gemini 1.5 / LLaMA Vision), Pillow, Pollinations/Flux API, JSON Data Contracts

## TURNKEY MASTER PROMPT (PROJECT 1)

Act as an expert full-stack AI engineer. Build a complete, production-ready Streamlit application in Python named "Multimodal Construction Intelligence Platform" (Skill Wallet Capstone Project 1).

### Core Requirements & Modules

1. **Sidebar:** Secure input for Google Gemini API key (with graceful fallback to demonstration mode if no key is supplied), architecture overview, and feature navigation.

2. **Tab 1 - Site Safety & PPE Audit (Epic 2):**
   - File uploader for construction site photos (JPG/PNG).
   - Multimodal prompt analyzing worker PPE compliance (helmets, high-vis vests, steel-toe boots, safety harnesses) under OSHA and IS 456 standards.
   - Output structured JSON containing safety_score (0-100), overall_status, ppe_detection checklist, and list of identified site hazards with severity (Low, Medium, High, Critical) and corrective remedies.
   - Render metric cards, status pills, and downloadable JSON report.

3. **Tab 2 - Crack Diagnostics & Structural Integrity (Epic 2):**
   - File uploader for concrete/wall surfaces.
   - Multimodal prompt classifying defect type (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling) with estimated crack width (mm), root causes, recommended engineering repairs (epoxy injection, structural re-grouting), and urgency.

4. **Tab 3 - Planning & Real Estate Valuation (Epic 3):**
   - Interactive inputs for structure type, built-up sqft, location tier (Tier 1/2/3 Indian cities), and completion percentage slider.
   - Calculate total project budget, capital expenditure incurred, current market asset valuation in INR (Lakhs/Crores), and steel/cement requirement metrics with milestone progress bar.
   - Conceptual 3D architectural rendering integration via Pollinations AI prompt generator.

5. **Tab 4 - Daily Site Assistant & Weather-Aware Advisory (Epic 5):**
   - Weather condition selector (High Wind, Heavy Rain, Extreme Heat, Normal) displaying dynamic safety alerts (e.g. suspending crane operations, electrical hazard mitigation, concrete curing protocol).
   - Interactive multi-turn construction engineering assistant chatbot.

Ensure clean, modular code with exception handling, modern CSS styling, and zero external database dependencies for seamless 1-click deployment on Streamlit Community Cloud.
