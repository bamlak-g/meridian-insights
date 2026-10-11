import os
import yfinance as yf
import pandas as pd

HOLDINGS = {"AAPL": 50, "MSFT": 30, "JNJ": 40, "JPM": 35, "XOM": 45}
BENCHMARK = "SPY"
CACHE_DIR = "data/cache"

os.makedirs("data/yf_cache", exist_ok=True)
yf.set_tz_cache_location("data/yf_cache")


def fetch_prices(ticker):
    # download one year of daily prices
    hist = yf.Ticker(ticker).history(period="1y")
    if hist.empty:
        raise ValueError(f"No data found for {ticker}")

    prices = hist["Close"]
    # remove timezone so dates save and load from csv correctly
    prices.index = prices.index.tz_localize(None)
    return prices


def save_prices(prices, ticker):
    os.makedirs(CACHE_DIR, exist_ok=True)
    prices.to_csv(f"{CACHE_DIR}/{ticker}.csv")


def load_prices(ticker):
    path = f"{CACHE_DIR}/{ticker}.csv"
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    return df["Close"]


def get_prices(tickers):
    data = {}
    for ticker in tickers:
        prices = load_prices(ticker)
        if prices is None:
            # not cached yet, so download it and save it
            prices = fetch_prices(ticker)
            save_prices(prices, ticker)
        data[ticker] = prices
    return pd.DataFrame(data).dropna()


if __name__ == "__main__":
    prices = get_prices(list(HOLDINGS) + [BENCHMARK])
    print(prices.tail())
    print()

    for ticker, shares in HOLDINGS.items():
        latest = prices[ticker].iloc[-1]
        value = latest * shares
        print(f"{ticker}: {shares} shares x ${latest:.2f} = ${value:,.2f}")