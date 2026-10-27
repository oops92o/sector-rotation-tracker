import json
from datetime import datetime, timezone
import yfinance as yf

SECTORS = {
    "XLK": "기술", "XLE": "에너지", "XLF": "금융", "XLV": "헬스케어",
    "XLI": "산업재", "XLY": "경기소비재", "XLP": "필수소비재",
    "XLU": "유틸리티", "XLB": "소재", "XLRE": "부동산", "XLC": "통신",
}
PERIODS = {"1M": 21, "3M": 63}

tickers = list(SECTORS) + ["SPY"]
data = yf.download(tickers, period="6mo", auto_adjust=True, progress=False)["Close"]

def ret(series, days):
    s = series.dropna()
    return (s.iloc[-1] / s.iloc[-1 - days] - 1) * 100

spy = {p: ret(data["SPY"], d) for p, d in PERIODS.items()}

rows = []
for t, name in SECTORS.items():
    row = {"ticker": t, "name": name}
    for p, d in PERIODS.items():
        r = ret(data[t], d)
        row[p + "_abs"] = round(r, 2)      # 섹터 자체 수익률(%)
        row[p] = round(r - spy[p], 2)      # SPY 대비 상대 성과(%p)
    rows.append(row)

rows.sort(key=lambda r: r["1M"], reverse=True)

out = {
    "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "asof": str(data.index[-1].date()),
    "spy": {p: round(v, 2) for p, v in spy.items()},
    "sectors": rows,
}
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
