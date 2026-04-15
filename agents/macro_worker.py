"""Macro Worker: deep macro analysis (independent perspective)."""
from data.deepseek_client import chat_json

SYSTEM = """你是一名资深宏观分析师。给定宏观事件，请独立给出深入的宏观解读。

输出严格的 JSON 对象：
{
  "impact_direction": "利多/利空/中性",
  "magnitude_score": 0-10 的整数,
  "transmission_chain": "事件如何传导到资产价格（1段话，要具体，包含因果链）",
  "historical_analogs": ["历史上类似的事件（如：'2019年美联储降息周期'）"],
  "key_indicators_to_watch": ["需要持续跟踪的3-5个关键指标"],
  "style_preference": "成长/价值/防御/周期 中最受益的风格",
  "risks_to_this_view": ["这个判断可能出错的2-3个前提条件"]
}
"""


def analyze(event_description: str, plan_result: dict) -> dict:
    user = f"""宏观事件：{event_description}

研究计划摘要：
- 事件分类：{plan_result.get('event_category')}
- 时间跨度：{plan_result.get('time_horizon')}
- 核心假设：{plan_result.get('core_hypotheses')}

请独立给出宏观解读。"""
    return chat_json(SYSTEM, user)
