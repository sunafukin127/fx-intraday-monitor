
import os
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ["TWELVE_DATA_API_KEY"]
DATA_FILE = Path("data/fx_prices.json")
PAIRS = ["USD/JPY", "EUR/USD"]

def fetch_price(pair):
    params = urllib.parse.urlencode({
        "symbol": pair,
        "apikey": API_KEY
    })
    url = "https://api.twelvedata.com/price?" + params

    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.load(response)

    if "price" not in data:
        raise RuntimeError(
            f"API error for {pair}: {data.get('message', 'Unknown error')}"
        )

    return float(data["price"])

def main():
    if DATA_FILE.exists():
        history = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    else:
        history = []

    timestamp = datetime.now(timezone.utc).isoformat()

    prices = {}
    for pair in PAIRS:
        prices[pair] = fetch_price(pair)

    history.append({
        "timestamp": timestamp,
        "prices": prices
    })

    # Keep approximately 7 days of observations
    cutoff = datetime.now(timezone.utc).timestamp() - 7 * 86400
    history = [
        row for row in history
        if datetime.fromisoformat(
            row["timestamp"].replace("Z", "+00:00")
        ).timestamp() >= cutoff
    ]

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(history, indent=2),
        encoding="utf-8"
    )

    print("Updated:", timestamp, prices)

if __name__ == "__main__":
    main()
