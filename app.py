# app.py
# Flask backend for CEA – Circular Economy AI
# Run with:  python app.py
# Then open: http://127.0.0.1:5000

from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__)

SUSPICIOUS_WORDS = [
    "rob", "steal", "attack", "bomb", "kill", "hurt",
    "terror", "hack", "fraud", "bribe"
]

YEARS = [2023, 2024, 2025, 2026, 2027]

CHART_DATA = {
    "housing": {
        "label": "Projected Housing Stress Index (lower is better) – CEA reduces stress over time.",
        "baseline": [72, 74, 75, 76, 77],
        "withCEA": [72, 70, 67, 64, 60],
        "higherBetter": False
    },
    "education": {
        "label": "Projected Education Access & Quality Index (higher is better) – CEA improves targeting.",
        "baseline": [65, 66, 67, 68, 68],
        "withCEA": [65, 68, 71, 74, 77],
        "higherBetter": True
    },
    "healthcare": {
        "label": "Projected Healthcare Capacity Index (higher is better) – CEA supports planning.",
        "baseline": [60, 61, 61, 62, 62],
        "withCEA": [60, 63, 66, 68, 70],
        "higherBetter": True
    },
    "infrastructure": {
        "label": "Infrastructure Efficiency Index (higher is better) – better project selection with CEA.",
        "baseline": [58, 59, 59, 60, 61],
        "withCEA": [58, 62, 66, 69, 72],
        "higherBetter": True
    },
    "agriculture": {
        "label": "Sustainable Agriculture Index (higher is better) – more circular, climate‑smart.",
        "baseline": [55, 56, 57, 58, 59],
        "withCEA": [55, 59, 63, 66, 70],
        "higherBetter": True
    },
    "energy": {
        "label": "Clean Energy Share Index (higher is better) – renewables plus circular management.",
        "baseline": [50, 52, 53, 54, 55],
        "withCEA": [50, 55, 60, 65, 70],
        "higherBetter": True
    },
    "waste": {
        "label": "Waste Diversion from Landfill Index (higher is better) – core circular marketplace impact.",
        "baseline": [40, 41, 42, 43, 44],
        "withCEA": [40, 48, 55, 60, 65],
        "higherBetter": True
    },
}

LEARNING_USAGE = {k: 0 for k in CHART_DATA.keys()}
ALERTS = []

# --- Companies store (in-memory demo) ---
COMPANIES = {}        # company_id -> dict
NEXT_COMPANY_ID = 1   # simple counter


# ---------- Helpers ----------

def is_suspicious(text: str) -> bool:
    lower = text.lower()
    return any(word in lower for word in SUSPICIOUS_WORDS)


def update_learning(sector: str) -> None:
    if sector not in CHART_DATA:
        return
    data = CHART_DATA[sector]
    LEARNING_USAGE[sector] = LEARNING_USAGE.get(sector, 0) + 1

    base_step = 0.5
    max_gap = 20

    for i in range(len(data["withCEA"])):
        base = data["baseline"][i]
        current = data["withCEA"][i]

        progress_factor = float(i + 1) / len(data["withCEA"])
        step = base_step * progress_factor

        if data["higherBetter"]:
            target = min(100, base + max_gap)
            if current < target:
                current = min(target, current + step)
        else:
            target = max(0, base - max_gap)
            if current > target:
                current = max(target, current - step)

        data["withCEA"][i] = current


def generate_advice(user_type: str, sector: str) -> str:
    if sector == "housing":
        if user_type == "government":
            return (
                "Use CEA data to map where housing demand is highest and where there is\n"
                "vacant or under-used buildings. Redirect new housing projects to these\n"
                "areas and give incentives to developers who use recycled materials\n"
                "through the CEA circular marketplace.\n\n"
                "Graph idea: Plot average rent vs. vacancy rate by region."
            )
        elif user_type == "business":
            return (
                "Search the CEA marketplace for surplus or recycled construction materials\n"
                "to cut your input costs. List your own surplus stock instead of sending it\n"
                "to landfill – this creates a new revenue stream and supports the circular\n"
                "economy."
            )
        else:
            return (
                "Use public CEA dashboards (future feature) to compare suburbs by rent,\n"
                "services, and public transport. Support projects and policies that reuse\n"
                "building materials to lower both prices and emissions."
            )

    if sector == "education":
        return (
            "CEA can match education spending to local needs: enrolment trends, teacher\n"
            "shortages, and outcomes. Underused equipment can be shared between schools\n"
            "and TAFEs through the circular marketplace instead of being thrown away."
        )

    if sector == "healthcare":
        return (
            "By analysing de‑identified health data, CEA can show where aged care and\n"
            "disability services are under pressure. Equipment that is still safe but no\n"
            "longer needed in one hospital can be transferred to another through the\n"
            "CEA marketplace, instead of being scrapped."
        )

    if sector == "infrastructure":
        return (
            "CEA ranks infrastructure projects by social benefit per dollar: roads,\n"
            "public transport, broadband. Materials from demolished projects can be\n"
            "reused in new builds. This reduces waste and stretches the budget further."
        )

    if sector == "agriculture":
        return (
            "CEA tracks inputs (water, fertiliser, energy) and outputs (crops, waste)\n"
            "to suggest more efficient, climate-smart farming. Organic waste from\n"
            "cities can be fed back to farms as compost via the marketplace."
        )

    if sector == "energy":
        return (
            "CEA identifies high-potential regions for renewables and matches surplus\n"
            "solar/wind power to local demand. It also manages end-of-life solar panels\n"
            "and batteries so they are refurbished or recycled, not dumped."
        )

    if sector == "waste":
        return (
            "This is the core of the circular marketplace: businesses and councils list\n"
            "surplus or waste materials; others buy or exchange them. AI recommends the\n"
            "best matches, reducing landfill and saving on raw material costs."
        )

    return (
        "CEA uses your data to find where resources are wasted and suggests reuse,\n"
        "repair, and sharing solutions across sectors."
    )


def generate_company_growth(start_revenue: float):
    """
    Simple simulated 5-year revenue forecasts:
    - Baseline: grows at 2% per year.
    - With CEA: grows at 5% per year (better resource use, less waste).
    """
    baseline_rate = 0.02
    cea_rate = 0.05

    baseline = []
    with_cea = []
    current_base = start_revenue
    current_cea = start_revenue

    for _ in YEARS:
        baseline.append(round(current_base, 2))
        with_cea.append(round(current_cea, 2))
        current_base *= (1.0 + baseline_rate)
        current_cea *= (1.0 + cea_rate)

    return baseline, with_cea


# ---------- PAGE ROUTES ----------

@app.route("/")
@app.route("/home")
def home():
    return send_from_directory(".", "home.html")


@app.route("/ai")
def ai_page():
    return send_from_directory(".", "ai.html")


@app.route("/contact")
def contact_page():
    return send_from_directory(".", "contact.html")


@app.route("/login")
def login_page():
    return send_from_directory(".", "login.html")


@app.route("/companies")
def companies_page():
    return send_from_directory(".", "companies.html")


# ---------- AI API ROUTES ----------

@app.route("/api/cea", methods=["POST"])
def api_cea():
    data = request.get_json(force=True)
    user_type = data.get("userType", "").lower()
    sector = data.get("sector", "").lower()
    problem = (data.get("problem", "") or "").strip()

    if not problem:
        return jsonify({"error": "Problem text is required."}), 400

    if is_suspicious(problem):
        ALERTS.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "userType": user_type,
            "sector": sector,
            "problem": problem
        })
        return jsonify({
            "suspicious": True,
            "message": "I cannot assist with harmful, violent, or illegal actions."
        })

    if sector not in CHART_DATA:
        return jsonify({"error": f"Unknown sector: {sector}"}), 400

    update_learning(sector)
    advice = generate_advice(user_type, sector)
    d = CHART_DATA[sector]

    header = (
        f"[CEA Analysis] User: {user_type.upper()}, Sector: {sector.upper()}\n"
        "------------------------------------------------------------\n\n"
    )

    return jsonify({
        "suspicious": False,
        "header": header,
        "advice": advice,
        "problem": problem,
        "sector": sector,
        "userType": user_type,
        "years": YEARS,
        "baseline": d["baseline"],
        "withCEA": d["withCEA"],
        "learningUsage": LEARNING_USAGE[sector],
        "label": d["label"]
    })


@app.route("/api/alerts", methods=["GET"])
def api_alerts():
    return jsonify({"alerts": ALERTS})


# ---------- COMPANIES API ROUTES ----------

@app.route("/api/companies", methods=["GET", "POST"])
def api_companies():
    global NEXT_COMPANY_ID

    if request.method == "GET":
        # Return list of all companies
        return jsonify({"companies": list(COMPANIES.values())})

    # POST: add a new company
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    sector = (data.get("sector") or "").strip()
    revenue_raw = (data.get("revenue") or "").strip()

    if not name or not revenue_raw:
        return jsonify({"error": "Name and revenue are required."}), 400

    try:
        start_revenue = float(revenue_raw)
        if start_revenue <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Revenue must be a positive number."}), 400

    baseline, with_cea = generate_company_growth(start_revenue)

    company_id = NEXT_COMPANY_ID
    NEXT_COMPANY_ID += 1

    company = {
        "id": company_id,
        "name": name,
        "sector": sector or "General",
        "startRevenue": start_revenue,
        "years": YEARS,
        "baseline": baseline,
        "withCEA": with_cea
    }

    COMPANIES[company_id] = company
    return jsonify(company), 201


if __name__ == "__main__":
    app.run(debug=True)
