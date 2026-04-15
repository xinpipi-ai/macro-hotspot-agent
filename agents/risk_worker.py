"""Risk Worker: independent devil's-advocate analysis."""
from data.deepseek_client import chat_json

SYSTEM = """你是一名风险管理官，立场是「证伪」——专门挑这个投资逻辑可能出错的地方。

输出严格的 JSON 对象：
{
  "failure_conditions": [
    "投资逻辑被证伪的具体触发条件（如：'CPI重回3%以上导致货币政策转向'）"
  ],
  "drawdown_scenarios": [
    {
      "scenario": "具体下跌情景",
      "estimated_drawdown": "-X%",
      "probability": "high/medium/low"
    }
  ],
  "contrarian_signals": ["应该警惕的反向信号"],
  "hedge_suggestions": ["建议配置的对冲工具或防御资产（如：黄金、高股息、国债）"]
}

要求：不要给面面俱到的套话，要具体、可量化、可监控。
"""


def analyze(event_description: str, plan_result: dict) -> dict:
    user = f"""宏观事件：{event_description}

主流判断：{plan_result.get('core_hypotheses')}

请作为反方，列出这个逻辑可能被证伪的触发条件和回撤情景。"""
    return chat_json(SYSTEM, user)
