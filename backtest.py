"""Weighted backtest vs CSI300."""
import pandas as pd
import numpy as np
from data import tushare_client
from config import BENCHMARK


def backtest_weighted(
    picks: list[dict],  # each has ts_code and weight
    start_date: str,
    end_date: str,
) -> dict:
    """Buy & hold weighted portfolio vs CSI300."""
    if not picks:
        raise ValueError("Empty portfolio")

    # Fetch prices
    frames = []
    valid_picks = []
    missing = []
    for p in picks:
        code = p["ts_code"]
        df = tushare_client.daily_prices(code, start_date, end_date)
        if df.empty:
            missing.append(code)
            continue
        df = df[["trade_date", "close"]].rename(columns={"close": code})
        frames.append(df.set_index("trade_date"))
        valid_picks.append(p)

    if not frames:
        raise RuntimeError("No price data")

    prices = pd.concat(frames, axis=1).sort_index()

    # Normalize each stock using its own first valid price (handles late listings)
    first_valid = prices.apply(lambda col: col.dropna().iloc[0] if col.dropna().size else None)
    norm = prices.div(first_valid, axis=1)

    # Drop stocks with no valid price data at all
    norm = norm.dropna(axis=1, how="all")

    # Renormalize weights over stocks that actually have data
    available_codes = list(norm.columns)
    valid_picks = [p for p in valid_picks if p["ts_code"] in available_codes]
    total_w = sum(p["weight"] for p in valid_picks)
    weights = pd.Series({p["ts_code"]: p["weight"] / total_w for p in valid_picks})

    # Portfolio NAV: per-date weighted average over AVAILABLE stocks (renormalize weights per date)
    # This prevents late-listing NaNs from poisoning the whole series.
    mask = norm.notna().astype(float)
    weighted_sum = (norm.fillna(0) * weights).sum(axis=1)
    active_weight = (mask * weights).sum(axis=1)
    portfolio_nav = (weighted_sum / active_weight).dropna()

    # Benchmark
    bench = tushare_client.index_daily(BENCHMARK, start_date, end_date)
    bench = bench.sort_values("trade_date").set_index("trade_date")["close"]
    bench_nav = bench / bench.iloc[0]

    common = portfolio_nav.index.intersection(bench_nav.index)
    portfolio_nav = portfolio_nav.loc[common]
    bench_nav = bench_nav.loc[common]

    p_returns = portfolio_nav.pct_change(fill_method=None).dropna()
    total_ret = portfolio_nav.iloc[-1] - 1
    bench_ret = bench_nav.iloc[-1] - 1
    ann_vol = p_returns.std() * np.sqrt(252)
    sharpe = (p_returns.mean() * 252) / ann_vol if ann_vol > 0 else 0
    cummax = portfolio_nav.cummax()
    max_dd = ((portfolio_nav - cummax) / cummax).min()

    return {
        "portfolio_nav": portfolio_nav,
        "benchmark_nav": bench_nav,
        "metrics": {
            "total_return": float(total_ret),
            "benchmark_return": float(bench_ret),
            "excess_return": float(total_ret - bench_ret),
            "annualized_vol": float(ann_vol),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
            "n_stocks": len(valid_picks),
            "missing_data": missing,
        },
    }


def print_backtest_report(result: dict):
    m = result["metrics"]
    print("\n" + "=" * 50)
    print("📈 Backtest Report (weighted: core=3, satellite=2, hedge=1)")
    print("=" * 50)
    print(f"Stocks in backtest:   {m['n_stocks']}")
    if m["missing_data"]:
        print(f"Missing data:         {m['missing_data']}")
    print(f"Portfolio return:     {m['total_return']:+.2%}")
    print(f"Benchmark (CSI300):   {m['benchmark_return']:+.2%}")
    print(f"Excess return:        {m['excess_return']:+.2%}")
    print(f"Annualized vol:       {m['annualized_vol']:.2%}")
    print(f"Sharpe ratio:         {m['sharpe']:.2f}")
    print(f"Max drawdown:         {m['max_drawdown']:.2%}")
    print("=" * 50)
