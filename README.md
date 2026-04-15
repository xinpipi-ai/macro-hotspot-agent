# Macro Hotspot Agent

A runnable multi-agent stock selection project for macro-event investing.

This project recreates the "macro hotspot stock selection" side of the Huatai research note 《大模型概念与宏观热点选股》. Instead of starting from a concept label, it starts from a macro event description such as `美联储连续降息50bp` or `国内新一轮化债万亿`, then turns that event into a weighted stock portfolio with rationale and backtest output.

## What It Does

- Takes a macro event in natural language
- Maps the event to likely beneficiary or defensive sectors
- Runs specialized agents for macro interpretation, stock picking, and risk falsification
- Lets a judge reconcile disagreements
- Builds a weighted `core / satellite / hedge` portfolio
- Runs a weighted backtest against CSI 300

## Why This Project Is Interesting

- It models an event-driven workflow instead of a static theme screener.
- The hedge bucket makes it more realistic than a long-only idea list.
- The agent roles are clearly separated, so the reasoning is easier to audit.
- It is designed as a local research prototype, not just a notebook experiment.

## Pipeline

```text
planner
  -> sector_worker
  -> macro_worker   (parallel)
  -> stock_worker   (parallel)
  -> risk_worker    (parallel)
  -> evidence_judge
  -> portfolio_builder
```

## Compared With Concept Stock Selection

| Dimension | Concept Stock Agent | Macro Hotspot Agent |
|---|---|---|
| Input | Concept name such as `AI算力` | Event description such as `美联储降息50bp` |
| Candidate pool | Tushare concept constituents | Beneficiary SW level-1 industries and top market-cap names |
| Portfolio buckets | `core / satellite` | `core / satellite / hedge` |
| Weighting | Equal-weight backtest | Bucket-weighted backtest |
| Focus | Theme decomposition | Event transmission path and cross-checking |

## Stack

- `Python`
- `Tushare` for SW industry classification and daily market-cap data
- `DeepSeek` for agent reasoning
- Local JSON outputs for inspection and reuse

## Repository Structure

```text
agents/      planner, sector mapper, macro reader, stock picker, risk worker, judge
data/        Tushare + model clients
run.py       CLI entry point
graph.py     pipeline orchestration
backtest.py  weighted portfolio backtest
config.py    model, token, and strategy parameters
```

## Setup

```bash
cd "/Users/xinwei/Desktop/my show/macro_hotspot_agent"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a local `.env` file:

```bash
TUSHARE_TOKEN=your_tushare_token
DEEPSEEK_API_KEY=your_deepseek_key
```

## Usage

```bash
# Activate the environment
source .venv/bin/activate

# Run different macro events
python run.py "美联储连续降息50bp"
python run.py "国内新一轮化债万亿"
python run.py "中东地缘冲突升级，油价飙升"
python run.py "碳中和政策加码"

# Customize the backtest window
python run.py "AI产业链景气度加速" --backtest-start 20240101 --backtest-end 20260414

# Skip backtest and only build the portfolio
python run.py "xxx事件" --skip-backtest
```

## Output

Each run writes a JSON artifact under `outputs/` containing:

- Event interpretation
- Selected reasoning paths
- Sector mapping
- Stock recommendations
- Risk checks and judge adjustments
- Final weighted portfolio

The CLI also prints the final basket, bucket weights, and backtest summary.

## Key Parameters

Main knobs live in `config.py`:

- `PORTFOLIO_MAX_SIZE = 20`
- `STOCKS_PER_SECTOR_MIN` / `STOCKS_PER_SECTOR_MAX`
- `STOCKS_PER_INDUSTRY_IN_POOL = 8`
- `DEFAULT_REASONING_PATHS`
- `BENCHMARK = "000300.SH"`

## Design Notes

- Candidate stocks are constrained by sector and market cap to keep the search space practical.
- The `risk_worker` is intentionally separate so the system can generate counterarguments.
- The final portfolio uses bucket weighting to reflect different confidence levels.

## Roadmap Ideas

- Add richer event templates and sector-mapping rules
- Support benchmark comparison beyond CSI 300
- Export judge decisions and risk notes as standalone artifacts
- Add batch evaluation for multiple macro scenarios
