import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import griddata

# ---------- Configuration ----------
CSV_FILE_PATH = "SPX_options_next5_6000_7000_mid_actual_interpolated.csv"
NUM_EXPIRATIONS_TO_ANALYZE = 5

# ---------- Load Data ----------
print(f"Loading data from {CSV_FILE_PATH}...")
df = pd.read_csv(CSV_FILE_PATH)

# Convert 'expirationDate' to datetime
df['expirationDate'] = pd.to_datetime(df['expirationDate'])

# Filter only calls
calls_df = df[df['optionType'] == 'call'].copy()

# Get unique expirations and select the nearest ones
unique_expirations = np.sort(calls_df['expirationDate'].unique())[:NUM_EXPIRATIONS_TO_ANALYZE]

# Convert to pandas Timestamps to avoid numpy.datetime64 issues
unique_expirations_ts = [pd.Timestamp(d) for d in unique_expirations]

calls_df = calls_df[calls_df['expirationDate'].isin(unique_expirations_ts)]

print(f"Analyzing expirations: {[d.strftime('%Y-%m-%d') for d in unique_expirations_ts]}")

# ---------- Prepare data for PDF ----------
base_date = unique_expirations_ts[0]
calls_df['expiration_numeric'] = (calls_df['expirationDate'] - base_date).dt.days

all_strikes = calls_df['strike'].values
all_exp_numeric = calls_df['expiration_numeric'].values
all_midprices = calls_df['midPrice'].values

# ---------- Compute PDF using Breeden-Litzenberger approximation ----------
def compute_pdf(strikes, prices):
    if len(strikes) < 3:
        return np.array([]), np.array([])
    # sort by strike
    sort_idx = np.argsort(strikes)
    strikes_sorted = strikes[sort_idx]
    prices_sorted = prices[sort_idx]

    # second derivative
    first_der = np.gradient(prices_sorted, strikes_sorted)
    second_der = np.gradient(first_der, strikes_sorted)
    pdf = np.maximum(0, second_der)
    return strikes_sorted, pdf

pdf_data = []
for exp in unique_expirations_ts:
    group = calls_df[calls_df['expirationDate'] == exp]
    strikes, pdf = compute_pdf(group['strike'].values, group['midPrice'].values)
    if len(strikes) > 0:
        pdf_data.append(pd.DataFrame({
            'strike': strikes,
            'expiration_numeric': (exp - base_date).days,
            'pdf': pdf
        }))

pdf_df = pd.concat(pdf_data, ignore_index=True)

# ---------- Interpolate for smooth surface ----------
strike_grid = np.linspace(pdf_df['strike'].min(), pdf_df['strike'].max(), 100)
exp_grid = np.linspace(pdf_df['expiration_numeric'].min(), pdf_df['expiration_numeric'].max(), 50)
grid_strike, grid_exp = np.meshgrid(strike_grid, exp_grid)

interpolated_pdf = griddata(
    (pdf_df['strike'], pdf_df['expiration_numeric']),
    pdf_df['pdf'],
    (grid_strike, grid_exp),
    method='linear'
)

interpolated_pdf = np.nan_to_num(interpolated_pdf, nan=0.0)

# ---------- Plot 3D PDF Surface ----------
fig = go.Figure(data=[
    go.Surface(
        z=interpolated_pdf,
        x=grid_strike,
        y=grid_exp,
        colorscale='Viridis',
        colorbar=dict(title='PDF Magnitude'),
        hovertemplate=(
            '<b>Strike:</b> %{x:.2f}<br>'
            '<b>Expiration:</b> %{customdata}<br>'
            '<b>PDF:</b> %{z:.4f}<extra></extra>'
        ),
        customdata=np.array([
            [(base_date + pd.Timedelta(days=int(e))).strftime('%Y-%m-%d') for e in row]
            for row in grid_exp
        ])
    )
])

fig.update_layout(
    title='3D Risk-Neutral PDF Surface for SPX Calls',
    scene=dict(
        xaxis_title='Strike Price',
        yaxis_title='Expiration Date',
        zaxis_title='Risk-Neutral PDF',
        xaxis=dict(autorange=True),
        yaxis=dict(
            tickmode='array',
            tickvals=[(d - base_date).days for d in unique_expirations_ts],
            ticktext=[d.strftime('%Y-%m-%d') for d in unique_expirations_ts],
            autorange=True
        ),
        zaxis=dict(autorange=True),
        aspectratio=dict(x=1.5, y=1.5, z=0.7),
        aspectmode='manual'
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    hovermode='closest'
)

fig.show()
print("\nInteractive 3D PDF surface generated successfully.")
