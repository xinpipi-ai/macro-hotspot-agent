"""Tushare wrapper focused on industry/macro data for hotspot strategy."""
import tushare as ts
import pandas as pd
from functools import lru_cache
from config import TUSHARE_TOKEN

ts.set_token(TUSHARE_TOKEN)
_pro = ts.pro_api()


@lru_cache(maxsize=1)
def stock_basic() -> pd.DataFrame:
    """Full A-share metadata."""
    return _pro.stock_basic(
        exchange="",
        list_status="L",
        fields="ts_code,name,area,industry,market,list_date"
    )


@lru_cache(maxsize=1)
def sw_l1_industries() -> pd.DataFrame:
    """申万一级行业分类（31个）. Columns: index_code, industry_name, level, src"""
    return _pro.index_classify(level="L1", src="SW2021")


def sw_industry_stocks(sw_index_code: str) -> pd.DataFrame:
    """Get stocks in a SW industry by its index code."""
    return _pro.index_member_all(l1_code=sw_index_code, is_new="Y")


@lru_cache(maxsize=1)
def sw_stock_mapping() -> pd.DataFrame:
    """Full mapping of stocks to SW L1 industries (one row per stock)."""
    df = _pro.index_member_all(is_new="Y")
    cols = [c for c in df.columns if c in ("ts_code", "name", "l1_code", "l1_name")]
    return df[cols].drop_duplicates(subset=["ts_code"])


def daily_prices(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    return _pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)


def index_daily(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    return _pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)


def daily_basic(trade_date: str) -> pd.DataFrame:
    """Daily basic indicators incl. market cap (for ranking top N per industry)."""
    return _pro.daily_basic(
        trade_date=trade_date,
        fields="ts_code,total_mv,circ_mv,pe,pb,turnover_rate"
    )


def top_stocks_per_industry(
    industry_names: list[str],
    top_n: int = 8,
    snapshot_date: str = "20260410",
) -> pd.DataFrame:
    """For given SW L1 industries, return top N stocks by market cap.

    Returns: ts_code, name, l1_name, total_mv (in 10k yuan)
    """
    mapping = sw_stock_mapping()
    if not industry_names:
        return pd.DataFrame(columns=["ts_code", "name", "l1_name", "total_mv"])

    subset = mapping[mapping["l1_name"].isin(industry_names)].copy()
    if subset.empty:
        return subset

    mv = daily_basic(snapshot_date)
    merged = subset.merge(mv[["ts_code", "total_mv"]], on="ts_code", how="left")

    # Rank within each industry
    merged = merged.sort_values(["l1_name", "total_mv"], ascending=[True, False])
    return merged.groupby("l1_name").head(top_n).reset_index(drop=True)
