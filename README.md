# Macro Hotspot Agent

基于华泰金工研报《大模型概念与宏观热点选股》的**宏观热点选股**多智能体复现。

## 架构

```
        planner (识别事件 + 选推理路径)
            ↓
        sector_worker (映射申万L1行业)
            ↓
    ┌──── 并行 ────┐
macro_worker  stock_worker  risk_worker
(宏观解读)   (个股筛选)      (证伪/对冲)
    └────┬────────┘
         ↓
    evidence_judge (仲裁)
         ↓
    portfolio_builder (权重: core=3/satellite=2/hedge=1)
```

## 与概念选股的区别

| | 概念选股 | 宏观热点选股 |
|---|---|---|
| 输入 | 概念名（如 "AI算力"） | 事件描述（如 "美联储降息50bp"） |
| 候选池 | Tushare 概念板块成分股 | 申万L1受益行业 × 市值top N |
| 分桶 | core / satellite | core / satellite / **hedge** |
| 组合上限 | 30 只 | 20 只 |
| 权重 | 等权 | 按 bucket 加权（core=3/sat=2/hedge=1） |
| 架构 | 5 agent 顺序 | 4 agent 并行 + 仲裁 |

## 安装

```bash
cd "/Users/xinwei/Desktop/my show/macro_hotspot_agent"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用

```bash
# 激活环境
source .venv/bin/activate

# 跑不同宏观事件
python run.py "美联储连续降息50bp"
python run.py "国内新一轮化债万亿"
python run.py "中东地缘冲突升级，油价飙升"
python run.py "碳中和政策加码"

# 自定义回测区间
python run.py "AI产业链景气度加速" --backtest-start 20240101 --backtest-end 20260414

# 跳过回测
python run.py "xxx事件" --skip-backtest
```

## 数据源

- **Tushare** 申万一级行业分类（31 个）+ 日频市值（daily_basic）
- **DeepSeek** 作为各 agent 的推理引擎

## 关键参数（config.py）

- `PORTFOLIO_MAX_SIZE = 20` - 组合容量
- `STOCKS_PER_INDUSTRY_IN_POOL = 8` - 每行业候选池大小
- `DEFAULT_REASONING_PATHS` - 默认推理路径（利率敏感成长/高股息防御/出口链景气）
- `BENCHMARK = "000300.SH"` - 沪深300
