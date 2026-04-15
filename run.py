"""Entry point.

Usage:
    python run.py "美联储连续降息50bp"
    python run.py "国内新一轮化债" --backtest-start 20250101 --backtest-end 20260414
"""
import argparse
import sys

from graph import run_macro_pipeline
from backtest import backtest_weighted, print_backtest_report


def main():
    parser = argparse.ArgumentParser(description="Macro hotspot stock selection via multi-agent LLM pipeline")
    parser.add_argument("event", help="Macro event description (natural language)")
    parser.add_argument("--skip-backtest", action="store_true")
    parser.add_argument("--backtest-start", default="20250101")
    parser.add_argument("--backtest-end", default="20260414")
    args = parser.parse_args()

    print(f"\n🚀 Running macro hotspot pipeline\n事件: {args.event}\n" + "=" * 50)
    state = run_macro_pipeline(args.event)

    print("\n📋 Final Portfolio:")
    for i, p in enumerate(state["portfolio"]["portfolio"], 1):
        print(f"  {i:2d}. {p['ts_code']} {p['name']:10s} [{p['bucket']:9s}] w={p['weight']:.2%} {p.get('sector', '')}")
        print(f"       {p['rationale']}")

    if state["judge"].get("adjustments"):
        print("\n⚙️  Judge adjustments:")
        for a in state["judge"]["adjustments"]:
            print(f"  - {a}")

    if args.skip_backtest:
        return

    print("\n🏁 Running backtest...")
    try:
        result = backtest_weighted(
            state["portfolio"]["portfolio"],
            args.backtest_start,
            args.backtest_end,
        )
        print_backtest_report(result)
    except Exception as e:
        print(f"⚠️  Backtest failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
