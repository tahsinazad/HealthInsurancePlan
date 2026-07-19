import streamlit as st
import pandas as pd
st.set_page_config(page_title="Health Insurance Plan Advisor",page_icon="🏥",layout="wide")
st.markdown(
    """
    
    <style>
        :root {
            --color-bg: #EAF5FB;
            --color-card: #FFFFFF;
            --color-primary: #1C6FA8;
            --color-primary-dark: #145988;
            --color-accent: #5FC2D9;
            --color-text: #1C3A4B;
            --color-text-muted: #5A7A8E;
            --color-border: #CFE7F5;
        }

        [data-testid="stAppViewContainer"] {
            background-color: var(--color-bg);
        }

        /* Force readable text color everywhere by default, regardless of
           light/dark system theme, then re-enable white text only where
           it's actually needed (primary buttons, the logo icon). */
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stAppViewContainer"] div,
        [data-testid="stAppViewContainer"] li,
        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3,
        [data-testid="stAppViewContainer"] h4,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] * {
            color: var(--color-text);
        }

        [data-testid="stHeader"] {
            background-color: transparent;
        }

        .main-header {
            text-align: center;
            padding: 1.5rem 0 1rem 0;
        }

        .main-header .logo-mark {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 56px;
            height: 56px;
            border-radius: 16px;
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
            box-shadow: 0 6px 16px rgba(28, 111, 168, 0.25);
        }

        .main-header h1 {
            margin: 0.6rem 0 0.2rem 0;
            color: var(--color-primary-dark) !important;
            font-weight: 800;
        }

        .main-header p {
            color: var(--color-text-muted) !important;
            margin-top: 0;
        }

        .section-label {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            color: var(--color-primary-dark) !important;
            background-color: #FFFFFF;
            border: 1px solid var(--color-border);
            border-radius: 999px;
            padding: 0.3rem 0.9rem;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.06rem;
            margin-top: 1.4rem;
            margin-bottom: 0.7rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: var(--color-card);
            border-radius: 14px;
            border: 1px solid var(--color-border);
            box-shadow: 0 2px 10px rgba(28, 111, 168, 0.06);
        }

        /* Input widgets: make sure typed/entered text and dropdown text
           is dark-on-white and clearly visible */
        [data-testid="stAppViewContainer"] input,
        [data-testid="stAppViewContainer"] textarea,
        [data-testid="stAppViewContainer"] select,
        .stNumberInput input,
        .stTextInput input {
            color: var(--color-text) !important;
            background-color: #FFFFFF !important;
        }

        /* Buttons */
        button[kind="primary"] {
            background-color: var(--color-primary) !important;
            border-color: var(--color-primary) !important;
        }

        button[kind="primary"],
        button[kind="primary"] p,
        button[kind="primary"] span,
        button[kind="primary"] div {
            color: #FFFFFF !important;
        }

        button[kind="primary"]:hover {
            background-color: var(--color-primary-dark) !important;
            border-color: var(--color-primary-dark) !important;
        }

        button[kind="secondary"] {
            background-color: #FFFFFF !important;
            border-color: var(--color-border) !important;
        }

        button[kind="secondary"],
        button[kind="secondary"] p,
        button[kind="secondary"] span,
        button[kind="secondary"] div {
            color: var(--color-primary-dark) !important;
        }

        div[data-testid="stExpander"] {
            background-color: var(--color-card);
            border: 1px solid var(--color-border);
            border-radius: 12px;
        }

        /* Dataframe / table text */
        [data-testid="stDataFrame"] * {
            color: var(--color-text) !important;
        }

        /* Alert boxes (info/success/warning/error) keep their own
           built-in contrast-safe colors, so leave those untouched. */
    </style>
    """,
    unsafe_allow_html=True
)

# Default values used when a new plan is added
DEFAULT_PLAN = {"name": "",
    "premium": 250.0,
    "deductible": 2000.0,
    "oop_max": 6000.0,
    "doctor_copay": 25.0,
    "rx_copay": 15.0,
    "er_coinsurance": 20,
    "hospital_coinsurance": 20,
    "quality": 3}

if "plans" not in st.session_state:
    st.session_state.plans = [
        {
            "name": "Plan A",
            "premium": 200.0,
            "deductible": 3000.0,
            "oop_max": 7000.0,
            "doctor_copay": 30.0,
            "rx_copay": 15.0,
            "er_coinsurance": 20,
            "hospital_coinsurance": 20,
            "quality": 3
        },
        {
            "name": "Plan B",
            "premium": 300.0,
            "deductible": 1500.0,
            "oop_max": 5000.0,
            "doctor_copay": 20.0,
            "rx_copay": 10.0,
            "er_coinsurance": 20,
            "hospital_coinsurance": 20,
            "quality": 4
        }
    ]

if "compared" not in st.session_state:
    st.session_state.compared = False


def allocate_deductible_proportionally(service_costs, deductible):
    total_allowed = sum(service_costs.values())
    if total_allowed <= 0 or deductible <= 0:
        return dict((name, 0.0) for name in service_costs), 0.0
    deductible_used = min(float(deductible), float(total_allowed))
    allocations = {}
    for name, allowed_cost in service_costs.items():
        allocations[name] = deductible_used * (allowed_cost / total_allowed)
    return allocations, deductible_used


def cap_cost_components(cost_components, oop_max):
    raw_total = sum(cost_components.values())
    if raw_total <= 0:
        return dict((name, 0.0) for name in cost_components), 0.0, False
    if oop_max <= 0 or raw_total <= oop_max:
        return cost_components.copy(), raw_total, False
    scale = float(oop_max) / float(raw_total)
    capped_components = {}
    for name, cost in cost_components.items():
        capped_components[name] = cost * scale
    return capped_components, float(oop_max), True


def estimate_annual_cost(plan,doctor_visits,prescriptions_per_month,
    er_visits,
    hospital_stays,
    er_allowed_cost,
    hospital_allowed_cost
):
    annual_premium = float(plan["premium"]) * 12.0
    doctor_cost_raw = float(plan["doctor_copay"]) * int(doctor_visits)
    annual_prescriptions = int(prescriptions_per_month) * 12
    prescription_cost_raw = float(plan["rx_copay"]) * annual_prescriptions

    allowed_costs = {"ER care": float(er_allowed_cost) * int(er_visits),
        "Hospital care": float(hospital_allowed_cost) * int(hospital_stays)}

    deductible_allocations, deductible_used = allocate_deductible_proportionally(
        allowed_costs,float(plan["deductible"]))

    er_remaining_after_deductible = max(0.0, allowed_costs["ER care"] - deductible_allocations["ER care"])
    hospital_remaining_after_deductible = max(0.0, allowed_costs["Hospital care"] - deductible_allocations["Hospital care"])

    er_cost_raw = (deductible_allocations["ER care"]
        + er_remaining_after_deductible * (float(plan["er_coinsurance"]) / 100.0))

    hospital_cost_raw = (
        deductible_allocations["Hospital care"]
        + hospital_remaining_after_deductible * (float(plan["hospital_coinsurance"]) / 100.0))

    raw_components = {
        "Doctor visits": doctor_cost_raw,
        "Prescriptions": prescription_cost_raw,
        "ER care": er_cost_raw,
        "Hospital care": hospital_cost_raw}

    capped_components, capped_medical_spending, oop_cap_reached = cap_cost_components(
        raw_components, float(plan["oop_max"]))

    raw_medical_spending = sum(raw_components.values())
    total_annual_cost = annual_premium + capped_medical_spending

    return {"plan": plan["name"].strip(),
        "annual_premium": annual_premium,
        "doctor_cost": capped_components["Doctor visits"],
        "prescription_cost": capped_components["Prescriptions"],
        "er_cost": capped_components["ER care"],
        "hospital_cost": capped_components["Hospital care"],
        "medical_spending_before_cap": raw_medical_spending,
        "out_of_pocket": capped_medical_spending,
        "total": total_annual_cost,
        "quality": int(plan["quality"]),
        "deductible_used": deductible_used,
        "oop_cap_reached": oop_cap_reached}


def find_main_cost_driver(result):
    categories = {"doctor visits": result["doctor_cost"],
        "prescriptions": result["prescription_cost"],"ER care": result["er_cost"],
        "hospital care": result["hospital_cost"]}
    return max(categories.items(), key=lambda item: item[1])


def validate_inputs(plans, er_visits, hospital_stays, er_allowed_cost, hospital_allowed_cost):
    errors = []
    seen_names = set()
    for index, plan in enumerate(plans):
        label = "Plan " + chr(65 + index)
        name = plan["name"].strip()
        if not name:
            errors.append(label + " needs a plan name.")
        elif name.lower() in seen_names:
            errors.append("Plan names must be unique.")
        else:
            seen_names.add(name.lower())
        if float(plan["oop_max"]) <= 0:
            errors.append(name + " needs an out-of-pocket maximum greater than $0.")
        if (float(plan["oop_max"]) > 0
            and float(plan["deductible"]) > float(plan["oop_max"])
        ):
            errors.append(name + " has a deductible greater than its out-of-pocket maximum.")
    if int(er_visits) > 0 and float(er_allowed_cost) <= 0:
        errors.append("Enter an estimated ER allowed cost greater than $0 when ER visits are expected.")
    if int(hospital_stays) > 0 and float(hospital_allowed_cost) <= 0:
        errors.append("Enter an estimated hospital allowed cost greater than $0 when hospital stays are expected.")
    return errors


st.markdown(
    """
    <div class="main-header">
        <div class="logo-mark">
            <svg width="30" height="30" viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg">
                <rect x="12" y="4" width="6" height="22" rx="2" fill="#FFFFFF" />
                <rect x="4" y="12" width="22" height="6" rx="2" fill="#FFFFFF" />
            </svg>
        </div>
        <h1>Health Insurance Plan Advisor</h1>
        <p>Compare estimated annual costs based on expected healthcare use.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "This academic proof-of-concept provides simplified estimates. "
    "It is not financial, insurance, or medical advice."
)

st.markdown('<div class="section-label">STEP 1 · EXPECTED HEALTHCARE USAGE</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    doctor_visits = st.number_input(
        "Doctor visits per year",
        min_value=0,
        value=3,
        step=1,
        help="Expected routine or primary-care visits during the year.")

with col2:
    prescriptions_per_month = st.number_input(
        "Generic prescriptions per month",
        min_value=0,
        value=0,
        step=1,
        help="Average number of generic prescriptions filled per month.")

with col3:
    er_visits = st.number_input("ER visits per year", min_value=0, value=0, step=1)
with col4:
    hospital_stays = st.number_input("Hospital stays per year", min_value=0, value=0, step=1)
with st.expander("Model assumptions: estimated service prices"):
    st.write("Coinsurance is calculated as a percentage of an estimated allowed "
        "service cost. These values are editable model assumptions.")
    assumption_col1, assumption_col2 = st.columns(2)
    with assumption_col1:
        er_allowed_cost = st.number_input(
            "Estimated allowed cost per ER visit ($)",
            min_value=0.0,
            value=2000.0,
            step=100.0)
    with assumption_col2:
        hospital_allowed_cost = st.number_input(
            "Estimated allowed cost per hospital stay ($)",
            min_value=0.0,
            value=10000.0,
            step=500.0)

st.markdown('<div class="section-label">STEP 2 · INSURANCE PLANS</div>', unsafe_allow_html=True)
plan_columns = st.columns(len(st.session_state.plans))
for index, column in enumerate(plan_columns):
    plan = st.session_state.plans[index]
    with column:
        card = st.container()
        with card:
            st.subheader("🩺 Plan " + chr(65 + index))
            plan["name"] = st.text_input(
                "Plan name",
                value=plan["name"] or "Plan " + chr(65 + index),
                key="name_" + str(index))
            plan["premium"] = st.number_input(
                "Monthly premium ($)",
                min_value=0.0,
                value=float(plan["premium"]),
                step=10.0,
                key="premium_" + str(index),
                help="The amount paid each month to keep the insurance plan.")
            plan["deductible"] = st.number_input(
                "Annual deductible ($)",
                min_value=0.0,
                value=float(plan["deductible"]),
                step=100.0,
                key="deductible_" + str(index),
                help="ER and hospital costs share this annual deductible before coinsurance is applied.")
            plan["oop_max"] = st.number_input(
                "Annual out-of-pocket maximum ($)",
                min_value=0.0,
                value=float(plan["oop_max"]),
                step=100.0,
                key="oop_" + str(index),
                help="Maximum annual modeled medical spending, excluding premiums.")
            plan["doctor_copay"] = st.number_input(
                "Doctor visit copay ($)",
                min_value=0.0,
                value=float(plan["doctor_copay"]),
                step=5.0,
                key="doctor_" + str(index))
            plan["rx_copay"] = st.number_input(
                "Generic prescription copay ($)",
                min_value=0.0,
                value=float(plan["rx_copay"]),
                step=5.0,
                key="rx_" + str(index))
            plan["er_coinsurance"] = st.slider(
                "ER coinsurance after deductible (%)",
                min_value=0,
                max_value=100,
                value=int(plan["er_coinsurance"]),
                step=5,
                key="er_coinsurance_" + str(index))
            plan["hospital_coinsurance"] = st.slider(
                "Hospital coinsurance after deductible (%)",
                min_value=0,
                max_value=100,
                value=int(plan["hospital_coinsurance"]),
                step=5,
                key="hospital_coinsurance_" + str(index))
            plan["quality"] = st.slider(
                "Quality rating",
                min_value=1,
                max_value=5,
                value=int(plan["quality"]),
                key="quality_" + str(index),
                help="Used only to break an exact estimated-cost tie.")

st.write("")
button_col1, button_col2, remaining_space = st.columns([1, 1, 3])
with button_col1:
    if len(st.session_state.plans) < 4:
        if st.button("+ Add plan"):
            next_letter = chr(65 + len(st.session_state.plans))
            new_plan = DEFAULT_PLAN.copy()
            new_plan["name"] = "Plan " + next_letter
            st.session_state.plans.append(new_plan)
            st.session_state.compared = False
            st.rerun()
with button_col2:
    if len(st.session_state.plans) > 2:
        if st.button("- Remove last"):
            st.session_state.plans.pop()
            st.session_state.compared = False
            st.rerun()
validation_errors = validate_inputs(st.session_state.plans,er_visits,
    hospital_stays,er_allowed_cost,hospital_allowed_cost)
if validation_errors:
    for validation_error in validation_errors:
        st.warning(validation_error)
st.write("")
left_space, center_button, right_space = st.columns([1, 2, 1])
with center_button:
    if st.button("Compare plans", type="primary", use_container_width=True):
        if validation_errors:
            st.session_state.compared = False
            st.error("Please correct the highlighted input issues before comparing.")
        else:
            st.session_state.compared = True
if st.session_state.compared and not validation_errors:
    results = []
    for plan in st.session_state.plans:
        result = estimate_annual_cost(plan,doctor_visits,prescriptions_per_month,
                                      er_visits,hospital_stays,er_allowed_cost,hospital_allowed_cost)
        results.append(result)
    results_sorted = sorted(results,
        key=lambda result: (round(result["total"], 2), -result["quality"]))
    best = results_sorted[0]
    most_expensive = results_sorted[-1]
    savings = most_expensive["total"] - best["total"]
    st.markdown('<div class="section-label">STEP 3 · RESULTS</div>', unsafe_allow_html=True)
    st.success(
        (
            "Recommended: {0}\n\n"
            "Estimated annual cost: \\${1:,.0f}\n\n"
            "Estimated savings compared with the most expensive option: \\${2:,.0f}"
        ).format(
            best["plan"],
            best["total"],
            savings
        )
    )
    st.subheader("📊 Annual cost comparison")
    table_rows = []
    for rank, result in enumerate(results_sorted, start=1):
        table_rows.append(
            {
                "Rank": rank,
                "Plan": result["plan"],
                "Annual premium": "${:,.0f}".format(result["annual_premium"]),
                "Estimated medical spending": "${:,.0f}".format(result["out_of_pocket"]),
                "Total estimated annual cost": "${:,.0f}".format(result["total"]),
                "Quality rating": "{}/5".format(result["quality"]),
                "OOP maximum reached": "Yes" if result["oop_cap_reached"] else "No"
            }
        )
    comparison_table = pd.DataFrame(table_rows)
    st.dataframe(comparison_table, use_container_width=True)
    st.subheader("💊 Estimated cost breakdown")
    chart_rows = []
    for result in results_sorted:
        chart_rows.append(
            {
                "Plan": result["plan"],
                "Annual premium": result["annual_premium"],
                "Doctor visits": result["doctor_cost"],
                "Prescriptions": result["prescription_cost"],
                "ER care": result["er_cost"],
                "Hospital care": result["hospital_cost"]
            }
        )
    chart_data = pd.DataFrame(chart_rows).set_index("Plan")
    st.bar_chart(chart_data)
    main_driver_name, main_driver_cost = find_main_cost_driver(best)
    st.subheader("✅ Why this plan?")
    explanation = (
        "Based on your expected use of "
        "{} doctor visit(s), "
        "{} generic prescription(s) per month, "
        "{} ER visit(s), and "
        "{} hospital stay(s), "
        "{} produced the lowest estimated annual cost of "
        "${:,.0f}. ".format(
            doctor_visits,
            prescriptions_per_month,
            er_visits,
            hospital_stays,
            best["plan"],
            best["total"]
        )
    )
    if main_driver_cost > 0:
        explanation += "Its largest estimated non-premium cost category was {} at approximately ${:,.0f}. ".format(
            main_driver_name,
            main_driver_cost
        )
    else:
        explanation += "No healthcare services generating out-of-pocket costs were entered. "
    if best["oop_cap_reached"]:
        explanation += "The plan's out-of-pocket maximum was reached in this scenario. "
    explanation += "The plan has a quality rating of {}/5. Quality is used only to break an exact estimated-cost tie.".format(
        best["quality"]
    )
    st.write(explanation.replace("$", "\\$"))
    with st.expander("How this estimate was calculated"):
        st.write(
            "The model annualizes monthly premiums and uses fixed copays for doctor visits and generic prescriptions. "
            "ER and hospital services share one annual deductible. Because this model uses annual utilization totals "
            "rather than a calendar of individual events, it allocates the deductible proportionally across ER and "
            "hospital allowed costs. This prevents the result from depending on whether ER or hospital care is "
            "processed first. "
            "After the deductible is allocated, the applicable coinsurance percentage is applied to the remaining "
            "allowed cost in each category. Total medical spending is capped at the annual out-of-pocket maximum. "
            "If the cap is reached, displayed medical cost categories are scaled proportionally so the chart and "
            "table reconcile with the capped total. "
            "Annual premiums are then added to medical spending to produce the estimated total annual cost. "
            "This simplified model does not account for provider networks, uncovered services, negotiated prices, "
            "specialist visits, family deductibles, separate prescription deductibles, or every variation found in "
            "actual insurance contracts.")