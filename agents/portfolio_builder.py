"""Portfolio Builder: assemble final 20-stock weighted portfolio."""
from config import PORTFOLIO_MAX_SIZE


BUCKET_WEIGHTS = {"core": 3, "satellite": 2, "hedge": 1}


def build(stock_result: dict, judge_result: dict) -> dict:
    """
    Dedupe, score, and cap at PORTFOLIO_MAX_SIZE.
    Weight scheme: core=3, satellite=2, hedge=1. Normalize at the end.
    """
    picks = stock_result.get("picks", [])
    # Dedupe by ts_code (keep highest-weighted bucket)
    agg: dict[str, dict] = {}
    for p in picks:
        code = p["ts_code"]
        w = BUCKET_WEIGHTS.get(p.get("bucket", "satellite"), 2)
        if code not in agg or w > agg[code]["raw_weight"]:
            agg[code] = {
                "ts_code": code,
                "name": p["name"],
                "sector": p.get("sector"),
                "bucket": p.get("bucket"),
                "rationale": p.get("rationale"),
                "raw_weight": w,
            }

    # Sort by bucket weight desc, then alphabetical for stability
    ranked = sorted(agg.values(), key=lambda x: (-x["raw_weight"], x["ts_code"]))
    portfolio = ranked[:PORTFOLIO_MAX_SIZE]

    # Normalize weights to sum to 1.0
    total = sum(p["raw_weight"] for p in portfolio)
    for p in portfolio:
        p["weight"] = p["raw_weight"] / total if total > 0 else 0

    bucket_counts = {"core": 0, "satellite": 0, "hedge": 0}
    for p in portfolio:
        bucket_counts[p["bucket"]] = bucket_counts.get(p["bucket"], 0) + 1

    return {
        "portfolio": portfolio,
        "size": len(portfolio),
        "bucket_counts": bucket_counts,
        "overall_score": judge_result.get("overall_score"),
        "final_recommendation": judge_result.get("final_recommendation"),
        "adjustments": judge_result.get("adjustments", []),
    }
