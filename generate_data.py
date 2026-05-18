"""Synthetic data generator for the Penn State Health Telestroke PoC.

Produces three CSV files under data/:
  - telestroke_synthetic.csv     (500 patient records, ~60 fields including derived KPI columns)
  - cart_uptime_synthetic.csv    (monthly cart uptime per facility)
  - monthly_cost_synthetic.csv   (monthly cost of delivery and downstream revenue)

All data is synthetic. MRN values are prefixed SYN- to make that obvious.
Timestamps are internally consistent:
  ed_arrival_dt < stroke_alert_initiation_dt < call_to_provider_dt
  < provider_response_dt < neurologist_evaluation_start_dt
  < treatment_decision_dt < thrombolysis_administration_dt
  < consult_signed_dt < depart_dt
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

RNG_SEED = 42
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

N_RECORDS = 500

FACILITIES = [
    "Hershey Medical Center",
    "Holy Spirit",
    "Mount Nittany",
    "Hampden",
    "Good Samaritan",
    "St. Joseph",
]

CONSULTANTS = [
    "Dr. A. Singh",
    "Dr. M. Patel",
    "Dr. R. Chen",
    "Dr. L. Torres",
    "Dr. K. Williams",
    "Dr. J. Okafor",
]

ENCOUNTER_TYPES = ["Audio/Video", "Phone", "Reg-No Consult"]
ENCOUNTER_WEIGHTS = [0.70, 0.20, 0.10]

# FY runs July through June. FY2023-2024 = Jul 2023 - Jun 2024.
FISCAL_YEARS = {
    "FY2023-2024": (datetime(2023, 7, 1), datetime(2024, 6, 30)),
    "FY2024-2025": (datetime(2024, 7, 1), datetime(2025, 6, 30)),
    "FY2025-2026": (datetime(2025, 7, 1), datetime(2026, 6, 30)),
}

FY_MONTH_NAMES = [
    "July", "August", "September", "October", "November", "December",
    "January", "February", "March", "April", "May", "June",
]

CALENDAR_TO_FY_MONTH = {
    7: ("July", 1, "Q1"),
    8: ("August", 2, "Q1"),
    9: ("September", 3, "Q1"),
    10: ("October", 4, "Q2"),
    11: ("November", 5, "Q2"),
    12: ("December", 6, "Q2"),
    1: ("January", 7, "Q3"),
    2: ("February", 8, "Q3"),
    3: ("March", 9, "Q3"),
    4: ("April", 10, "Q4"),
    5: ("May", 11, "Q4"),
    6: ("June", 12, "Q4"),
}

STROKE_DIAGNOSES = ["Ischemic Stroke", "TIA", "Hemorrhagic Stroke", "Mimics"]
STROKE_DIAGNOSIS_WEIGHTS = [0.55, 0.20, 0.15, 0.10]

DISCHARGE_DESTINATIONS = ["Home", "Rehab", "SNF", "Expired", "Other"]
DISCHARGE_WEIGHTS = [0.40, 0.25, 0.15, 0.03, 0.17]

PAYERS = ["Medicare", "Medicaid", "Commercial", "Self-Pay"]
PAYER_WEIGHTS = [0.45, 0.15, 0.30, 0.10]

OUTLIER_REASONS = [
    "Uncontrolled Hypertension",
    "Consent Delay",
    "Extended Treatment Window",
    "None",
]


def weighted_nihss():
    # Realistic distribution — most cases 4-16, long tail to 42
    buckets = (
        list(range(0, 4)) * 1
        + list(range(4, 17)) * 4
        + list(range(17, 25)) * 2
        + list(range(25, 43)) * 1
    )
    return int(random.choice(buckets))


def weighted_mrs_pre():
    # Pre-stroke mRS weighted toward 0-1
    return int(np.random.choice([0, 1, 2, 3, 4, 5], p=[0.45, 0.30, 0.12, 0.08, 0.03, 0.02]))


def weighted_mrs_discharge():
    return int(np.random.choice(range(7), p=[0.10, 0.18, 0.20, 0.18, 0.14, 0.12, 0.08]))


def weighted_mrs_90day():
    # Generally improves vs discharge
    return int(np.random.choice(range(7), p=[0.18, 0.22, 0.20, 0.15, 0.12, 0.08, 0.05]))


def random_datetime_in_fy(fy_label: str) -> datetime:
    start, end = FISCAL_YEARS[fy_label]
    span_seconds = int((end - start).total_seconds())
    offset = random.randint(0, span_seconds)
    return start + timedelta(seconds=offset)


def time_of_day_block(dt: datetime) -> str:
    h = dt.hour
    if 8 <= h < 16:
        return "Morning (8a-4p)"
    if 16 <= h < 24:
        return "Evening (4p-12a)"
    return "Night (12a-8a)"


def pick_treatment_agent(fy_label: str, eligible: bool) -> str:
    if not eligible:
        return "None"
    if fy_label == "FY2023-2024":
        return "tPA"
    return "TNK"


def generate_patient_records(n: int) -> pd.DataFrame:
    records = []
    # Distribute roughly equally across FYs (~167 per FY)
    fy_assignments = []
    per_fy = n // len(FISCAL_YEARS)
    for fy_label in FISCAL_YEARS:
        fy_assignments.extend([fy_label] * per_fy)
    while len(fy_assignments) < n:
        fy_assignments.append(random.choice(list(FISCAL_YEARS.keys())))
    random.shuffle(fy_assignments)

    for i in range(n):
        fy = fy_assignments[i]
        ed_arrival = random_datetime_in_fy(fy)

        month_name, month_number, quarter = CALENDAR_TO_FY_MONTH[ed_arrival.month]

        facility = random.choice(FACILITIES)
        consultant = random.choice(CONSULTANTS)
        encounter_type = np.random.choice(ENCOUNTER_TYPES, p=ENCOUNTER_WEIGHTS)

        # Timestamp chain
        stroke_alert = ed_arrival + timedelta(minutes=random.randint(5, 25))
        last_known_normal = ed_arrival - timedelta(minutes=random.randint(30, 360))
        call_to_provider = stroke_alert + timedelta(minutes=random.randint(2, 10))
        provider_response = call_to_provider + timedelta(minutes=random.randint(1, 20))
        neurologist_eval_start = provider_response + timedelta(minutes=random.randint(1, 5))
        consult_signed = neurologist_eval_start + timedelta(minutes=random.randint(20, 60))
        depart = ed_arrival + timedelta(minutes=random.randint(60, 240))

        # Audio/Video-only fields
        is_av = encounter_type == "Audio/Video"
        eligible = is_av and np.random.random() < 0.40

        if is_av:
            treatment_decision = neurologist_eval_start + timedelta(minutes=random.randint(5, 30))
            order_entry = treatment_decision + timedelta(minutes=random.randint(1, 5))
        else:
            treatment_decision = pd.NaT
            order_entry = pd.NaT

        agent = pick_treatment_agent(fy, eligible)
        if eligible and is_av:
            thrombolysis_admin = treatment_decision + timedelta(minutes=random.randint(2, 15))
        else:
            thrombolysis_admin = pd.NaT

        # Clinical scores
        nihss = weighted_nihss()
        pre_mrs = weighted_mrs_pre()
        discharge_mrs = weighted_mrs_discharge()
        ninety_day_mrs = weighted_mrs_90day() if np.random.random() > 0.30 else np.nan

        nihss_compliance = "Yes" if np.random.random() < 0.85 else "No"
        consent_completed = "Yes" if np.random.random() < 0.78 else "No"

        # Disposition
        transferred = np.random.random() < 0.45
        transfer_status = "Transferred" if transferred else "Not Transferred"
        transfer_destination = "Hershey Medical Center" if transferred else ""
        discharge_destination = np.random.choice(DISCHARGE_DESTINATIONS, p=DISCHARGE_WEIGHTS)
        lvo = "Yes" if np.random.random() < 0.25 else "No"

        stroke_diagnosis = np.random.choice(STROKE_DIAGNOSES, p=STROKE_DIAGNOSIS_WEIGHTS)
        stroke_subtype = {
            "Ischemic Stroke": np.random.choice(["Large Vessel", "Small Vessel", "Cardioembolic", "Cryptogenic"]),
            "TIA": "TIA",
            "Hemorrhagic Stroke": np.random.choice(["Intracerebral", "Subarachnoid"]),
            "Mimics": np.random.choice(["Migraine", "Seizure", "Functional", "Other"]),
        }[stroke_diagnosis]

        admit_status = np.random.choice(["Admitted", "Observation", "Discharged"], p=[0.60, 0.25, 0.15])
        los_days = int(np.random.choice(range(1, 15), p=np.array([3, 4, 5, 5, 4, 3, 3, 2, 2, 1, 1, 1, 1, 1]) / 36))
        icu = "Yes" if np.random.random() < 0.20 else "No"
        readmission = "Yes" if np.random.random() < 0.12 else "No"

        # Derived times in minutes
        def _mins(later, earlier):
            if pd.isna(later) or pd.isna(earlier):
                return np.nan
            return (later - earlier).total_seconds() / 60.0

        dido_minutes = _mins(depart, ed_arrival)
        door_to_needle = _mins(thrombolysis_admin, ed_arrival)
        symptom_to_treatment = _mins(thrombolysis_admin, last_known_normal)
        door_to_neurologist = _mins(neurologist_eval_start, ed_arrival)
        door_to_cart = _mins(stroke_alert, ed_arrival)
        neuro_to_decision = _mins(treatment_decision, neurologist_eval_start)
        decision_to_admin = _mins(thrombolysis_admin, treatment_decision)

        # Outlier flags
        lkn_to_alert_minutes = _mins(stroke_alert, last_known_normal)
        lkn_flag = "Yes" if lkn_to_alert_minutes >= 270 else "No"  # 4.5 hours
        response_time_outlier = "Yes" if _mins(provider_response, call_to_provider) > 15 else "No"
        outlier_exclusion = "Yes" if eligible and np.random.random() < 0.08 else "No"
        if outlier_exclusion == "Yes":
            outlier_reason = np.random.choice(OUTLIER_REASONS[:-1])  # exclude "None"
        else:
            outlier_reason = "None"

        # Reimbursement — Medicare dominant, LVO/admit boost
        payer = np.random.choice(PAYERS, p=PAYER_WEIGHTS)
        base = {"Admitted": 18000, "Observation": 12000, "Discharged": 9000}[admit_status]
        if lvo == "Yes":
            base += 12000
        if payer == "Self-Pay":
            base *= 0.55
        reimbursement = float(np.clip(base + np.random.normal(0, 3000), 8000, 45000))

        # Identifiers
        mrn = f"SYN-{random.randint(10000000, 99999999)}"
        fin = str(random.randint(1000000000, 9999999999))
        case_number = f"CASE-{i + 1:05d}" if fy == "FY2025-2026" else ""

        # Phase 2 missingness on LOS/ICU/readmit for non-admitted
        if admit_status == "Discharged":
            los_days = np.nan
            icu = np.nan if np.random.random() < 0.5 else icu

        treatment_administered = "Yes" if eligible and agent != "None" else "No"

        records.append({
            # Period
            "fiscal_year": fy,
            "month_name": month_name,
            "month_number": month_number,
            "quarter": quarter,
            # Identifiers
            "mrn": mrn,
            "fin": fin,
            "case_number": case_number,
            "facility": facility,
            "consultant_name": consultant,
            "encounter_type": encounter_type,
            # Presentation timestamps
            "ed_arrival_dt": ed_arrival,
            "stroke_alert_initiation_dt": stroke_alert,
            "last_known_normal_dt": last_known_normal,
            # Consult initiation
            "call_to_provider_dt": call_to_provider,
            "provider_response_dt": provider_response,
            "neurologist_evaluation_start_dt": neurologist_eval_start,
            # Treatment
            "treatment_decision_dt": treatment_decision,
            "thrombolysis_eligibility_indicator": "Yes" if eligible else "No",
            "treatment_agent": agent,
            "thrombolysis_administration_dt": thrombolysis_admin,
            "order_entry_dt": order_entry,
            # Closure
            "consult_signed_dt": consult_signed,
            "depart_dt": depart,
            "dido_time_minutes": dido_minutes,
            # Clinical assessment
            "nihss_score": nihss,
            "pre_mrs_score": pre_mrs,
            "discharge_mrs_score": discharge_mrs,
            "ninety_day_mrs_score": ninety_day_mrs,
            "nihss_documentation_compliance": nihss_compliance,
            "consent_form_completed": consent_completed,
            # Disposition / transfer
            "transfer_status": transfer_status,
            "transfer_destination": transfer_destination,
            "discharge_destination": discharge_destination,
            "lvo_indicator": lvo,
            # Procedures & outcomes
            "treatment_administered": treatment_administered,
            "stroke_diagnosis": stroke_diagnosis,
            "stroke_subtype": stroke_subtype,
            "admit_status": admit_status,
            "length_of_stay_days": los_days,
            "icu_admission": icu,
            "thirty_day_readmission": readmission,
            "door_to_needle_time_minutes": door_to_needle,
            "symptom_to_treatment_time_minutes": symptom_to_treatment,
            # Quality flags
            "lkn_flag": lkn_flag,
            "response_time_outlier_flag": response_time_outlier,
            "outlier_exclusion_flag": outlier_exclusion,
            "outlier_exception_reason": outlier_reason,
            # Financial
            "payer_category": payer,
            "reimbursement_amount": round(reimbursement, 2),
            # Derived KPI fields
            "door_to_needle_compliant": "Yes" if pd.notna(door_to_needle) and door_to_needle <= 60 else ("No" if pd.notna(door_to_needle) else ""),
            "door_to_needle_compliant_45": "Yes" if pd.notna(door_to_needle) and door_to_needle <= 45 else ("No" if pd.notna(door_to_needle) else ""),
            "door_to_needle_compliant_30": "Yes" if pd.notna(door_to_needle) and door_to_needle <= 30 else ("No" if pd.notna(door_to_needle) else ""),
            "door_to_neurologist_minutes": door_to_neurologist,
            "door_to_cart_minutes": door_to_cart,
            "neurologist_to_decision_minutes": neuro_to_decision,
            "decision_to_administration_minutes": decision_to_admin,
            "time_of_day_block": time_of_day_block(ed_arrival),
            # Provider response in minutes (helpful for downstream KPIs)
            "provider_response_minutes": _mins(provider_response, call_to_provider),
        })

    return pd.DataFrame(records)


def generate_cart_uptime() -> pd.DataFrame:
    rows = []
    for fy_label in FISCAL_YEARS:
        for month_name in FY_MONTH_NAMES:
            for facility in FACILITIES:
                uptime = round(np.random.uniform(94.0, 99.8), 2)
                rows.append({
                    "fiscal_year": fy_label,
                    "month_name": month_name,
                    "facility": facility,
                    "cart_uptime_pct": uptime,
                })
    return pd.DataFrame(rows)


def generate_monthly_cost() -> pd.DataFrame:
    rows = []
    for fy_label in FISCAL_YEARS:
        for month_name in FY_MONTH_NAMES:
            cost = round(np.random.uniform(45000, 65000), 2)
            revenue = round(np.random.uniform(180000, 420000), 2)
            rows.append({
                "fiscal_year": fy_label,
                "month_name": month_name,
                "total_monthly_cost": cost,
                "downstream_revenue": revenue,
            })
    return pd.DataFrame(rows)


def main():
    print("Generating Telestroke synthetic data...")
    patients = generate_patient_records(N_RECORDS)
    cart = generate_cart_uptime()
    costs = generate_monthly_cost()

    patients_path = os.path.join(DATA_DIR, "telestroke_synthetic.csv")
    cart_path = os.path.join(DATA_DIR, "cart_uptime_synthetic.csv")
    costs_path = os.path.join(DATA_DIR, "monthly_cost_synthetic.csv")

    patients.to_csv(patients_path, index=False)
    cart.to_csv(cart_path, index=False)
    costs.to_csv(costs_path, index=False)

    print("---")
    print(f"Patient records:    {len(patients):>5} rows  x  {patients.shape[1]:>3} fields  ->  {patients_path}")
    print(f"Cart uptime rows:   {len(cart):>5} rows  x  {cart.shape[1]:>3} fields  ->  {cart_path}")
    print(f"Monthly cost rows:  {len(costs):>5} rows  x  {costs.shape[1]:>3} fields  ->  {costs_path}")
    print("---")
    print("Fiscal year distribution:")
    print(patients["fiscal_year"].value_counts().sort_index().to_string())
    print("---")
    print("Encounter type distribution:")
    print(patients["encounter_type"].value_counts(normalize=True).round(3).to_string())
    print("---")
    print("Generation complete.")


if __name__ == "__main__":
    main()
