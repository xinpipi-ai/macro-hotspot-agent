"""Config: macro hotspot strategy."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Strategy params (from Huatai report)
PORTFOLIO_MAX_SIZE = 20              # Macro caps at 20 stocks
STOCKS_PER_SECTOR_MIN = 3
STOCKS_PER_SECTOR_MAX = 6
BENCHMARK = "000300.SH"              # CSI 300
STOCKS_PER_INDUSTRY_IN_POOL = 8      # Top N by market cap per industry for candidate pool

# Default reasoning paths (from report: "利率敏感成长"、"高股息防御"、"出口链景气")
DEFAULT_REASONING_PATHS = [
    "利率敏感成长",
    "高股息防御",
    "出口链景气",
]
