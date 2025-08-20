import yfinance as yf
import pandas as pd
from datetime import date
import time
import numpy as np

# ---------- Parameters ----------
ticker = "^SPX"
strike_min = 6000
strike_max = 7000
strike_step = 5      # every 5 points
delay = 3           # seconds to avoid rate limits
num_expirations = 5  # fetch only next 5 expirations

# ---------- Initialize ----------
spx = yf.Ticker(ticker)
expirations = spx.options[:num_expirations]
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

            # Compute midPrice safely
            calls["midPrice"] = calls[["bid", "ask"]].mean(axis=1)

            # Merge with full strike grid
            full_calls = pd.DataFrame({"strike": strike_grid})
            full_calls = full_calls.merge(calls[["strike", "midPrice"]], on="strike", how="left")

            # Interpolate internal NaNs
            full_calls["midPrice"] = full_calls["midPrice"].interpolate(method="linear")

            # Extrapolate missing values at edges
            if full_calls["midPrice"].isna().any():
                # Fill leading NaNs
                first_valid = full_calls["midPrice"].first_valid_index()
                full_calls.loc[:first_valid-1, "midPrice"] = full_calls.loc[first_valid, "midPrice"] - \
                    (full_calls.loc[first_valid+1, "midPrice"] - full_calls.loc[first_valid, "midPrice"])
                # Fill trailing NaNs
                last_valid = full_calls["midPrice"].last_valid_index()
                full_calls.loc[last_valid+1:, "midPrice"] = full_calls.loc[last_valid, "midPrice"] + \
                    (full_calls.loc[last_valid, "midPrice"] - full_calls.loc[last_valid-1, "midPrice"])

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
