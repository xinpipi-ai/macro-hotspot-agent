"""Sector Worker: map macro event to A-share SW L1 industries."""
from data.deepseek_client import chat_json
from data import tushare_client


def _build_sw_list() -> str:
    df = tushare_client.sw_l1_industries()
    return "\n".join(f"- {r['industry_name']}" for _, r in df.iterrows())


SYSTEM_TMPL = """你是 A 股行业分析师。给定宏观事件和研究计划，请将事件映射到申万一级行业（共31个）的受益/受损/中性分类。

申万一级行业清单：
{sw_list}

输出严格的 JSON 对象：
{{
  "beneficiary_sectors": [
    {{"name": "行业名（必须是上面列表中的）", "magnitude": "high/medium/low", "rationale": "受益逻辑（1-2句）"}}
  ],
  "impacted_sectors": [
    {{"name": "行业名", "magnitude": "high/medium/low", "rationale": "受损逻辑"}}
  ],
  "neutral_sectors": ["行业名1", "行业名2"]
}}

要求：
1. 所有行业名必须严格来自上面的申万清单，不要自造
2. beneficiary_sectors 控制在 3-6 个，聚焦主线
3. 每个行业给出具体逻辑，不要套话
"""


def analyze(event_description: str, plan_result: dict) -> dict:
    system = SYSTEM_TMPL.format(sw_list=_build_sw_list())
    user = f"""宏观事件：{event_description}

研究计划摘要：
- 事件分类：{plan_result.get('event_category')}
- 时间跨度：{plan_result.get('time_horizon')}
- 推理路径：{plan_result.get('selected_reasoning_paths')}
- 核心假设：{plan_result.get('core_hypotheses')}

请映射到申万一级行业。"""
    return chat_json(system, user)
