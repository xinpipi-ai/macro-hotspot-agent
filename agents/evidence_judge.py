"""Evidence Judge: arbitrate 4 workers' outputs."""
from data.deepseek_client import chat_json

SYSTEM = """你是一名投研组合仲裁员。4 个 agent 独立分析了同一宏观事件：sector（行业映射）、macro（宏观解读）、stock（个股推荐）、risk（风险反证）。请综合评审。

输出严格的 JSON 对象：
{
  "overall_score": 0-10 的整数，表示逻辑整体可信度,
  "consistency_check": "4 个 worker 结论一致性描述（如：sector 和 macro 一致看好成长，但 risk 提示降息预期被证伪的尾部风险）",
  "conflicts": ["具体冲突点"],
  "adjustments": [
    "建议对 stock 组合的调整（如：'降低 core 仓位，增加 hedge 比例因为 risk_worker 提示中等概率下行'）"
  ],
  "final_recommendation": "进入组合构建 / 需要补充分析 / 放弃本次事件"
}
"""


def judge(event_description: str, macro: dict, sector: dict, stock: dict, risk: dict) -> dict:
    user = f"""宏观事件：{event_description}

【Macro Worker】
- 方向：{macro.get('impact_direction')}（强度 {macro.get('magnitude_score')}/10）
- 传导链：{macro.get('transmission_chain')}
- 风险前提：{macro.get('risks_to_this_view')}

【Sector Worker】
- 受益行业：{[s['name'] for s in sector.get('beneficiary_sectors', [])]}
- 受损行业：{[s['name'] for s in sector.get('impacted_sectors', [])]}

【Stock Worker】
- 推荐股票数：{len(stock.get('picks', []))}
- 分桶：{dict((b, sum(1 for p in stock.get('picks', []) if p.get('bucket') == b)) for b in ['core', 'satellite', 'hedge'])}

【Risk Worker】
- 失效条件：{risk.get('failure_conditions')}
- 下行情景：{risk.get('drawdown_scenarios')}
- 对冲建议：{risk.get('hedge_suggestions')}

请综合仲裁。"""
    return chat_json(SYSTEM, user)
