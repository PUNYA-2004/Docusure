import json
from pathlib import Path
from typing import Dict, Any, List, Optional

RULES_FILE = Path(__file__).resolve().parent / "brsr_rules.json"

CANONICAL_INDICATORS: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # ENVIRONMENTAL INDICATORS (Principle 6 / Section C)
    # =========================================================================
    "ENV_ENERGY_TOTAL": {
        "code": "ENV_ENERGY_TOTAL",
        "name": "Total Energy Consumption",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Energy footprint (Total energy consumed)",
        "canonical_unit": "GJ",
        "aliases": [
            "total energy consumed",
            "total energy consumption",
            "total energy consumption (a+b+c+d+e+f)",
            "total energy consumed (a+b+c+d+e+f)",
            "total energy consumption (a + b + c + d + e + f)",
            "energy consumption (a+b+c+d+e+f)",
            "total energy requirement",
            "gross energy consumption"
        ],
        "keywords": ["energy consumption", "energy consumed", "total energy", "gj", "mwh"],
        "unit_conversions": {
            "mwh": 3.6,     # 1 MWh = 3.6 GJ
            "kwh": 0.0036,  # 1 kWh = 0.0036 GJ
            "tj": 1000.0,   # 1 TJ = 1000 GJ
            "gj": 1.0
        }
    },
    "ENV_ENERGY_RENEWABLE": {
        "code": "ENV_ENERGY_RENEWABLE",
        "name": "Renewable Energy Consumption",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Energy footprint (Renewable energy share)",
        "canonical_unit": "GJ",
        "aliases": [
            "total energy consumed from renewable sources",
            "energy consumed from renewable sources",
            "renewable energy consumption",
            "energy from renewable sources",
            "total renewable energy consumed",
            "renewable sources (a+b+c)",
            "renewable energy share"
        ],
        "keywords": ["renewable sources", "renewable energy", "solar", "wind", "renewable consumption"],
        "unit_conversions": {"mwh": 3.6, "kwh": 0.0036, "gj": 1.0}
    },
    "ENV_ENERGY_NON_RENEWABLE": {
        "code": "ENV_ENERGY_NON_RENEWABLE",
        "name": "Non-Renewable Energy Consumption",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Energy footprint",
        "canonical_unit": "GJ",
        "aliases": [
            "total energy consumed from non-renewable sources",
            "total energy consumed from non- renewable sources",
            "energy from non-renewable sources",
            "non-renewable energy consumption",
            "non-renewable sources (d+e+f)"
        ],
        "keywords": ["non-renewable sources", "non renewable", "grid electricity", "coal", "diesel"],
        "unit_conversions": {"mwh": 3.6, "kwh": 0.0036, "gj": 1.0}
    },
    "ENV_GHG_SCOPE1": {
        "code": "ENV_GHG_SCOPE1",
        "name": "Scope 1 GHG Emissions",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Greenhouse gas (GHG) footprint (Scope 1 emissions)",
        "canonical_unit": "Metric tonnes CO2e",
        "aliases": [
            "total scope 1 emissions",
            "scope 1 emissions",
            "gross scope 1 emissions",
            "scope 1 ghg emissions",
            "scope 1 (break-up of the ghg into co2, ch4, n2o)"
        ],
        "keywords": ["scope 1", "direct emissions", "co2 equivalent", "tco2e", "metric tonnes"],
        "unit_conversions": {"tco2e": 1.0, "mt co2e": 1.0, "metric tonnes of co2 equivalent": 1.0}
    },
    "ENV_GHG_SCOPE2": {
        "code": "ENV_GHG_SCOPE2",
        "name": "Scope 2 GHG Emissions",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Greenhouse gas (GHG) footprint (Scope 2 emissions)",
        "canonical_unit": "Metric tonnes CO2e",
        "aliases": [
            "total scope 2 emissions",
            "scope 2 emissions",
            "gross scope 2 emissions",
            "scope 2 ghg emissions",
            "total scope 2 emissions metric tonnes of co2"
        ],
        "keywords": ["scope 2", "location-based scope 2", "indirect emissions", "co2 equivalent", "tco2e"],
        "unit_conversions": {"tco2e": 1.0, "mt co2e": 1.0, "metric tonnes of co2 equivalent": 1.0}
    },
    "ENV_GHG_SCOPE3": {
        "code": "ENV_GHG_SCOPE3",
        "name": "Scope 3 GHG Emissions",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Greenhouse gas (GHG) footprint (Scope 3 emissions)",
        "canonical_unit": "Metric tonnes CO2e",
        "aliases": [
            "total scope 3 emissions",
            "scope 3 emissions",
            "gross scope 3 emissions",
            "value chain ghg emissions",
            "other indirect emissions (scope 3)"
        ],
        "keywords": ["scope 3", "value chain emissions", "indirect upstream downstream"],
        "unit_conversions": {"tco2e": 1.0, "mt co2e": 1.0}
    },
    "ENV_WATER_WITHDRAWAL": {
        "code": "ENV_WATER_WITHDRAWAL",
        "name": "Total Water Withdrawal",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Water footprint (Total water withdrawal)",
        "canonical_unit": "Kilolitres (KL)",
        "aliases": [
            "total volume of water withdrawal",
            "total water withdrawal",
            "total volume of water withdrawal (in kilolitres)",
            "water withdrawal (i + ii + iii + iv + v)"
        ],
        "keywords": ["water withdrawal", "groundwater", "surface water", "third party water", "kilolitres"],
        "unit_conversions": {"kl": 1.0, "kilolitres": 1.0, "m3": 1.0, "cubic meters": 1.0}
    },
    "ENV_WATER_CONSUMPTION": {
        "code": "ENV_WATER_CONSUMPTION",
        "name": "Total Water Consumption",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Water footprint (Total water consumption)",
        "canonical_unit": "Kilolitres (KL)",
        "aliases": [
            "total volume of water consumption",
            "total water consumption",
            "total volume of water consumption (in kilolitres)",
            "water consumption"
        ],
        "keywords": ["water consumption", "volume of water consumed", "net water consumption", "kilolitres"],
        "unit_conversions": {"kl": 1.0, "kilolitres": 1.0, "m3": 1.0}
    },
    "ENV_WASTE_GENERATED": {
        "code": "ENV_WASTE_GENERATED",
        "name": "Total Waste Generated",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Embracing circularity (Total waste generated)",
        "canonical_unit": "Metric tonnes (MT)",
        "aliases": [
            "total waste generated",
            "total waste generated (in metric tonnes)",
            "gross waste generated",
            "total quantity of waste generated"
        ],
        "keywords": ["waste generated", "plastic waste", "hazardous waste", "e-waste", "metric tonnes"],
        "unit_conversions": {"mt": 1.0, "metric tonnes": 1.0, "tonnes": 1.0, "kg": 0.001}
    },
    "ENV_WASTE_RECYCLED": {
        "code": "ENV_WASTE_RECYCLED",
        "name": "Waste Recycled or Recovered",
        "esg_category": "Environmental",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Embracing circularity (Waste recycled/recovered)",
        "canonical_unit": "Metric tonnes (MT)",
        "aliases": [
            "waste recycled",
            "recycled in mt",
            "total waste recycled or re-used",
            "waste recovered",
            "waste diverted from disposal"
        ],
        "keywords": ["recycled", "reused", "recovery", "waste recycled", "circularity"],
        "unit_conversions": {"mt": 1.0, "metric tonnes": 1.0}
    },
    "ENV_ENVIRONMENTAL_TARGETS": {
        "code": "ENV_ENVIRONMENTAL_TARGETS",
        "name": "Environmental Targets Disclosed",
        "esg_category": "Environmental",
        "section": "Section B — Management and Process Disclosures",
        "principle": "Principle 6: Environmental protection and restoration",
        "brsr_core": "Climate change governance and goals",
        "canonical_unit": "Descriptive / Target Year",
        "aliases": [
            "specific commitments, goals and targets",
            "environmental targets",
            "net zero target",
            "carbon neutrality target",
            "renewable energy target"
        ],
        "keywords": ["net zero", "carbon neutral", "target", "renewable target", "emission reduction goal"],
        "unit_conversions": {}
    },

    # =========================================================================
    # SOCIAL INDICATORS (Principles 3, 4, 5, 8 / Sections A & C)
    # =========================================================================
    "SOC_EMPLOYEES_TOTAL": {
        "code": "SOC_EMPLOYEES_TOTAL",
        "name": "Total Employees Count",
        "esg_category": "Social",
        "section": "Section A — General Disclosures",
        "principle": "Principle 3: Employee well-being",
        "brsr_core": "Enhancing employee wellbeing and safety",
        "canonical_unit": "Count",
        "aliases": [
            "total employees",
            "total number of employees",
            "employees (a)",
            "permanent employees",
            "total workforce employees",
            "employees count"
        ],
        "keywords": ["permanent employees", "other than permanent employees", "total employees", "employees (a)"],
        "unit_conversions": {}
    },
    "SOC_WORKERS_TOTAL": {
        "code": "SOC_WORKERS_TOTAL",
        "name": "Total Workers Count",
        "esg_category": "Social",
        "section": "Section A — General Disclosures",
        "principle": "Principle 3: Employee well-being",
        "brsr_core": "Enhancing employee wellbeing and safety",
        "canonical_unit": "Count",
        "aliases": [
            "total workers",
            "total number of workers",
            "workers (b)",
            "permanent workers",
            "total workforce workers"
        ],
        "keywords": ["permanent workers", "other than permanent workers", "total workers", "workers (b)"],
        "unit_conversions": {}
    },
    "SOC_GENDER_DIVERSITY_FEMALE": {
        "code": "SOC_GENDER_DIVERSITY_FEMALE",
        "name": "Female Workforce Composition",
        "esg_category": "Social",
        "section": "Section A — General Disclosures",
        "principle": "Principle 3: Employee well-being",
        "brsr_core": "Gender diversity (Ratio of female employees/workers)",
        "canonical_unit": "%",
        "aliases": [
            "percentage of female employees",
            "female employees percentage",
            "female employees %",
            "female employee participation",
            "female workers percentage",
            "women employees %"
        ],
        "keywords": ["female employees", "female workers", "women employees", "% (b/a)", "female"],
        "unit_conversions": {}
    },
    "SOC_HEALTH_SAFETY_LTIFR": {
        "code": "SOC_HEALTH_SAFETY_LTIFR",
        "name": "Lost Time Injury Frequency Rate (LTIFR)",
        "esg_category": "Social",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 3: Employee well-being",
        "brsr_core": "Enhancing employee wellbeing and safety (Safety metric)",
        "canonical_unit": "Rate per million person-hours",
        "aliases": [
            "lost time injury frequency rate (ltifr)",
            "ltifr",
            "lost time injury frequency rate",
            "fatalities",
            "high consequence work-related injuries"
        ],
        "keywords": ["ltifr", "lost time injury", "fatalities", "safety incidents", "work-related injury"],
        "unit_conversions": {}
    },
    "SOC_TRAINING_HOURS": {
        "code": "SOC_TRAINING_HOURS",
        "name": "Employee and Worker Training Coverage",
        "esg_category": "Social",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 3: Employee well-being",
        "brsr_core": "Enhancing employee wellbeing (Skill development & training)",
        "canonical_unit": "% or Average Hours",
        "aliases": [
            "training on health and safety",
            "training on skill upgradation",
            "average training hours",
            "employee training percentage",
            "coverage of training"
        ],
        "keywords": ["training", "skill upgradation", "health and safety training", "person-hours of training"],
        "unit_conversions": {}
    },
    "SOC_HUMAN_RIGHTS": {
        "code": "SOC_HUMAN_RIGHTS",
        "name": "Human Rights Grievances and Due Diligence",
        "esg_category": "Social",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 5: Human rights",
        "brsr_core": "Fairness and human rights in workforce and value chain",
        "canonical_unit": "Complaints Count",
        "aliases": [
            "complaints filed in respect of human rights",
            "human rights complaints",
            "sexual harassment complaints",
            "child labour complaints",
            "forced labour complaints",
            "wages complaints"
        ],
        "keywords": ["human rights", "sexual harassment", "posh", "child labour", "forced labour"],
        "unit_conversions": {}
    },
    "SOC_CSR_SPENDING": {
        "code": "SOC_CSR_SPENDING",
        "name": "Corporate Social Responsibility (CSR) Spending",
        "esg_category": "Social",
        "section": "Section A — General Disclosures",
        "principle": "Principle 8: Inclusive growth and equitable development",
        "brsr_core": "Inclusive development (CSR outlay and beneficiaries)",
        "canonical_unit": "INR Crores / Lakhs",
        "aliases": [
            "total amount spent on csr",
            "csr spending",
            "csr obligation",
            "csr expenditure",
            "amount spent on corporate social responsibility"
        ],
        "keywords": ["csr", "corporate social responsibility", "csr expenditure", "csr project"],
        "unit_conversions": {}
    },
    "SOC_CONSUMER_COMPLAINTS": {
        "code": "SOC_CONSUMER_COMPLAINTS",
        "name": "Customer and Consumer Complaints",
        "esg_category": "Social",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 9: Responsible consumer engagement",
        "brsr_core": "Fairness in engaging with customers and suppliers",
        "canonical_unit": "Complaints Count",
        "aliases": [
            "number of consumer complaints",
            "consumer complaints received",
            "customer complaints",
            "complaints received in respect of data privacy",
            "cybersecurity complaints"
        ],
        "keywords": ["consumer complaints", "customer complaints", "data privacy", "product recall", "advertising"],
        "unit_conversions": {}
    },

    # =========================================================================
    # GOVERNANCE INDICATORS (Principles 1, 7 / Sections A, B, C)
    # =========================================================================
    "GOV_BOARD_SIZE": {
        "code": "GOV_BOARD_SIZE",
        "name": "Board of Directors Size & Composition",
        "esg_category": "Governance",
        "section": "Section A — General Disclosures",
        "principle": "Principle 1: Ethics, transparency and accountability",
        "brsr_core": "Openness of business and board oversight",
        "canonical_unit": "Count",
        "aliases": [
            "number of directors on the board",
            "board of directors",
            "total directors",
            "board size",
            "composition of the board"
        ],
        "keywords": ["board of directors", "executive directors", "independent directors", "non-executive directors"],
        "unit_conversions": {}
    },
    "GOV_INDEPENDENT_DIRECTORS": {
        "code": "GOV_INDEPENDENT_DIRECTORS",
        "name": "Independent Directors Share",
        "esg_category": "Governance",
        "section": "Section A — General Disclosures",
        "principle": "Principle 1: Ethics, transparency and accountability",
        "brsr_core": "Openness of business and board oversight",
        "canonical_unit": "% or Count",
        "aliases": [
            "independent directors count",
            "percentage of independent directors",
            "independent non-executive directors",
            "number of independent directors"
        ],
        "keywords": ["independent directors", "independent director", "non-executive independent"],
        "unit_conversions": {}
    },
    "GOV_WOMEN_DIRECTORS": {
        "code": "GOV_WOMEN_DIRECTORS",
        "name": "Women Directors Representation",
        "esg_category": "Governance",
        "section": "Section A — General Disclosures",
        "principle": "Principle 1: Ethics, transparency and accountability",
        "brsr_core": "Gender diversity (Board diversity)",
        "canonical_unit": "Count or %",
        "aliases": [
            "women directors",
            "female directors",
            "women representation on board",
            "number of women directors"
        ],
        "keywords": ["women directors", "female directors", "woman director"],
        "unit_conversions": {}
    },
    "GOV_ETHICS_POLICY": {
        "code": "GOV_ETHICS_POLICY",
        "name": "Anti-Corruption & Business Ethics Policy",
        "esg_category": "Governance",
        "section": "Section B — Management and Process Disclosures",
        "principle": "Principle 1: Ethics, transparency and accountability",
        "brsr_core": "Openness of business (Anti-corruption and anti-bribery policy)",
        "canonical_unit": "Disclosed (Yes / No)",
        "aliases": [
            "policy on anti-corruption or anti-bribery",
            "code of conduct",
            "anti-bribery and anti-corruption policy",
            "business ethics policy"
        ],
        "keywords": ["anti-corruption", "anti-bribery", "code of conduct", "ethics policy"],
        "unit_conversions": {}
    },
    "GOV_WHISTLEBLOWER": {
        "code": "GOV_WHISTLEBLOWER",
        "name": "Whistleblower & Vigil Mechanism",
        "esg_category": "Governance",
        "section": "Section B — Management and Process Disclosures",
        "principle": "Principle 1: Ethics, transparency and accountability",
        "brsr_core": "Openness of business (Whistleblower protection mechanism)",
        "canonical_unit": "Disclosed (Yes / No)",
        "aliases": [
            "whistle blower mechanism",
            "vigil mechanism",
            "whistleblower policy",
            "grievance redressal mechanism for stakeholders"
        ],
        "keywords": ["whistleblower", "vigil mechanism", "whistle-blower", "ombudsperson"],
        "unit_conversions": {}
    },
    "GOV_REGULATORY_FINES": {
        "code": "GOV_REGULATORY_FINES",
        "name": "Fines / Penalties Imposed by Regulators",
        "esg_category": "Governance",
        "section": "Section C — Principle-wise Performance",
        "principle": "Principle 1: Ethics, transparency and accountability",
        "brsr_core": "Openness of business and statutory compliance",
        "canonical_unit": "INR or Count",
        "aliases": [
            "fines / penalties paid in proceedings with regulators",
            "monetary penalties",
            "penalties / fines",
            "strictures or penalties imposed"
        ],
        "keywords": ["fines", "penalties", "monetary penalties", "regulatory action", "sebi penalty"],
        "unit_conversions": {}
    }
}

# 9 NGRBC Principles Description
NGRBC_PRINCIPLES: Dict[str, str] = {
    "P1": "Principle 1: Businesses should conduct and govern themselves with integrity, and in a manner that is Ethical, Transparent and Accountable.",
    "P2": "Principle 2: Businesses should provide goods and services in a manner that is sustainable and safe.",
    "P3": "Principle 3: Businesses should respect and promote the well-being of all employees, including those in their value chains.",
    "P4": "Principle 4: Businesses should respect the interests of and be responsive to all its stakeholders.",
    "P5": "Principle 5: Businesses should respect and promote human rights.",
    "P6": "Principle 6: Businesses should respect and make efforts to protect and restore the environment.",
    "P7": "Principle 7: Businesses, when engaging in influencing public and regulatory policy, should do so in a manner that is responsible and transparent.",
    "P8": "Principle 8: Businesses should promote inclusive growth and equitable development.",
    "P9": "Principle 9: Businesses should engage with and provide value to their consumers in a responsible manner."
}

def export_rules_json():
    """Exports configuration to JSON file for transparency and easy edits."""
    data = {
        "canonical_indicators": CANONICAL_INDICATORS,
        "ngrbc_principles": NGRBC_PRINCIPLES,
        "metadata": {
            "framework": "SEBI Business Responsibility and Sustainability Reporting (BRSR)",
            "statutory_reference": "SEBI LODR Regulation 34(2)(f) and SEBI/HO/CFD/CFD-SEC-2/P/CIR/2023/122",
            "guideline": "National Guidelines on Responsible Business Conduct (NGRBC)",
            "applicable_financial_years": ["2022-23", "2023-24", "2024-25", "2025-26"]
        }
    }
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Generate JSON on module import if not present
if not RULES_FILE.exists():
    export_rules_json()
