import yfinance as yf
import pandas as pd
from datetime import date
import time
import numpy as np

# ---------- Parameters ----------
ticker = "^SPX"
strike_min = 6000
strike_max = 7000
strike_step = 5  # every 5 points
delay = 10       # seconds to avoid rate limits
num_expirations = 500  # fetch only next 500 expirations

# ---------- Initialize ----------
spx = yf.Ticker(ticker)
expirations = spx.options[:num_expirations]  # next 5 expirations
print("Fetching expirations:", expirations)

all_options = []

# ---------- Generate full strike grid ----------
strike_grid = np.arange(strike_min, strike_max + strike_step, strike_step)

# ---------- Fetch each expiration ----------
for expiry in expirations:
    print(f"\nFetching expiration: {expiry}")
    success = False
    while not success:
        try:
            opt_chain = spx.option_chain(expiry)

            # Keep only calls
            calls = opt_chain.calls[["strike", "bid", "ask"]].copy()
            calls = calls[(calls["strike"] >= strike_min) & (calls["strike"] <= strike_max)]

            # Compute midPrice
            calls["midPrice"] = (calls["bid"] + calls["ask"]) / 2

            # Merge with full strike grid to include missing strikes
            full_calls = pd.DataFrame({"strike": strike_grid})
            full_calls = full_calls.merge(calls[["strike", "midPrice"]], on="strike", how="left")

            # Interpolate only missing midPrice values
            full_calls["midPrice"] = full_calls["midPrice"].interpolate(method="linear")

            # Add required fields
            full_calls["optionType"] = "call"
            full_calls["expirationDate"] = expiry

            all_options.append(full_calls)

            success = True
            print(f"Processed {len(full_calls)} strikes for {expiry}. Waiting {delay}s before next expiration...")
            time.sleep(delay)

        except Exception as e:
            print(f"Error or rate limit encountered: {e}. Retrying in 20s...")
            time.sleep(20)

# ---------- Merge and save ----------
df = pd.concat(all_options, ignore_index=True)
df["dataDate"] = str(date.today())
df.to_csv("SPX_options_next5_6000_7000_mid_actual_interpolated.csv", index=False)

print("\nAll calls for next 5 expirations saved to SPX_options_next5_6000_7000_mid_actual_interpolated.csv")
