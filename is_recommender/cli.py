"""
Interactive and One-Shot Command Line Interface (CLI) for IS-Recommender.
Enables fast terminal validation of BIS standard recommendations, confidence scores,
matched clauses, and plain-English justifications.
"""
import argparse
import sys
from pathlib import Path

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from is_recommender.recommender import ISRecommender

SAMPLE_SPECS = [
    (
        "Civil: TMT Rebars",
        "Supply of Fe 500D grade TMT thermo-mechanically treated deformed steel bars 12mm and 16mm diameter with minimum 500 N/mm2 proof stress, 565 N/mm2 tensile strength, and 16% elongation for RCC bridge construction."
    ),
    (
        "Civil: Potable Water Pipes",
        "Supply of unplasticized PVC (uPVC) pipes Class 3 (0.6 MPa) 110mm diameter for potable drinking water supply distribution with lead-free formulation and hydrostatic pressure testing."
    ),
    (
        "Electrical: Distribution Transformer",
        "Procurement of 500 kVA, 11 kV / 433 V, 3-phase, 50 Hz, outdoor type oil immersed copper wound distribution transformer conforming to BEE Star 2 energy efficiency loss levels."
    ),
    (
        "Safety: Fire Extinguisher",
        "Portable 6 kg capacity stored pressure ABC dry powder fire extinguisher containing monoammonium phosphate 50% min, with pressure gauge, squeeze grip valve, and fire rating 3A 89B."
    ),
    (
        "Medical / PPE: Surgical Masks",
        "Disposable 3-ply surgical face masks with meltblown filter layer, bacterial filtration efficiency (BFE) > 98%, differential pressure < 29.4 Pa/cm2, and fluid splash resistance at 120 mmHg."
    ),
    (
        "Food / Rations: Wheat Atta",
        "Supply of whole wheat flour (Chakki Atta) in 50 kg bags for government hostel mess: moisture content max 14%, total ash max 2.0%, gluten min 6.0%, free from insect infestation."
    ),
    (
        "Out of Scope / Service Contract",
        "Hiring of 10 security guards and 2 supervisors for round-the-clock 8-hour shift security service at government office complex."
    )
]

def format_recommendation_card(rec: dict) -> str:
    """Formats a single recommendation card for clear terminal readability."""
    rank = rec["rank"]
    std_id = rec["standard_id"]
    title = rec["title"]
    conf_pct = rec["confidence_pct"]
    conf_lvl = rec["confidence_level"]
    qco = rec["qco_compliance"]
    justification = rec["justification"]
    keywords = ", ".join(rec.get("matched_keywords", [])) or "None identified"

    # Color/badge markers
    level_badges = {
        "HIGH": "🟢 [HIGH CONFIDENCE]",
        "MEDIUM": "🟡 [MEDIUM CONFIDENCE]",
        "LOW": "🟠 [LOW CONFIDENCE]",
        "UNCERTAIN": "🔴 [UNCERTAIN]"
    }
    badge = level_badges.get(conf_lvl, f"[{conf_lvl}]")
    qco_badge = "⚖️  MANDATORY QCO (ISI Mark Required on GeM)" if qco.get("is_mandatory") else "ℹ️  Voluntary Standard / Code"

    lines = [
        f"┌─────────────────────────────────────────────────────────────────────────────",
        f"│ RANK #{rank}: {std_id} - {title}",
        f"│ {badge} | Score: {conf_pct}% | {qco_badge}",
        f"│ Sector: {rec.get('sector')} | ICS: {rec.get('ics_code', 'N/A')}",
        f"├─────────────────────────────────────────────────────────────────────────────",
        f"│ 🎯 Plain-English Justification:",
        f"│    {justification}",
        f"│",
        f"│ 🔑 Matched Technical Terms: {keywords}"
    ]

    clauses = rec.get("matched_clauses", [])
    if clauses:
        lines.append("│ 📜 Applicable Clauses:")
        for c in clauses:
            clause_no = c.get("clause_no", "")
            cl_title = c.get("title", "")
            cl_text = c.get("text", "")
            lines.append(f"│    • {clause_no} ({cl_title}): {cl_text[:110]}...")

    if rec.get("superseded_warning"):
        lines.append(f"│ ⚠️  {rec['superseded_warning']}")

    lines.append(f"└─────────────────────────────────────────────────────────────────────────────")
    return "\n".join(lines)

def run_cli_query(recommender: ISRecommender, query: str, top_k: int = 5):
    """Executes recommendation on a query and prints rich terminal output."""
    print("\n" + "=" * 80)
    print("📋 INPUT PROCUREMENT SPECIFICATION:")
    print(f"   \"{query}\"")
    print("=" * 80)

    result = recommender.recommend(query, top_k=top_k)

    print(f"\n⏱️  Execution Time: {result['execution_time_ms']} ms | Status: {result['status']}")

    if result["status"] == "OUT_OF_SCOPE":
        print("\n🚫 [REJECTED - OUT OF SCOPE]")
        print(f"   {result['message']}\n")
        return

    if not result["is_confident"]:
        print("\n⚠️  [LOW CONFIDENCE / UNCERTAIN RESULT]")
        print(f"   {result['message']}\n")

    recs = result.get("recommendations", [])
    if not recs:
        print("   No recommendations generated.\n")
        return

    print(f"\n🏆 TOP {len(recs)} APPLICABLE INDIAN STANDARDS (BIS):\n")
    for rec in recs:
        print(format_recommendation_card(rec))
        print()

def interactive_mode(recommender: ISRecommender):
    """Runs continuous interactive loop in terminal."""
    print("\n" + "=" * 80)
    print("🏛️  IS-RECOMMENDER: BIS Standards Recommender for GeM Procurement")
    print("   Smart India Hackathon (SIH26108) | Ministry of Consumer Affairs & GeM")
    print("=" * 80)

    while True:
        print("\nOPTIONS:")
        print(" [1-7] Run one of the pre-configured sample GeM procurement specs")
        print(" [C]   Type or paste a custom procurement specification")
        print(" [F]   Test Officer Feedback Logging (Accept/Reject demo)")
        print(" [Q]   Quit")

        choice = input("\nEnter choice: ").strip().lower()

        if choice in ["q", "exit", "quit"]:
            print("Exiting IS-Recommender CLI. Goodbye!")
            break

        elif choice in ["1", "2", "3", "4", "5", "6", "7"]:
            idx = int(choice) - 1
            label, spec = SAMPLE_SPECS[idx]
            print(f"\n[Selected Sample #{choice}: {label}]")
            run_cli_query(recommender, spec)

        elif choice == "c":
            custom_spec = input("\nEnter/paste procurement specification:\n> ").strip()
            if custom_spec:
                run_cli_query(recommender, custom_spec)
            else:
                print("Empty input entered.")

        elif choice == "f":
            print("\n--- OFFICER FEEDBACK SIMULATOR ---")
            spec = "Supply of Fe 500D grade TMT steel bars 12mm dia for bridge pier construction"
            print(f"Spec: \"{spec}\"")
            print("Action: Officer ACCEPTS IS 1786:2008")
            log_id = recommender.log_feedback(
                spec_text=spec,
                recommended_standard_id="IS 1786:2008",
                action="ACCEPT",
                officer_notes="Verified by GeM Technical Evaluation Committee"
            )
            print(f"Feedback successfully logged with ID #{log_id} in SQLite feedback_logs table.")
            summary = recommender.feedback_mgr.get_feedback_summary()
            print(f"Updated Feedback Stats: {summary['accepted_count']} accepted, {summary['rejected_count']} rejected, {summary['corrected_count']} corrected.")

        else:
            print("Invalid selection. Please enter 1-7, C, F, or Q.")

def main():
    parser = argparse.ArgumentParser(description="IS-Recommender: BIS Standards Recommender CLI")
    parser.add_argument("--spec", type=str, help="Free-text procurement specification to recommend standards for")
    parser.add_argument("--top_k", type=int, default=5, help="Number of top standards to retrieve (default: 5)")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive terminal mode")

    args = parser.parse_args()

    recommender = ISRecommender()

    if args.spec:
        run_cli_query(recommender, args.spec, top_k=args.top_k)
    elif args.interactive or len(sys.argv) == 1:
        interactive_mode(recommender)

if __name__ == "__main__":
    main()
