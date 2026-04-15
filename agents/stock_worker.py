"""Stock Worker: pick concrete A-share stocks from the sector-mapped pool."""
from data.deepseek_client import chat_json
from data import tushare_client
from config import STOCKS_PER_INDUSTRY_IN_POOL, STOCKS_PER_SECTOR_MIN, STOCKS_PER_SECTOR_MAX

SYSTEM = f"""你是 A 股个股分析师。给定宏观事件、受益行业清单和各行业的候选股票池（已按市值排序），请挑选代表性标的构建组合。

输出严格的 JSON 对象：
{{
  "picks": [
    {{
      "ts_code": "股票代码（必须来自候选池）",
      "name": "股票简称",
      "sector": "所属申万行业",
      "bucket": "core / satellite / hedge",
      "rationale": "为何入选（1-2句，结合事件传导逻辑）"
    }}
  ]
}}

规则：
- core：受益逻辑最直接、龙头地位明确的标的
- satellite：弹性标的或细分领域优势公司
- hedge：可作为对冲工具（如：事件利多成长时，可配少量高股息防御标的）
- 每个受益行业选 {STOCKS_PER_SECTOR_MIN}-{STOCKS_PER_SECTOR_MAX} 只
- 必须从候选池中挑，不要编造池外的股票
- 总数不超过 20 只
"""


def analyze(event_description: str, plan_result: dict, sector_result: dict) -> dict:
    """Pick stocks using sector_worker's output as guide."""
    beneficiaries = [s["name"] for s in sector_result.get("beneficiary_sectors", [])]
    if not beneficiaries:
        return {"picks": []}

    pool_df = tushare_client.top_stocks_per_industry(
        beneficiaries, top_n=STOCKS_PER_INDUSTRY_IN_POOL
    )
    if pool_df.empty:
        return {"picks": [], "warning": "No candidates from Tushare for these industries"}

    # Format pool grouped by industry
    pool_by_industry = {}
    for _, r in pool_df.iterrows():
        ind = r["l1_name"]
        pool_by_industry.setdefault(ind, []).append(
            f"{r['ts_code']} {r['name']}（市值{r['total_mv'] / 10000:.0f}亿）"
        )

    pool_str = ""
    for ind, stocks in pool_by_industry.items():
        pool_str += f"\n【{ind}】\n" + "\n".join(f"  - {s}" for s in stocks)

    sector_str = "\n".join(
        f"- {s['name']}（{s['magnitude']}）: {s['rationale']}"
        for s in sector_result.get("beneficiary_sectors", [])
    )

    user = f"""宏观事件：{event_description}

事件假设：{plan_result.get('core_hypotheses')}

受益行业（来自 sector_worker）：
{sector_str}

候选股票池（按市值 top {STOCKS_PER_INDUSTRY_IN_POOL}，来自 Tushare 申万分类）：
{pool_str}

请从候选池中挑选股票构建组合。"""
    return chat_json(SYSTEM, user)
