"""Planner: interpret the macro event and pick reasoning paths."""
from data.deepseek_client import chat_json
from config import DEFAULT_REASONING_PATHS

SYSTEM = f"""你是一名宏观策略分析师。给定一个宏观事件（政策/数据/地缘/市场现象），请生成结构化研究计划。

输出严格的 JSON 对象：
{{
  "event_summary": "对事件的一句话提炼（不超过50字）",
  "event_category": "政策/数据/地缘/市场/产业 中的一个",
  "time_horizon": "短期/中期/长期（1-3个月/3-12个月/1年以上）",
  "selected_reasoning_paths": ["从以下默认路径中选择2-3个最相关的：{', '.join(DEFAULT_REASONING_PATHS)}，或补充其他更契合的逻辑路径"],
  "core_hypotheses": ["2-3条待验证的关键假设（如：'降息利好成长风格'）"]
}}
"""


def plan(event_description: str) -> dict:
    user = f"宏观事件：{event_description}\n\n请生成研究计划。"
    return chat_json(SYSTEM, user)
