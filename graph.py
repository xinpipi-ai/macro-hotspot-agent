"""Orchestrator: planner → sector → parallel(macro, stock, risk) → judge → portfolio.

Follows the report's architecture with a practical tweak: sector_worker runs
before the parallel phase so stock_worker has a bounded candidate pool.
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from agents import planner, sector_worker, macro_worker, stock_worker, risk_worker, evidence_judge, portfolio_builder
from config import OUTPUT_DIR


def run_macro_pipeline(event: str, verbose: bool = True) -> dict:
    """Full workflow for one macro event.

    Returns final state dict.
    """
    state = {"event": event, "timestamp": datetime.now().isoformat()}

    # Step 1: Planner
    if verbose:
        print("\n[1/5] 🧭 Planner: interpreting event and picking reasoning paths...")
    state["plan"] = planner.plan(event)
    if verbose:
        print(f"    Summary: {state['plan'].get('event_summary')}")
        print(f"    Category: {state['plan'].get('event_category')} | Horizon: {state['plan'].get('time_horizon')}")
        print(f"    Reasoning paths: {state['plan'].get('selected_reasoning_paths')}")

    # Step 2: Sector Worker (sequential — needed for stock_worker)
    if verbose:
        print("\n[2/5] 🏭 Sector Worker: mapping event to SW L1 industries...")
    state["sector"] = sector_worker.analyze(event, state["plan"])
    beneficiaries = [s["name"] for s in state["sector"].get("beneficiary_sectors", [])]
    if verbose:
        print(f"    Beneficiary sectors: {beneficiaries}")

    if not beneficiaries:
        raise RuntimeError("Sector worker returned no beneficiary sectors — cannot proceed.")

    # Step 3: Parallel — macro, stock, risk
    if verbose:
        print("\n[3/5] 🔀 Parallel workers: macro + stock + risk...")
    with ThreadPoolExecutor(max_workers=3) as pool:
        fut_macro = pool.submit(macro_worker.analyze, event, state["plan"])
        fut_stock = pool.submit(stock_worker.analyze, event, state["plan"], state["sector"])
        fut_risk = pool.submit(risk_worker.analyze, event, state["plan"])

        state["macro"] = fut_macro.result()
        state["stock"] = fut_stock.result()
        state["risk"] = fut_risk.result()

    if verbose:
        print(f"    ✓ macro: direction={state['macro'].get('impact_direction')}, magnitude={state['macro'].get('magnitude_score')}/10")
        print(f"    ✓ stock: {len(state['stock'].get('picks', []))} picks")
        print(f"    ✓ risk: {len(state['risk'].get('failure_conditions', []))} failure conditions")

    # Step 4: Evidence Judge
    if verbose:
        print("\n[4/5] ⚖️  Evidence Judge: arbitrating 4 perspectives...")
    state["judge"] = evidence_judge.judge(
        event, state["macro"], state["sector"], state["stock"], state["risk"]
    )
    if verbose:
        print(f"    Overall score: {state['judge'].get('overall_score')}/10")
        print(f"    Recommendation: {state['judge'].get('final_recommendation')}")

    # Step 5: Portfolio Builder
    if verbose:
        print("\n[5/5] 📊 Portfolio Builder: assembling weighted portfolio...")
    state["portfolio"] = portfolio_builder.build(state["stock"], state["judge"])
    if verbose:
        print(f"    Final portfolio: {state['portfolio']['size']} stocks, buckets={state['portfolio']['bucket_counts']}")

    # Save artifact
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_event = "".join(c if c.isalnum() or c in "()-_" else "_" for c in event)[:40]
    out_path = OUTPUT_DIR / f"{safe_event}_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2, default=str)
    if verbose:
        print(f"\n💾 Saved to {out_path}")

    return state
